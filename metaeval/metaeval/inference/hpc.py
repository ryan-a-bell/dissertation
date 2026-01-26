"""HPC cluster execution via SLURM."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from metaeval.inference.base import ExecutorBase
from metaeval.inference.session import SSHSession
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SLURMConfig:
    """Configuration for SLURM job."""

    partition: str = "gpu"
    nodes: int = 1
    gpus_per_node: int = 1
    cpus_per_task: int = 8
    memory_gb: int = 64
    time_limit: str = "4:00:00"
    account: str | None = None
    job_name: str = "metaeval"
    output_pattern: str = "slurm-%j.out"
    error_pattern: str = "slurm-%j.err"
    modules: list[str] = field(default_factory=lambda: ["cuda", "python"])
    extra_directives: dict[str, str] = field(default_factory=dict)


SLURM_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --gpus-per-node={gpus_per_node}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem={memory_gb}G
#SBATCH --time={time_limit}
#SBATCH --output={output_pattern}
#SBATCH --error={error_pattern}
{account_line}
{extra_directives}

# Load modules
{module_loads}

# Run command
{command}
"""


class HPCExecutor(ExecutorBase):
    """Execute models on HPC clusters via SLURM."""

    def __init__(
        self,
        model: str,
        host: str,
        username: str,
        key_path: Path | None = None,
        slurm_config: SLURMConfig | None = None,
        work_dir: str = "~/metaeval",
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 14400,  # 4 hours default for HPC jobs
    ):
        """
        Initialize HPC executor.

        Args:
            model: Model identifier
            host: HPC login node hostname
            username: SSH username
            key_path: Path to SSH private key
            slurm_config: SLURM job configuration
            work_dir: Working directory on HPC
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Job timeout in seconds
        """
        super().__init__(model, temperature, max_tokens, timeout)
        self.host = host
        self.username = username
        self.key_path = key_path
        self.slurm_config = slurm_config or SLURMConfig()
        self.work_dir = work_dir
        self._session: SSHSession | None = None
        self._current_job_id: str | None = None

    def setup(self) -> None:
        """Set up SSH connection to HPC."""
        self._session = SSHSession(
            session_name=f"hpc-{self.host}",
            host=self.host,
            username=self.username,
            key_path=self.key_path,
        )

        # Create work directory
        self._session.run_remote(f"mkdir -p {self.work_dir}")

        self._is_setup = True
        logger.info(f"HPC executor connected to {self.host}")

    def teardown(self) -> None:
        """Clean up SSH connection."""
        # Cancel any running job
        if self._current_job_id:
            self._session.run_remote(f"scancel {self._current_job_id}")

        if self._session:
            self._session.close()

        self._is_setup = False

    def _generate_slurm_script(self, command: str) -> str:
        """Generate SLURM submission script."""
        config = self.slurm_config

        account_line = f"#SBATCH --account={config.account}" if config.account else ""

        extra_lines = "\n".join(
            f"#SBATCH --{k}={v}" for k, v in config.extra_directives.items()
        )

        module_lines = "\n".join(f"module load {m}" for m in config.modules)

        return SLURM_TEMPLATE.format(
            job_name=config.job_name,
            partition=config.partition,
            nodes=config.nodes,
            gpus_per_node=config.gpus_per_node,
            cpus_per_task=config.cpus_per_task,
            memory_gb=config.memory_gb,
            time_limit=config.time_limit,
            output_pattern=config.output_pattern,
            error_pattern=config.error_pattern,
            account_line=account_line,
            extra_directives=extra_lines,
            module_loads=module_lines,
            command=command,
        )

    def submit_job(self, script_content: str) -> str:
        """
        Submit a SLURM job.

        Args:
            script_content: SLURM script content

        Returns:
            Job ID
        """
        if not self._session:
            raise RuntimeError("Not connected to HPC")

        # Write script to file
        script_path = f"{self.work_dir}/job.slurm"
        escaped_content = script_content.replace("'", "'\\''")
        self._session.run_remote(f"echo '{escaped_content}' > {script_path}")

        # Submit job
        result = self._session.run_remote(f"sbatch {script_path}")

        if not result.success:
            raise RuntimeError(f"Job submission failed: {result.stderr}")

        # Extract job ID
        match = re.search(r"Submitted batch job (\d+)", result.stdout)
        if match:
            job_id = match.group(1)
            self._current_job_id = job_id
            logger.info(f"Job submitted: {job_id}")
            return job_id

        raise RuntimeError(f"Could not parse job ID from: {result.stdout}")

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: int = 30,
    ) -> dict[str, Any]:
        """
        Wait for a SLURM job to complete.

        Args:
            job_id: SLURM job ID
            poll_interval: Seconds between status checks

        Returns:
            Job result information
        """
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            # Check job status
            result = self._session.run_remote(f"squeue -j {job_id} -h")

            if not result.stdout.strip():
                # Job no longer in queue - check completion status
                sacct = self._session.run_remote(
                    f"sacct -j {job_id} --format=State,ExitCode -n"
                )

                lines = sacct.stdout.strip().split("\n")
                if lines:
                    state = lines[0].split()[0] if lines[0].split() else "UNKNOWN"
                    return {
                        "job_id": job_id,
                        "state": state,
                        "success": state == "COMPLETED",
                        "duration": time.time() - start_time,
                    }

            logger.info(f"Job {job_id} still running...")
            time.sleep(poll_interval)

        # Timeout - cancel job
        self._session.run_remote(f"scancel {job_id}")
        return {
            "job_id": job_id,
            "state": "TIMEOUT",
            "success": False,
            "duration": time.time() - start_time,
        }

    def generate(self, prompt: str) -> str:
        """Generate using model on HPC (submits job and waits)."""
        if not self._is_setup:
            self.setup()

        # Create inference script
        # This is a simplified example - actual implementation would depend on
        # the inference framework being used (lm-eval, vLLM, etc.)

        inference_script = f"""
import json
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("{self.model}")
tokenizer = AutoTokenizer.from_pretrained("{self.model}")

prompt = '''{prompt}'''

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(
    **inputs,
    max_new_tokens={self.max_tokens},
    temperature={self.temperature},
    do_sample={self.temperature > 0}
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

with open("output.json", "w") as f:
    json.dump({{"response": response}}, f)
"""

        # Write inference script
        script_path = f"{self.work_dir}/inference.py"
        escaped = inference_script.replace("'", "'\\''")
        self._session.run_remote(f"echo '{escaped}' > {script_path}")

        # Generate and submit SLURM job
        slurm_script = self._generate_slurm_script(f"python {script_path}")
        job_id = self.submit_job(slurm_script)

        # Wait for completion
        result = self.wait_for_job(job_id)

        if not result["success"]:
            raise RuntimeError(f"Job failed with state: {result['state']}")

        # Read output
        output_result = self._session.run_remote(f"cat {self.work_dir}/output.json")

        import json
        data = json.loads(output_result.stdout)
        return data.get("response", "")

    def get_queue_status(self) -> list[dict[str, Any]]:
        """Get status of user's jobs in queue."""
        result = self._session.run_remote(
            f"squeue -u {self.username} --format='%i|%j|%T|%M|%l'"
        )

        jobs = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header
            parts = line.split("|")
            if len(parts) >= 5:
                jobs.append({
                    "job_id": parts[0],
                    "name": parts[1],
                    "state": parts[2],
                    "time": parts[3],
                    "time_limit": parts[4],
                })

        return jobs

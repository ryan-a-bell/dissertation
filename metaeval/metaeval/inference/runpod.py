"""RunPod cloud GPU execution."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

from metaeval.inference.base import ExecutorBase
from metaeval.inference.session import SSHSession
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PodConfig:
    """Configuration for RunPod pod."""

    gpu_type: str = "NVIDIA RTX A4000"
    gpu_count: int = 1
    container_disk_gb: int = 50
    volume_disk_gb: int = 100
    image: str = "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04"
    env_vars: dict[str, str] | None = None


class RunPodExecutor(ExecutorBase):
    """Execute models on RunPod cloud GPUs."""

    def __init__(
        self,
        model: str,
        api_key: str,
        ssh_key_path: Path | None = None,
        pod_config: PodConfig | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 300,
    ):
        """
        Initialize RunPod executor.

        Args:
            model: Model identifier (HuggingFace or local)
            api_key: RunPod API key
            ssh_key_path: Path to SSH private key
            pod_config: Pod configuration
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        super().__init__(model, temperature, max_tokens, timeout)
        self.api_key = api_key
        self.ssh_key_path = ssh_key_path
        self.pod_config = pod_config or PodConfig()
        self._pod_id: str | None = None
        self._pod_ip: str | None = None
        self._ssh_port: int = 22
        self._session: SSHSession | None = None

    def setup(self) -> None:
        """Set up RunPod pod and SSH connection."""
        try:
            import runpod
            runpod.api_key = self.api_key
        except ImportError:
            raise ImportError("runpod package required for RunPod execution")

        # Create pod
        logger.info("Creating RunPod pod...")
        pod = runpod.create_pod(
            name=f"metaeval-{self.model.replace('/', '-')}",
            image_name=self.pod_config.image,
            gpu_type_id=self.pod_config.gpu_type,
            gpu_count=self.pod_config.gpu_count,
            container_disk_in_gb=self.pod_config.container_disk_gb,
            volume_in_gb=self.pod_config.volume_disk_gb,
            env=self.pod_config.env_vars,
        )

        self._pod_id = pod["id"]
        logger.info(f"Pod created: {self._pod_id}")

        # Wait for pod to be ready
        self._wait_for_pod()

        # Get connection info
        pod_info = runpod.get_pod(self._pod_id)
        self._pod_ip = pod_info.get("runtime", {}).get("publicIp")

        # Find SSH port
        ports = pod_info.get("runtime", {}).get("ports", [])
        for port in ports:
            if port.get("privatePort") == 22:
                self._ssh_port = port.get("publicPort", 22)
                break

        # Set up SSH session
        if self._pod_ip:
            self._session = SSHSession(
                session_name=f"runpod-{self._pod_id}",
                host=self._pod_ip,
                username="root",
                key_path=self.ssh_key_path,
                port=self._ssh_port,
            )

        self._is_setup = True
        logger.info(f"RunPod executor ready: {self._pod_ip}:{self._ssh_port}")

    def _wait_for_pod(self, max_wait: int = 300) -> None:
        """Wait for pod to be running."""
        import runpod

        start_time = time.time()
        while time.time() - start_time < max_wait:
            pod = runpod.get_pod(self._pod_id)
            status = pod.get("desiredStatus")

            if status == "RUNNING":
                # Additional wait for SSH to be ready
                time.sleep(10)
                return

            logger.info(f"Pod status: {status}")
            time.sleep(5)

        raise TimeoutError(f"Pod did not start within {max_wait} seconds")

    def teardown(self) -> None:
        """Terminate the RunPod pod."""
        if self._session:
            self._session.close()

        if self._pod_id:
            try:
                import runpod
                runpod.api_key = self.api_key
                runpod.terminate_pod(self._pod_id)
                logger.info(f"Pod terminated: {self._pod_id}")
            except Exception as e:
                logger.error(f"Failed to terminate pod: {e}")

        self._pod_id = None
        self._is_setup = False

    def generate(self, prompt: str) -> str:
        """Generate using the model on RunPod."""
        if not self._is_setup:
            self.setup()

        # For now, assume Ollama is set up on the pod
        # Escape the prompt for shell
        escaped_prompt = prompt.replace("'", "'\\''")

        command = f"""curl -s http://localhost:11434/api/generate -d '{{
            "model": "{self.model}",
            "prompt": "{escaped_prompt}",
            "stream": false,
            "options": {{
                "temperature": {self.temperature},
                "num_predict": {self.max_tokens}
            }}
        }}'"""

        result = self._session.run_remote(command, timeout=self.timeout)

        if not result.success:
            raise RuntimeError(f"Generation failed: {result.stderr}")

        # Parse JSON response
        import json
        try:
            data = json.loads(result.stdout)
            return data.get("response", "")
        except json.JSONDecodeError:
            return result.stdout

    def provision_ollama(self) -> None:
        """Install and set up Ollama on the pod."""
        if not self._session:
            raise RuntimeError("No SSH session available")

        logger.info("Provisioning Ollama...")

        # Install Ollama
        self._session.run_remote("curl -fsSL https://ollama.com/install.sh | sh")

        # Start Ollama service
        self._session.run_remote("ollama serve &")
        time.sleep(5)

        # Pull the model
        logger.info(f"Pulling model: {self.model}")
        self._session.run_remote(f"ollama pull {self.model}")

        logger.info("Ollama provisioned successfully")

    def stream_command(self, command: str) -> Generator[str, None, int]:
        """Stream a command on the pod."""
        if not self._session:
            raise RuntimeError("No SSH session available")

        return self._session.stream_remote(command)

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Upload a file to the pod."""
        if not self._session:
            raise RuntimeError("No SSH session available")

        result = self._session.upload_file(local_path, remote_path)
        return result.success

    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """Download a file from the pod."""
        if not self._session:
            raise RuntimeError("No SSH session available")

        result = self._session.download_file(remote_path, local_path)
        return result.success

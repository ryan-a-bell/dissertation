"""
LLM Judge Automation Module

This module provides automated orchestration for the LLM-as-a-judge workflow,
eliminating the need for manual step-by-step execution.

Based on the manual debugging workflow from llm-judge-runpod-manual.ipynb.
"""

import time
import json
import paramiko
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
import runpod


class AutomationSession:
    """Session state manager for automated workflow"""

    def __init__(self, log_dir: Path, task_name: str):
        self.pod_id = None
        self.ssh = None
        self.ssh_host = None
        self.ssh_port = None
        self.start_time = time.time()
        self.task_name = task_name

        # Create session log
        self.session_log_dir = Path(log_dir) / f"auto_session_{int(time.time())}"
        self.session_log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.session_log_dir / 'session.log'

    def log(self, msg: str, level: str = 'INFO'):
        """Session logger with file and console output"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted = f"[{timestamp}] [{level}] {msg}"
        print(formatted)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')

    def elapsed(self) -> tuple[int, int]:
        """Return elapsed time as (minutes, seconds)"""
        elapsed = time.time() - self.start_time
        return int(elapsed // 60), int(elapsed % 60)


def create_and_connect_pod(
    session: AutomationSession,
    image_name: str,
    gpu_type: str,
    gpu_count: int = 1,
    container_disk_gb: int = 200,
    ssh_key_path: str = "~/.ssh/id_ed25519",
    max_create_attempts: int = 3,
    ssh_wait_timeout: int = 600,
) -> None:
    """
    Stage 1: Create RunPod instance and establish SSH connection

    Args:
        session: AutomationSession instance
        image_name: Docker image for the pod
        gpu_type: GPU type ID
        gpu_count: Number of GPUs
        container_disk_gb: Container disk size
        ssh_key_path: Path to SSH private key
        max_create_attempts: Max retries for pod creation
        ssh_wait_timeout: Max seconds to wait for SSH (default 10 min)

    Raises:
        RuntimeError: If pod creation or SSH connection fails
    """
    session.log("=" * 60)
    session.log("STAGE 1: Creating Pod and Establishing Connection")
    session.log("=" * 60)

    # Step 1: Create pod with retries
    session.log(f"Creating pod with {gpu_type}...")

    last_err = None
    for attempt in range(1, max_create_attempts + 1):
        try:
            session.log(f"  Attempt {attempt}/{max_create_attempts}...")
            pod = runpod.create_pod(
                name=f"llm-judge-auto-{int(time.time())}",
                image_name=image_name,
                gpu_type_id=gpu_type,
                gpu_count=gpu_count,
                container_disk_in_gb=container_disk_gb,
                min_vcpu_count=4,
                min_memory_in_gb=16,
                ports="22/tcp,11434/http",
                env={"OLLAMA_HOST": "0.0.0.0"},
                support_public_ip=True,
                start_ssh=True,
            )
            session.pod_id = pod.get("id")
            session.log(f"✓ Pod created: {session.pod_id}")
            break
        except Exception as e:
            last_err = e
            session.log(f"  Failed: {e}", level='WARN')
            if attempt < max_create_attempts:
                retry_delay = 10 * attempt  # Progressive backoff
                session.log(f"  Retrying in {retry_delay}s...")
                time.sleep(retry_delay)

    if not session.pod_id:
        raise RuntimeError(f"Pod creation failed after {max_create_attempts} attempts. Last error: {last_err}")

    # Step 2: Wait for SSH port
    session.log("Waiting for SSH port to become available...")
    max_attempts = ssh_wait_timeout // 10  # 10 second intervals

    for attempt in range(max_attempts):
        try:
            pod_meta = runpod.get_pod(session.pod_id)
            runtime = pod_meta.get('runtime', {})

            if runtime and runtime.get('ports'):
                for port_entry in runtime['ports']:
                    if port_entry.get('privatePort') == 22 and port_entry.get('isIpPublic'):
                        session.ssh_host = port_entry['ip']
                        session.ssh_port = port_entry['publicPort']
                        session.log(f"✓ SSH port found: {session.ssh_host}:{session.ssh_port}")
                        break

            if session.ssh_host:
                break

            if attempt % 6 == 0:  # Log every minute
                session.log(f"  Still waiting... ({attempt * 10}s elapsed)")

            time.sleep(10)

        except Exception as e:
            session.log(f"  Error checking pod: {e}", level='WARN')
            time.sleep(10)

    if not session.ssh_host:
        raise RuntimeError(f"SSH port never became available after {ssh_wait_timeout}s")

    # Step 3: Establish SSH connection
    session.log("Establishing SSH connection...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_key_path = Path(ssh_key_path).expanduser()
        session.log(f"  Loading SSH key: {ssh_key_path}")
        private_key = paramiko.Ed25519Key.from_private_key_file(str(ssh_key_path))

        session.log(f"  Connecting to {session.ssh_host}:{session.ssh_port}...")
        ssh.connect(
            hostname=session.ssh_host,
            port=session.ssh_port,
            username='root',
            pkey=private_key,
            timeout=30,
            banner_timeout=30
        )

        session.ssh = ssh
        session.log("✓ SSH connection established")

        # Quick connectivity test
        stdin, stdout, stderr = ssh.exec_command('whoami')
        user = stdout.read().decode().strip()
        session.log(f"  Connected as: {user}")

    except Exception as e:
        session.log(f"SSH connection failed: {e}", level='ERROR')
        raise RuntimeError(f"Failed to establish SSH connection: {e}")


def run_ssh_command(
    ssh: paramiko.SSHClient,
    cmd: str,
    desc: str,
    log_func: Callable,
    check_exit_code: bool = True,
    timeout: Optional[int] = None
) -> str:
    """
    Execute SSH command and return output

    Args:
        ssh: SSH client
        cmd: Command to execute
        desc: Description for logging
        log_func: Logging function
        check_exit_code: Raise exception if exit code != 0
        timeout: Command timeout in seconds

    Returns:
        Command stdout output

    Raises:
        RuntimeError: If command fails and check_exit_code is True
    """
    log_func(f"▶ {desc}")

    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()

    if out.strip():
        log_func(f"  {out.strip()}")
    if err.strip():
        log_func(f"  stderr: {err.strip()}", level='WARN')

    if check_exit_code and exit_code != 0:
        raise RuntimeError(f"{desc} failed with exit code {exit_code}")

    log_func(f"✓ {desc} completed (exit {exit_code})")
    return out


def stream_ssh_command(
    ssh: paramiko.SSHClient,
    cmd: str,
    log_func: Callable,
    prefix: str = "[pod]",
    check_exit_code: bool = True
) -> int:
    """
    Stream SSH command output in real-time

    Args:
        ssh: SSH client
        cmd: Command to execute
        log_func: Logging function
        prefix: Prefix for output lines
        check_exit_code: Raise exception if exit code != 0

    Returns:
        Exit code

    Raises:
        RuntimeError: If command fails and check_exit_code is True
    """
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)

    while True:
        # Read stdout
        if chan.recv_ready():
            data = chan.recv(4096).decode()
            for line in data.splitlines():
                output = f"{prefix} {line}"
                print(output)
                log_func(output)

        # Read stderr
        if chan.recv_stderr_ready():
            data = chan.recv_stderr(4096).decode()
            for line in data.splitlines():
                output = f"{prefix}:stderr {line}"
                print(output)
                log_func(output, level='WARN')

        # Check if done
        if chan.exit_status_ready():
            exit_code = chan.recv_exit_status()
            break

        time.sleep(0.2)

    if check_exit_code and exit_code != 0:
        raise RuntimeError(f"Command failed with exit code {exit_code}")

    return exit_code


def provision_pod_environment(
    session: AutomationSession,
    judge_model: str,
    skip_gpu_check: bool = False
) -> None:
    """
    Stage 2: Provision pod environment (install Ollama, pull model, etc.)

    Args:
        session: AutomationSession instance
        judge_model: Model name to pull (e.g., "gpt-oss:120b")
        skip_gpu_check: Skip GPU availability check

    Raises:
        RuntimeError: If provisioning fails
    """
    session.log("=" * 60)
    session.log("STAGE 2: Provisioning Pod Environment")
    session.log("=" * 60)

    ssh = session.ssh
    if not ssh:
        raise RuntimeError("SSH connection not established")

    # Step 1: Check GPU (optional)
    if not skip_gpu_check:
        session.log("Checking GPU availability...")
        try:
            gpu_info = run_ssh_command(
                ssh, 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader',
                "Query GPU info", session.log, check_exit_code=False
            )
            if gpu_info.strip():
                session.log(f"  GPU: {gpu_info.strip()}")
        except:
            session.log("  GPU check skipped (nvidia-smi not available)", level='WARN')

    # Step 2: Update apt and install dependencies
    session.log("Installing system dependencies...")
    run_ssh_command(
        ssh,
        "apt update && apt install -y lshw curl",
        "Install dependencies",
        session.log,
        timeout=300
    )

    # Step 3: Install Ollama
    session.log("Installing Ollama (may take 2-3 minutes)...")
    run_ssh_command(
        ssh,
        "curl -fsSL https://ollama.com/install.sh | sh",
        "Install Ollama",
        session.log,
        timeout=300
    )

    # Verify Ollama installation
    ollama_path = run_ssh_command(
        ssh, 'which ollama', "Locate Ollama binary", session.log
    ).strip()
    session.log(f"  Ollama installed at: {ollama_path}")

    # Step 4: Start Ollama server
    session.log("Starting Ollama server...")
    run_ssh_command(
        ssh,
        "nohup env OLLAMA_HOST=0.0.0.0 ollama serve > /root/ollama.log 2>&1 &",
        "Start Ollama server",
        session.log
    )

    session.log("  Waiting for server to initialize...")
    time.sleep(10)

    # Verify server is running
    proc_check = run_ssh_command(
        ssh,
        'ps aux | grep "ollama serve" | grep -v grep',
        "Check Ollama process",
        session.log,
        check_exit_code=False
    )

    if not proc_check.strip():
        session.log("  Warning: Ollama process not found", level='WARN')

    # Step 5: Test Ollama API
    session.log("Testing Ollama API...")
    for attempt in range(6):  # Try for 30 seconds
        try:
            api_response = run_ssh_command(
                ssh,
                "curl -s http://localhost:11434/api/tags",
                "Test Ollama API",
                session.log,
                check_exit_code=False
            )

            data = json.loads(api_response)
            session.log(f"✓ Ollama API ready (found {len(data.get('models', []))} models)")
            break
        except json.JSONDecodeError:
            if attempt < 5:
                session.log(f"  API not ready, retrying... ({attempt + 1}/6)")
                time.sleep(5)
            else:
                raise RuntimeError("Ollama API never became ready")

    # Step 6: Pull judge model
    session.log(f"Pulling judge model: {judge_model}")
    session.log("  This may take 5-10 minutes for large models...")
    session.log("=" * 60)

    try:
        stream_ssh_command(
            ssh,
            f"ollama pull {judge_model}",
            session.log,
            prefix=f"[ollama]",
            check_exit_code=True
        )
        session.log("=" * 60)
        session.log(f"✓ Model {judge_model} pulled successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to pull model: {e}")

    # Step 7: Verify model availability
    session.log("Verifying model availability...")
    api_response = run_ssh_command(
        ssh,
        "curl -s http://localhost:11434/api/tags",
        "List available models",
        session.log
    )

    data = json.loads(api_response)
    models = data.get('models', [])
    model_names = [m['name'] for m in models]

    session.log(f"  Available models ({len(models)}):")
    for name in model_names:
        session.log(f"    - {name}")

    if judge_model not in model_names:
        raise RuntimeError(f"Judge model {judge_model} not found in available models")

    session.log("✓ Environment provisioning complete")


def deploy_worker_script(
    session: AutomationSession,
    worker_script: str,
    input_samples: List[Dict[str, Any]],
) -> tuple[str, str]:
    """
    Stage 3: Deploy worker script and upload input data

    Args:
        session: AutomationSession instance
        worker_script: Python worker script content
        input_samples: List of sample dictionaries to process

    Returns:
        Tuple of (remote_input_path, remote_output_path)

    Raises:
        RuntimeError: If deployment fails
    """
    session.log("=" * 60)
    session.log("STAGE 3: Deploying Worker Script and Data")
    session.log("=" * 60)

    ssh = session.ssh
    if not ssh:
        raise RuntimeError("SSH connection not established")

    # Step 1: Upload worker script using heredoc
    session.log("Uploading worker script...")

    upload_cmd = f"cat > /root/pod_worker.py << 'WORKER_EOF'\n{worker_script}\nWORKER_EOF"
    run_ssh_command(ssh, upload_cmd, "Upload worker script", session.log)

    # Verify upload
    line_count = run_ssh_command(
        ssh, 'wc -l /root/pod_worker.py', "Check script size", session.log
    ).strip()
    session.log(f"  Worker script: {line_count}")

    # Step 2: Create remote job directory
    remote_job_dir = f"/root/job_{int(time.time())}"
    run_ssh_command(ssh, f"mkdir -p {remote_job_dir}", "Create job directory", session.log)

    # Step 3: Write input data locally
    session.log(f"Preparing input data ({len(input_samples)} samples)...")
    local_input = session.session_log_dir / 'input.jsonl'
    with open(local_input, 'w') as f:
        for sample in input_samples:
            f.write(json.dumps(sample) + '\n')

    session.log(f"  Local input file: {local_input}")

    # Step 4: Upload input data via SFTP
    session.log("Uploading input data to pod...")
    remote_input = f"{remote_job_dir}/input.jsonl"
    remote_output = f"{remote_job_dir}/output.jsonl"

    sftp = ssh.open_sftp()
    try:
        sftp.put(str(local_input), remote_input)
        session.log(f"  Uploaded to: {remote_input}")

        # Verify upload
        remote_lines = run_ssh_command(
            ssh, f'wc -l {remote_input}', "Verify input upload", session.log
        ).strip()
        session.log(f"  Remote file: {remote_lines}")

    finally:
        sftp.close()

    session.log("✓ Deployment complete")
    return remote_input, remote_output


def execute_and_monitor(
    session: AutomationSession,
    remote_input: str,
    remote_output: str,
    judge_model: str,
    prompt_id: str,
    temperature: float,
    max_tokens: int,
    task_name: str,
    model_name: str,
) -> Path:
    """
    Stage 4: Execute worker script and monitor progress

    Args:
        session: AutomationSession instance
        remote_input: Path to input file on pod
        remote_output: Path to output file on pod
        judge_model: Judge model name
        prompt_id: Prompt ID (e.g., "p1", "p2")
        temperature: Sampling temperature
        max_tokens: Max tokens for generation
        task_name: Task name
        model_name: Model being judged

    Returns:
        Path to downloaded output file

    Raises:
        RuntimeError: If execution fails
    """
    session.log("=" * 60)
    session.log("STAGE 4: Executing Worker and Monitoring Progress")
    session.log("=" * 60)

    ssh = session.ssh
    if not ssh:
        raise RuntimeError("SSH connection not established")

    # Step 1: Build worker command
    worker_cmd = (
        f"python3 /root/pod_worker.py "
        f"--input {remote_input} "
        f"--output {remote_output} "
        f"--judge-model {judge_model} "
        f"--prompt-id {prompt_id} "
        f"--temperature {temperature} "
        f"--max-tokens {max_tokens} "
        f"--task-name {task_name} "
        f"--model-name {model_name}"
    )

    session.log("Executing worker script...")
    session.log(f"  Command: {worker_cmd}")
    session.log("=" * 60)

    # Step 2: Execute with real-time streaming
    try:
        stream_ssh_command(ssh, worker_cmd, session.log, prefix="[worker]")
        session.log("=" * 60)
        session.log("✓ Worker script completed successfully")
    except Exception as e:
        session.log(f"Worker script failed: {e}", level='ERROR')
        raise

    # Step 3: Verify output file exists
    session.log("Checking output file...")
    file_info = run_ssh_command(
        ssh, f'ls -lh {remote_output}', "Check output file", session.log
    ).strip()
    session.log(f"  {file_info}")

    line_count = run_ssh_command(
        ssh, f'wc -l {remote_output}', "Count output lines", session.log
    ).strip()
    session.log(f"  Lines: {line_count}")

    # Step 4: Download output file
    session.log("Downloading output file...")
    local_output = session.session_log_dir / 'output.jsonl'

    sftp = ssh.open_sftp()
    try:
        sftp.get(remote_output, str(local_output))
        file_size = local_output.stat().st_size
        session.log(f"✓ Downloaded to: {local_output}")
        session.log(f"  Size: {file_size:,} bytes")
    finally:
        sftp.close()

    # Step 5: Validate output structure
    session.log("Validating output structure...")
    with open(local_output) as f:
        output_samples = [json.loads(line) for line in f]

    session.log(f"  Total samples: {len(output_samples)}")

    if output_samples:
        sample = output_samples[0]
        session.log(f"  Sample keys: {list(sample.keys())}")

        # Check for judge scores
        if 'judge_scores' in sample:
            scores = sample['judge_scores']
            session.log(f"  Judge scores found: {list(scores.keys())}")
        elif 'judgment' in sample:
            session.log(f"  Judgment field found")
        else:
            session.log("  Warning: No judge scores or judgment found", level='WARN')

    session.log("✓ Execution and monitoring complete")
    return local_output


def cleanup_pod(session: AutomationSession, force: bool = False) -> None:
    """
    Stage 5: Cleanup - close SSH and terminate pod

    Args:
        session: AutomationSession instance
        force: Force cleanup even if errors occur
    """
    session.log("=" * 60)
    session.log("STAGE 5: Cleanup")
    session.log("=" * 60)

    errors = []

    # Step 1: Close SSH
    if session.ssh:
        session.log("Closing SSH connection...")
        try:
            session.ssh.close()
            session.ssh = None
            session.log("✓ SSH connection closed")
        except Exception as e:
            msg = f"Error closing SSH: {e}"
            session.log(msg, level='WARN')
            errors.append(msg)

    # Step 2: Terminate pod
    if session.pod_id:
        session.log(f"Terminating pod {session.pod_id}...")
        try:
            runpod.terminate_pod(session.pod_id)
            session.log("✓ Pod terminated")
            session.pod_id = None
        except Exception as e:
            msg = f"Error terminating pod: {e}"
            session.log(msg, level='WARN')
            errors.append(msg)

    # Step 3: Session summary
    minutes, seconds = session.elapsed()
    session.log("=" * 60)
    session.log("SESSION SUMMARY")
    session.log("=" * 60)
    session.log(f"Duration: {minutes}m {seconds}s")
    session.log(f"Log file: {session.log_file}")
    session.log(f"Session dir: {session.session_log_dir}")

    if errors and not force:
        raise RuntimeError(f"Cleanup completed with errors: {errors}")
    elif errors:
        session.log(f"Cleanup completed with {len(errors)} errors (forced)", level='WARN')


def judge_with_automated_workflow(
    task_name: str,
    model_name: str,
    input_samples: List[Dict[str, Any]],
    judge_model: str,
    worker_script: str,
    log_dir: Path,
    prompt_id: str = "p1",
    temperature: float = 0.0,
    max_tokens: int = 2000,
    image_name: str = "runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04",
    gpu_type: str = "NVIDIA H200",
    gpu_count: int = 1,
    container_disk_gb: int = 200,
    ssh_key_path: str = "~/.ssh/id_ed25519",
    cleanup_on_error: bool = True,
) -> Dict[str, Any]:
    """
    Orchestrator function: Automated LLM-as-a-judge workflow

    This function automates the entire manual debugging workflow by executing
    all stages in sequence with comprehensive error handling and retry logic.

    Args:
        task_name: Task name (e.g., "sysengbench-osq")
        model_name: Model being judged (e.g., "anthropic__claude-sonnet-4.5")
        input_samples: List of sample dictionaries to judge
        judge_model: Judge model name (e.g., "gpt-oss:120b")
        worker_script: Python worker script content
        log_dir: Directory for logs
        prompt_id: Prompt ID (e.g., "p1", "p2")
        temperature: Sampling temperature
        max_tokens: Max tokens for generation
        image_name: Docker image for pod
        gpu_type: GPU type ID
        gpu_count: Number of GPUs
        container_disk_gb: Container disk size
        ssh_key_path: Path to SSH private key
        cleanup_on_error: Whether to cleanup pod on error

    Returns:
        Dictionary with results:
        {
            'success': bool,
            'output_file': Path,
            'session_dir': Path,
            'samples_processed': int,
            'duration_seconds': float,
            'error': Optional[str]
        }

    Example:
        >>> samples = load_samples("model_samples.jsonl")
        >>> result = judge_with_automated_workflow(
        ...     task_name="sysengbench-osq",
        ...     model_name="anthropic__claude-sonnet-4.5",
        ...     input_samples=samples[:10],
        ...     judge_model="gpt-oss:120b",
        ...     worker_script=POD_WORKER_SCRIPT_VERBOSE,
        ...     log_dir=Path("./logs"),
        ... )
        >>> if result['success']:
        ...     print(f"Processed {result['samples_processed']} samples")
        ...     print(f"Output: {result['output_file']}")
    """
    session = AutomationSession(log_dir, task_name)

    session.log("=" * 70)
    session.log("AUTOMATED LLM-AS-A-JUDGE WORKFLOW")
    session.log("=" * 70)
    session.log(f"Task: {task_name}")
    session.log(f"Model: {model_name}")
    session.log(f"Samples: {len(input_samples)}")
    session.log(f"Judge Model: {judge_model}")
    session.log(f"GPU Type: {gpu_type}")
    session.log("=" * 70)

    result = {
        'success': False,
        'output_file': None,
        'session_dir': session.session_log_dir,
        'samples_processed': 0,
        'duration_seconds': 0.0,
        'error': None
    }

    try:
        # Stage 1: Create and connect
        create_and_connect_pod(
            session=session,
            image_name=image_name,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            container_disk_gb=container_disk_gb,
            ssh_key_path=ssh_key_path,
        )

        # Stage 2: Provision environment
        provision_pod_environment(
            session=session,
            judge_model=judge_model,
        )

        # Stage 3: Deploy worker and data
        remote_input, remote_output = deploy_worker_script(
            session=session,
            worker_script=worker_script,
            input_samples=input_samples,
        )

        # Stage 4: Execute and monitor
        output_file = execute_and_monitor(
            session=session,
            remote_input=remote_input,
            remote_output=remote_output,
            judge_model=judge_model,
            prompt_id=prompt_id,
            temperature=temperature,
            max_tokens=max_tokens,
            task_name=task_name,
            model_name=model_name,
        )

        # Success!
        result['success'] = True
        result['output_file'] = output_file
        result['samples_processed'] = len(input_samples)

    except Exception as e:
        error_msg = f"Workflow failed: {e}"
        session.log(error_msg, level='ERROR')
        result['error'] = str(e)

        if not cleanup_on_error:
            session.log("Skipping cleanup (cleanup_on_error=False)", level='WARN')
            session.log("You must manually cleanup the pod!", level='WARN')
            raise

    finally:
        # Stage 5: Always cleanup (unless disabled)
        if cleanup_on_error or result['success']:
            try:
                cleanup_pod(session, force=True)
            except Exception as e:
                session.log(f"Cleanup error (non-fatal): {e}", level='WARN')

        # Calculate final duration
        elapsed = time.time() - session.start_time
        result['duration_seconds'] = elapsed

        minutes, seconds = session.elapsed()
        session.log("=" * 70)
        if result['success']:
            session.log("✅ WORKFLOW COMPLETED SUCCESSFULLY")
            session.log(f"Processed {result['samples_processed']} samples in {minutes}m {seconds}s")
            session.log(f"Output: {result['output_file']}")
        else:
            session.log("❌ WORKFLOW FAILED")
            session.log(f"Error: {result['error']}")
            session.log(f"Failed after {minutes}m {seconds}s")
        session.log(f"Session logs: {session.session_log_dir}")
        session.log("=" * 70)

    return result

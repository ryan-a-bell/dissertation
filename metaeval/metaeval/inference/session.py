"""Automation session management."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

from metaeval.core.logging import SessionLogger, get_logger

logger = get_logger(__name__)


@dataclass
class CommandResult:
    """Result from command execution."""

    command: str
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    success: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
        }


class AutomationSession:
    """Manage long-running automation sessions with logging."""

    def __init__(
        self,
        session_name: str,
        log_dir: Path | None = None,
        working_dir: Path | None = None,
    ):
        """
        Initialize automation session.

        Args:
            session_name: Name of the session
            log_dir: Directory for log files
            working_dir: Working directory for commands
        """
        self.session_name = session_name
        self.start_time = datetime.now()
        self.working_dir = working_dir or Path.cwd()
        self.log_dir = log_dir or Path("logs")

        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = SessionLogger(session_name, self.log_dir)
        self.command_history: list[CommandResult] = []

        self.logger.info(f"Session started: {session_name}")

    def run_command(
        self,
        command: str,
        timeout: int | None = None,
        capture_output: bool = True,
    ) -> CommandResult:
        """
        Run a shell command.

        Args:
            command: Command to run
            timeout: Optional timeout in seconds
            capture_output: Whether to capture stdout/stderr

        Returns:
            CommandResult with output and status
        """
        self.logger.info(f"Running: {command}")
        start_time = time.time()

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )

            duration = time.time() - start_time

            cmd_result = CommandResult(
                command=command,
                return_code=result.returncode,
                stdout=result.stdout if capture_output else "",
                stderr=result.stderr if capture_output else "",
                duration_seconds=duration,
                success=result.returncode == 0,
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            cmd_result = CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr="Command timed out",
                duration_seconds=duration,
                success=False,
            )
            self.logger.error(f"Command timed out after {timeout}s")

        except Exception as e:
            duration = time.time() - start_time
            cmd_result = CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                duration_seconds=duration,
                success=False,
            )
            self.logger.error(f"Command failed: {e}")

        self.command_history.append(cmd_result)

        if cmd_result.success:
            self.logger.info(f"Command completed in {duration:.2f}s")
        else:
            self.logger.error(f"Command failed with code {cmd_result.return_code}")

        return cmd_result

    def stream_command(
        self,
        command: str,
        timeout: int | None = None,
    ) -> Generator[str, None, int]:
        """
        Run a command and stream output.

        Args:
            command: Command to run
            timeout: Optional timeout in seconds

        Yields:
            Output lines

        Returns:
            Return code
        """
        self.logger.info(f"Streaming: {command}")

        process = subprocess.Popen(
            command,
            shell=True,
            cwd=self.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        start_time = time.time()
        output_lines = []

        try:
            for line in iter(process.stdout.readline, ""):
                if timeout and (time.time() - start_time) > timeout:
                    process.kill()
                    raise subprocess.TimeoutExpired(command, timeout)

                output_lines.append(line)
                yield line.rstrip()

            process.wait()

            self.command_history.append(CommandResult(
                command=command,
                return_code=process.returncode,
                stdout="".join(output_lines),
                stderr="",
                duration_seconds=time.time() - start_time,
                success=process.returncode == 0,
            ))

            return process.returncode

        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout}s")
            return -1

    def elapsed(self) -> tuple[int, int]:
        """
        Get elapsed time since session start.

        Returns:
            Tuple of (minutes, seconds)
        """
        return self.logger.elapsed()

    def elapsed_str(self) -> str:
        """Get elapsed time as string."""
        m, s = self.elapsed()
        return f"{m:02d}:{s:02d}"

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)

    def get_summary(self) -> dict[str, Any]:
        """
        Get session summary.

        Returns:
            Summary dictionary
        """
        total_commands = len(self.command_history)
        successful = sum(1 for c in self.command_history if c.success)
        failed = total_commands - successful

        return {
            "session_name": self.session_name,
            "start_time": self.start_time.isoformat(),
            "elapsed": self.elapsed_str(),
            "total_commands": total_commands,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_commands if total_commands > 0 else 0,
        }

    def close(self) -> None:
        """Close the session."""
        summary = self.get_summary()
        self.logger.info(f"Session closed. Summary: {summary}")


class SSHSession(AutomationSession):
    """Automation session with SSH support."""

    def __init__(
        self,
        session_name: str,
        host: str,
        username: str,
        key_path: Path | None = None,
        port: int = 22,
        **kwargs: Any,
    ):
        """
        Initialize SSH session.

        Args:
            session_name: Name of the session
            host: SSH host
            username: SSH username
            key_path: Path to SSH private key
            port: SSH port
            **kwargs: Additional arguments for AutomationSession
        """
        super().__init__(session_name, **kwargs)
        self.host = host
        self.username = username
        self.key_path = key_path
        self.port = port
        self._ssh_client = None

    def _build_ssh_command(self, remote_command: str) -> str:
        """Build SSH command string."""
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no"

        if self.key_path:
            ssh_cmd += f" -i {self.key_path}"

        if self.port != 22:
            ssh_cmd += f" -p {self.port}"

        ssh_cmd += f" {self.username}@{self.host}"
        ssh_cmd += f" '{remote_command}'"

        return ssh_cmd

    def run_remote(
        self,
        command: str,
        timeout: int | None = None,
    ) -> CommandResult:
        """
        Run a command on the remote host.

        Args:
            command: Command to run remotely
            timeout: Optional timeout in seconds

        Returns:
            CommandResult
        """
        ssh_command = self._build_ssh_command(command)
        return self.run_command(ssh_command, timeout=timeout)

    def stream_remote(
        self,
        command: str,
        timeout: int | None = None,
    ) -> Generator[str, None, int]:
        """
        Stream a remote command's output.

        Args:
            command: Command to run remotely
            timeout: Optional timeout in seconds

        Yields:
            Output lines

        Returns:
            Return code
        """
        ssh_command = self._build_ssh_command(command)
        return self.stream_command(ssh_command, timeout=timeout)

    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
    ) -> CommandResult:
        """
        Upload a file to the remote host.

        Args:
            local_path: Local file path
            remote_path: Remote destination path

        Returns:
            CommandResult
        """
        scp_cmd = f"scp -o StrictHostKeyChecking=no"

        if self.key_path:
            scp_cmd += f" -i {self.key_path}"

        if self.port != 22:
            scp_cmd += f" -P {self.port}"

        scp_cmd += f" {local_path} {self.username}@{self.host}:{remote_path}"

        return self.run_command(scp_cmd)

    def download_file(
        self,
        remote_path: str,
        local_path: Path,
    ) -> CommandResult:
        """
        Download a file from the remote host.

        Args:
            remote_path: Remote file path
            local_path: Local destination path

        Returns:
            CommandResult
        """
        scp_cmd = f"scp -o StrictHostKeyChecking=no"

        if self.key_path:
            scp_cmd += f" -i {self.key_path}"

        if self.port != 22:
            scp_cmd += f" -P {self.port}"

        scp_cmd += f" {self.username}@{self.host}:{remote_path} {local_path}"

        return self.run_command(scp_cmd)

"""Logging utilities for metaeval."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
    format_string: str | None = None,
) -> None:
    """
    Set up logging configuration for metaeval.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for logging output
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"metaeval.{name}")


class SessionLogger:
    """Logger for tracking long-running automation sessions."""

    def __init__(
        self,
        session_name: str,
        log_dir: Path | None = None,
        stream: TextIO | None = None,
    ):
        """
        Initialize session logger.

        Args:
            session_name: Name of the session for identification
            log_dir: Directory to store log files
            stream: Optional stream for output (default: stdout)
        """
        self.session_name = session_name
        self.start_time = datetime.now()
        self.log_dir = log_dir
        self.stream = stream or sys.stdout

        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
            self.log_file = log_dir / f"{session_name}_{timestamp}.log"
        else:
            self.log_file = None

    def log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message with timestamp and elapsed time.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        elapsed = self.elapsed()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] [{elapsed[0]:02d}:{elapsed[1]:02d}] {message}"

        print(formatted, file=self.stream)

        if self.log_file:
            with open(self.log_file, "a") as f:
                print(formatted, file=f)

    def elapsed(self) -> tuple[int, int]:
        """
        Get elapsed time since session start.

        Returns:
            Tuple of (minutes, seconds)
        """
        delta = datetime.now() - self.start_time
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return (minutes, seconds)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.log(message, "INFO")

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.log(message, "WARNING")

    def error(self, message: str) -> None:
        """Log an error message."""
        self.log(message, "ERROR")

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.log(message, "DEBUG")

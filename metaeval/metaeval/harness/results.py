"""lm-eval results.json parsing."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class LMEvalResults:
    """Parsed lm-eval results.json file."""

    task_name: str
    model_name: str
    model_name_sanitized: str

    # Metrics
    accuracy: float | None = None
    accuracy_stderr: float | None = None

    # Metadata
    n_samples: int = 0
    eval_time_seconds: float = 0.0
    lm_eval_version: str = ""
    date: datetime | None = None

    # Raw data for extensibility
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: Path | str) -> "LMEvalResults":
        """
        Load from lm-eval results.json file.

        Args:
            path: Path to results.json or results_*.json file

        Returns:
            LMEvalResults instance
        """
        path = Path(path)
        data = json.loads(path.read_text())

        # Extract first task (usually only one per results file)
        task_name = list(data.get("results", {}).keys())[0] if data.get("results") else ""
        task_results = data.get("results", {}).get(task_name, {})

        # Find accuracy metric (key varies: exact_match,none or exact_match,strict-match)
        accuracy = None
        accuracy_stderr = None
        for key, value in task_results.items():
            if "exact_match" in key and "stderr" not in key:
                accuracy = value
            elif "stderr" in key:
                accuracy_stderr = value

        # Parse n_samples
        n_samples_data = data.get("n-samples", {}).get(task_name, {})
        n_samples = n_samples_data.get("effective", n_samples_data.get("original", 0))

        # Parse eval time (can be string or float)
        eval_time = data.get("total_evaluation_time_seconds", 0)
        if isinstance(eval_time, str):
            eval_time = float(eval_time)

        # Parse date
        date = None
        if "date" in data:
            try:
                date = datetime.fromtimestamp(data["date"])
            except (TypeError, ValueError, OSError):
                pass

        return cls(
            task_name=task_name,
            model_name=data.get("model_name", ""),
            model_name_sanitized=data.get("model_name_sanitized", ""),
            accuracy=accuracy,
            accuracy_stderr=accuracy_stderr,
            n_samples=n_samples,
            eval_time_seconds=eval_time,
            lm_eval_version=data.get("lm_eval_version", ""),
            date=date,
            raw=data,
        )

    def get_metric(self, metric: str) -> float | None:
        """
        Get a specific metric value.

        Args:
            metric: Metric name (e.g., "exact_match", "acc")

        Returns:
            Metric value or None if not found
        """
        task_results = self.raw.get("results", {}).get(self.task_name, {})
        for key, value in task_results.items():
            if metric in key and "stderr" not in key:
                return value
        return None

    @property
    def is_mcq(self) -> bool:
        """Check if this is an MCQ task based on task name."""
        return "osq" not in self.task_name.lower()

    @property
    def is_osq(self) -> bool:
        """Check if this is an OSQ task based on task name."""
        return "osq" in self.task_name.lower()

    @property
    def variant(self) -> str:
        """
        Extract position variant from task name.

        Returns:
            Variant letter (A, B, C, D) or empty string for base/OSQ tasks
        """
        name = self.task_name.lower()
        if name.endswith("-a") or name == "sysengbench":
            return "A"
        elif name.endswith("-b"):
            return "B"
        elif name.endswith("-c"):
            return "C"
        elif name.endswith("-d"):
            return "D"
        return ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_name": self.task_name,
            "model_name": self.model_name,
            "model_name_sanitized": self.model_name_sanitized,
            "accuracy": self.accuracy,
            "accuracy_stderr": self.accuracy_stderr,
            "n_samples": self.n_samples,
            "eval_time_seconds": self.eval_time_seconds,
            "lm_eval_version": self.lm_eval_version,
            "date": self.date.isoformat() if self.date else None,
        }

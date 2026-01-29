"""Progress tracking and checkpointing for batch operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BatchProgress:
    """Progress information for a batch operation."""

    total: int
    completed: int
    failed: int
    cached: int
    skipped: int
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def remaining(self) -> int:
        """Number of items remaining."""
        return self.total - self.completed - self.failed - self.skipped

    @property
    def percent_complete(self) -> float:
        """Percentage of items completed."""
        if self.total == 0:
            return 100.0
        return ((self.completed + self.failed + self.skipped) / self.total) * 100

    @property
    def is_complete(self) -> bool:
        """Whether all items have been processed."""
        return self.remaining == 0

    def format_status(self) -> str:
        """Format progress status for display."""
        parts = [f"{self.completed + self.failed + self.skipped}/{self.total}"]

        details = []
        if self.cached > 0:
            details.append(f"{self.cached} cached")
        if self.skipped > 0:
            details.append(f"{self.skipped} skipped")
        if self.failed > 0:
            details.append(f"{self.failed} failed")

        if details:
            parts.append(f"({', '.join(details)})")

        return " ".join(parts)


class CheckpointManager:
    """
    Manages checkpointing for resumable batch operations.

    Uses JSONL format where each line is a completed result. This allows:
    - Append-only writes for reliability
    - Easy resumption by reading completed IDs
    - Human-readable output
    - Streaming compatibility

    Example usage:
        checkpoint = CheckpointManager(output_path)
        completed_ids = checkpoint.load_completed_ids()

        for item in items:
            if item["question_id"] in completed_ids:
                continue  # Skip already processed

            result = process(item)
            checkpoint.save_result(result)
    """

    def __init__(self, output_path: Path | str):
        """
        Initialize checkpoint manager.

        Args:
            output_path: Path to the output JSONL file (also used as checkpoint)
        """
        self.output_path = Path(output_path)
        self._completed_ids: set[str] | None = None
        self._completed_count: int = 0
        self._failed_count: int = 0

    def load_completed_ids(self) -> set[str]:
        """
        Load set of completed question IDs from existing output.

        Returns:
            Set of question_id values that have already been processed
        """
        if self._completed_ids is not None:
            return self._completed_ids

        self._completed_ids = set()
        self._completed_count = 0
        self._failed_count = 0

        if not self.output_path.exists():
            return self._completed_ids

        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        question_id = data.get("question_id")
                        if question_id is not None:
                            self._completed_ids.add(str(question_id))
                            if "error" in data:
                                self._failed_count += 1
                            else:
                                self._completed_count += 1
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping malformed line {line_num}: {e}")

            logger.info(
                f"Resuming: found {len(self._completed_ids)} completed items "
                f"({self._completed_count} success, {self._failed_count} failed)"
            )

        except OSError as e:
            logger.warning(f"Could not read checkpoint file: {e}")

        return self._completed_ids

    def save_result(self, result: dict[str, Any]) -> None:
        """
        Save a single result to the output file (append).

        Args:
            result: Result dictionary (must contain question_id)
        """
        # Ensure parent directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

            # Update tracking
            question_id = result.get("question_id")
            if question_id is not None:
                if self._completed_ids is not None:
                    self._completed_ids.add(str(question_id))
                if "error" in result:
                    self._failed_count += 1
                else:
                    self._completed_count += 1

        except OSError as e:
            logger.error(f"Could not save result: {e}")
            raise

    def get_progress(self, total: int, cached: int = 0) -> BatchProgress:
        """
        Get current progress information.

        Args:
            total: Total number of items to process
            cached: Number of items served from cache

        Returns:
            BatchProgress with current status
        """
        completed_ids = self.load_completed_ids()
        return BatchProgress(
            total=total,
            completed=self._completed_count,
            failed=self._failed_count,
            cached=cached,
            skipped=len(completed_ids),
        )

    def clear(self) -> None:
        """Clear checkpoint file to start fresh."""
        if self.output_path.exists():
            self.output_path.unlink()
        self._completed_ids = None
        self._completed_count = 0
        self._failed_count = 0
        logger.info(f"Cleared checkpoint: {self.output_path}")

    def iter_results(self) -> Iterator[dict[str, Any]]:
        """
        Iterate over completed results.

        Yields:
            Result dictionaries from the output file
        """
        if not self.output_path.exists():
            return

        with open(self.output_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

    def count(self) -> int:
        """Return count of completed items."""
        self.load_completed_ids()
        return len(self._completed_ids) if self._completed_ids else 0


class ProgressTracker:
    """
    Tracks progress for batch operations with live updates.

    Provides a context manager interface and callback-based updates
    that work well with tqdm or custom progress displays.
    """

    def __init__(
        self,
        total: int,
        description: str = "Processing",
        checkpoint: CheckpointManager | None = None,
    ):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items
            description: Description for progress display
            checkpoint: Optional checkpoint manager for resumability
        """
        self.total = total
        self.description = description
        self.checkpoint = checkpoint

        self.completed = 0
        self.failed = 0
        self.cached = 0
        self.skipped = 0

        self._callbacks: list = []

    def add_callback(self, callback) -> None:
        """Add a progress callback function."""
        self._callbacks.append(callback)

    def update(
        self,
        completed: int = 0,
        failed: int = 0,
        cached: int = 0,
        skipped: int = 0,
    ) -> None:
        """
        Update progress counters.

        Args:
            completed: Number of newly completed items
            failed: Number of newly failed items
            cached: Number of items from cache
            skipped: Number of skipped items
        """
        self.completed += completed
        self.failed += failed
        self.cached += cached
        self.skipped += skipped

        progress = self.get_progress()
        for callback in self._callbacks:
            callback(progress)

    def get_progress(self) -> BatchProgress:
        """Get current progress information."""
        return BatchProgress(
            total=self.total,
            completed=self.completed,
            failed=self.failed,
            cached=self.cached,
            skipped=self.skipped,
        )

    def format_description(self, model: str = "") -> str:
        """Format description with progress info."""
        progress = self.get_progress()
        desc = f"{self.description}"
        if model:
            desc += f" with {model}"

        status = progress.format_status()
        return f"{desc} [{status}]"

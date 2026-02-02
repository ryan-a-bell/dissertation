"""Tests for the progress module."""

import json
import tempfile
from pathlib import Path

import pytest

from metaeval.core.progress import (
    BatchProgress,
    CheckpointManager,
    ProgressTracker,
)


class TestBatchProgress:
    """Tests for BatchProgress dataclass."""

    def test_create_progress(self):
        """Test creating a progress instance."""
        progress = BatchProgress(
            total=100,
            completed=25,
            failed=2,
            cached=10,
            skipped=5,
        )
        assert progress.total == 100
        assert progress.completed == 25
        assert progress.failed == 2
        assert progress.cached == 10
        assert progress.skipped == 5

    def test_remaining(self):
        """Test remaining property."""
        progress = BatchProgress(
            total=100,
            completed=30,
            failed=5,
            cached=0,
            skipped=10,
        )
        # remaining = total - completed - failed - skipped
        assert progress.remaining == 55

    def test_remaining_all_done(self):
        """Test remaining when all items are processed."""
        progress = BatchProgress(
            total=100,
            completed=90,
            failed=5,
            cached=0,
            skipped=5,
        )
        assert progress.remaining == 0

    def test_percent_complete(self):
        """Test percent_complete property."""
        progress = BatchProgress(
            total=100,
            completed=40,
            failed=10,
            cached=0,
            skipped=0,
        )
        # (completed + failed + skipped) / total * 100
        assert progress.percent_complete == 50.0

    def test_percent_complete_empty(self):
        """Test percent_complete with zero total."""
        progress = BatchProgress(
            total=0,
            completed=0,
            failed=0,
            cached=0,
            skipped=0,
        )
        assert progress.percent_complete == 100.0

    def test_is_complete(self):
        """Test is_complete property."""
        incomplete = BatchProgress(
            total=100,
            completed=50,
            failed=0,
            cached=0,
            skipped=0,
        )
        assert incomplete.is_complete is False

        complete = BatchProgress(
            total=100,
            completed=95,
            failed=5,
            cached=0,
            skipped=0,
        )
        assert complete.is_complete is True

    def test_format_status_basic(self):
        """Test format_status with basic counts."""
        progress = BatchProgress(
            total=100,
            completed=50,
            failed=0,
            cached=0,
            skipped=0,
        )
        status = progress.format_status()
        assert "50/100" in status

    def test_format_status_with_details(self):
        """Test format_status with cached/skipped/failed."""
        progress = BatchProgress(
            total=100,
            completed=40,
            failed=5,
            cached=10,
            skipped=15,
        )
        status = progress.format_status()
        assert "60/100" in status  # 40 + 5 + 15
        assert "10 cached" in status
        assert "15 skipped" in status
        assert "5 failed" in status


class TestCheckpointManager:
    """Tests for CheckpointManager class."""

    def test_init(self):
        """Test checkpoint manager initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)
            assert checkpoint.output_path == path

    def test_load_completed_ids_empty(self):
        """Test loading from non-existent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            completed = checkpoint.load_completed_ids()
            assert completed == set()

    def test_save_and_load_result(self):
        """Test saving and loading results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            # Save some results
            checkpoint.save_result({"question_id": "q1", "score": 85})
            checkpoint.save_result({"question_id": "q2", "score": 90})
            checkpoint.save_result({"question_id": "q3", "score": 75})

            # Load completed IDs
            completed = checkpoint.load_completed_ids()
            assert completed == {"q1", "q2", "q3"}

    def test_save_result_with_error(self):
        """Test that errors are tracked separately."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": "q1", "score": 85})
            checkpoint.save_result({"question_id": "q2", "error": "Failed to process"})

            progress = checkpoint.get_progress(total=10)
            assert progress.completed == 1  # Only successful ones
            assert progress.failed == 1

    def test_save_result_creates_parent_dir(self):
        """Test that save_result creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "nested" / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": "q1", "score": 100})

            assert path.exists()
            assert path.parent.exists()

    def test_clear(self):
        """Test clearing checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": "q1", "score": 85})
            assert path.exists()

            checkpoint.clear()
            assert not path.exists()

            completed = checkpoint.load_completed_ids()
            assert completed == set()

    def test_get_progress(self):
        """Test getting progress information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": "q1", "score": 85})
            checkpoint.save_result({"question_id": "q2", "score": 90})
            checkpoint.save_result({"question_id": "q3", "error": "Failed"})

            progress = checkpoint.get_progress(total=10, cached=2)
            assert progress.total == 10
            assert progress.completed == 2  # q1, q2
            assert progress.failed == 1     # q3
            assert progress.cached == 2
            assert progress.skipped == 3    # All completed IDs

    def test_iter_results(self):
        """Test iterating over results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": "q1", "score": 85})
            checkpoint.save_result({"question_id": "q2", "score": 90})

            results = list(checkpoint.iter_results())
            assert len(results) == 2
            assert results[0]["question_id"] == "q1"
            assert results[1]["question_id"] == "q2"

    def test_iter_results_empty(self):
        """Test iterating over empty/nonexistent file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            results = list(checkpoint.iter_results())
            assert results == []

    def test_count(self):
        """Test count method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            assert checkpoint.count() == 0

            checkpoint.save_result({"question_id": "q1", "score": 85})
            checkpoint.save_result({"question_id": "q2", "score": 90})

            assert checkpoint.count() == 2

    def test_handles_malformed_lines(self):
        """Test that malformed lines are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"

            # Write mixed valid/invalid lines
            with open(path, "w") as f:
                f.write('{"question_id": "q1", "score": 85}\n')
                f.write("not valid json\n")
                f.write('{"question_id": "q2", "score": 90}\n')

            checkpoint = CheckpointManager(path)
            completed = checkpoint.load_completed_ids()

            assert completed == {"q1", "q2"}

    def test_persistence_across_instances(self):
        """Test that data persists across checkpoint instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"

            # First instance
            cp1 = CheckpointManager(path)
            cp1.save_result({"question_id": "q1", "score": 85})

            # Second instance (simulating process restart)
            cp2 = CheckpointManager(path)
            completed = cp2.load_completed_ids()

            assert "q1" in completed

    def test_integer_question_ids(self):
        """Test that integer question IDs work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            checkpoint.save_result({"question_id": 1, "score": 85})
            checkpoint.save_result({"question_id": 2, "score": 90})

            completed = checkpoint.load_completed_ids()
            assert "1" in completed
            assert "2" in completed


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_init(self):
        """Test progress tracker initialization."""
        tracker = ProgressTracker(total=100, description="Testing")
        assert tracker.total == 100
        assert tracker.description == "Testing"
        assert tracker.completed == 0
        assert tracker.failed == 0

    def test_update(self):
        """Test updating progress."""
        tracker = ProgressTracker(total=100)

        tracker.update(completed=5)
        assert tracker.completed == 5

        tracker.update(completed=3, failed=1)
        assert tracker.completed == 8
        assert tracker.failed == 1

        tracker.update(cached=2, skipped=1)
        assert tracker.cached == 2
        assert tracker.skipped == 1

    def test_get_progress(self):
        """Test getting progress as BatchProgress."""
        tracker = ProgressTracker(total=100)
        tracker.update(completed=30, failed=5, cached=10, skipped=5)

        progress = tracker.get_progress()
        assert isinstance(progress, BatchProgress)
        assert progress.total == 100
        assert progress.completed == 30
        assert progress.failed == 5
        assert progress.cached == 10
        assert progress.skipped == 5

    def test_callback(self):
        """Test progress callbacks."""
        tracker = ProgressTracker(total=100)

        received_progress = []

        def callback(progress):
            received_progress.append(progress)

        tracker.add_callback(callback)

        tracker.update(completed=10)
        tracker.update(completed=20)

        assert len(received_progress) == 2
        assert received_progress[0].completed == 10
        assert received_progress[1].completed == 30

    def test_format_description(self):
        """Test format_description method."""
        tracker = ProgressTracker(total=100, description="Judging")
        tracker.update(completed=25, failed=5)

        desc = tracker.format_description(model="gpt-4o")
        assert "Judging" in desc
        assert "gpt-4o" in desc
        assert "30/100" in desc  # completed + failed

    def test_with_checkpoint(self):
        """Test progress tracker with checkpoint manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "output.jsonl"
            checkpoint = CheckpointManager(path)

            tracker = ProgressTracker(
                total=100,
                description="Processing",
                checkpoint=checkpoint,
            )

            assert tracker.checkpoint is checkpoint

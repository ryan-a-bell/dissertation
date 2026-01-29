"""Tests for judge base classes."""

import tempfile
from pathlib import Path

import pytest

from metaeval.judges.base import JudgeSettings, JudgeBase
from metaeval.core.config import get_config, reset_config
from metaeval.core.cache import JudgeCache, reset_cache


class TestJudgeSettings:
    """Tests for JudgeSettings dataclass."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def test_defaults(self):
        """Test default values."""
        settings = JudgeSettings()
        assert settings.temperature == 0.0
        assert settings.max_tokens == 2048
        assert settings.timeout == 300
        assert settings.prompt_style == "multi_dimensional"

    def test_custom_values(self):
        """Test custom values."""
        settings = JudgeSettings(
            temperature=0.7,
            max_tokens=4096,
            prompt_style="chain_of_thought",
        )
        assert settings.temperature == 0.7
        assert settings.max_tokens == 4096
        assert settings.prompt_style == "chain_of_thought"

    def test_from_config(self):
        """Test creating settings from global config."""
        settings = JudgeSettings.from_config()
        config = get_config()

        assert settings.temperature == config.judge.temperature
        assert settings.max_tokens == config.judge.max_tokens
        assert settings.timeout == config.judge.timeout


class TestJudgeBase:
    """Tests for JudgeBase abstract class."""

    def test_cannot_instantiate_abstract(self):
        """Test that JudgeBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            JudgeBase("test-model")

    def test_concrete_implementation(self):
        """Test that concrete implementation works."""

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                return '{"technical_accuracy": 15, "conceptual_understanding": 12, "completeness": 14, "clarity_organization": 10, "professional_relevance": 9, "total_score": 60, "justification": "Good response"}'

        judge = MockJudge("mock-model")
        assert judge.model == "mock-model"
        assert judge.settings is not None

    def test_judge_method(self):
        """Test the judge method."""

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                return '{"technical_accuracy": 15, "conceptual_understanding": 12, "completeness": 14, "clarity_organization": 10, "professional_relevance": 9, "total_score": 60, "justification": "Good response"}'

        judge = MockJudge("mock-model")
        result = judge.judge(
            question="What is systems engineering?",
            expected_answer="A discipline that focuses on system design...",
            response="Systems engineering is about designing complex systems.",
        )

        assert isinstance(result, dict)
        assert "total_score" in result or "scores" in result or "parse_success" in result

    def test_batch_judge(self):
        """Test batch judging."""

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                return '{"technical_accuracy": 15, "conceptual_understanding": 12, "completeness": 14, "clarity_organization": 10, "professional_relevance": 9, "total_score": 60, "justification": "Good response"}'

        judge = MockJudge("mock-model")
        items = [
            {
                "question": "Q1",
                "expected_answer": "A1",
                "response": "R1",
            },
            {
                "question": "Q2",
                "expected_answer": "A2",
                "response": "R2",
            },
        ]

        results = judge.batch_judge(items, progress=False)
        assert len(results) == 2

    def test_custom_settings(self):
        """Test passing custom settings."""

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                return "{}"

        settings = JudgeSettings(temperature=0.9, max_tokens=1000)
        judge = MockJudge("mock-model", settings=settings)

        assert judge.settings.temperature == 0.9
        assert judge.settings.max_tokens == 1000


class TestJudgeCaching:
    """Tests for caching in JudgeBase."""

    def setup_method(self):
        """Reset cache before each test."""
        reset_cache()
        reset_config()

    def _create_mock_judge(self, enable_cache=True, cache_dir=None):
        """Create a mock judge for testing."""
        call_count = {"value": 0}

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                call_count["value"] += 1
                return '{"technical_accuracy": 15, "conceptual_understanding": 12, "completeness": 14, "clarity_organization": 10, "professional_relevance": 9, "total_score": 60, "justification": "Good response"}'

        cache = JudgeCache(cache_dir=cache_dir, enabled=enable_cache) if cache_dir else None
        judge = MockJudge("mock-model", enable_cache=enable_cache, cache=cache)
        return judge, call_count

    def test_caching_enabled_by_default(self):
        """Test that caching is enabled by default."""
        judge, _ = self._create_mock_judge()
        assert judge._cache.enabled is True

    def test_caching_can_be_disabled(self):
        """Test disabling caching."""
        judge, _ = self._create_mock_judge(enable_cache=False)
        assert judge._cache.enabled is False

    def test_cache_hit_avoids_generate(self):
        """Test that cache hit avoids calling _generate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            judge, call_count = self._create_mock_judge(cache_dir=tmpdir)

            # First call - should call _generate
            result1 = judge.judge(
                question="What is SE?",
                expected_answer="A discipline...",
                response="SE is about systems",
            )
            assert call_count["value"] == 1
            assert result1["from_cache"] is False

            # Second call with same inputs - should use cache
            result2 = judge.judge(
                question="What is SE?",
                expected_answer="A discipline...",
                response="SE is about systems",
            )
            assert call_count["value"] == 1  # No additional calls
            assert result2["from_cache"] is True

    def test_cache_miss_for_different_inputs(self):
        """Test that different inputs cause cache miss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            judge, call_count = self._create_mock_judge(cache_dir=tmpdir)

            judge.judge(
                question="What is SE?",
                expected_answer="A",
                response="Response 1",
            )
            assert call_count["value"] == 1

            # Different response - should miss cache
            judge.judge(
                question="What is SE?",
                expected_answer="A",
                response="Response 2",  # Different!
            )
            assert call_count["value"] == 2

    def test_cache_stats(self):
        """Test cache hit/miss statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            judge, _ = self._create_mock_judge(cache_dir=tmpdir)

            # Initial stats
            stats = judge.get_cache_stats()
            assert stats["hits"] == 0
            assert stats["misses"] == 0

            # First call - miss
            judge.judge("Q", "A", "R")
            stats = judge.get_cache_stats()
            assert stats["hits"] == 0
            assert stats["misses"] == 1

            # Second call (same) - hit
            judge.judge("Q", "A", "R")
            stats = judge.get_cache_stats()
            assert stats["hits"] == 1
            assert stats["misses"] == 1

            # Hit rate should be 50%
            assert stats["hit_rate"] == 0.5

    def test_cache_stats_no_tracking_when_disabled(self):
        """Test that stats aren't affected when cache is disabled."""
        judge, _ = self._create_mock_judge(enable_cache=False)

        judge.judge("Q", "A", "R")
        judge.judge("Q", "A", "R")

        stats = judge.get_cache_stats()
        # With cache disabled, we shouldn't track misses
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    def test_use_cache_false_bypasses_cache(self):
        """Test that use_cache=False bypasses cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            judge, call_count = self._create_mock_judge(cache_dir=tmpdir)

            # First call - populate cache
            judge.judge("Q", "A", "R")
            assert call_count["value"] == 1

            # Second call with use_cache=False - should still call _generate
            result = judge.judge("Q", "A", "R", use_cache=False)
            assert call_count["value"] == 2
            assert result["from_cache"] is False


class TestJudgeCheckpointing:
    """Tests for checkpointing in batch_judge."""

    def setup_method(self):
        """Reset cache before each test."""
        reset_cache()
        reset_config()

    def _create_mock_judge(self):
        """Create a mock judge for testing."""

        class MockJudge(JudgeBase):
            def _setup(self, **kwargs):
                pass

            def _generate(self, prompt: str) -> str:
                return '{"total_score": 60, "justification": "Good"}'

        return MockJudge("mock-model", enable_cache=False)

    def test_batch_judge_saves_to_output(self):
        """Test that batch_judge saves results to output path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.jsonl"
            judge = self._create_mock_judge()

            items = [
                {"question_id": "q1", "question": "Q1", "expected_answer": "A1", "response": "R1"},
                {"question_id": "q2", "question": "Q2", "expected_answer": "A2", "response": "R2"},
            ]

            judge.batch_judge(items, progress=False, output_path=output_path)

            assert output_path.exists()

            # Read and verify
            import json
            with open(output_path) as f:
                lines = f.readlines()

            assert len(lines) == 2

    def test_batch_judge_resume(self):
        """Test that batch_judge resumes from checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.jsonl"

            # Simulate previous run by writing a checkpoint
            import json
            with open(output_path, "w") as f:
                f.write(json.dumps({"question_id": "q1", "total_score": 60}) + "\n")

            judge = self._create_mock_judge()

            items = [
                {"question_id": "q1", "question": "Q1", "expected_answer": "A1", "response": "R1"},
                {"question_id": "q2", "question": "Q2", "expected_answer": "A2", "response": "R2"},
                {"question_id": "q3", "question": "Q3", "expected_answer": "A3", "response": "R3"},
            ]

            results = judge.batch_judge(items, progress=False, output_path=output_path, resume=True)

            # Only q2 and q3 should be processed (q1 was in checkpoint)
            assert len(results) == 2
            result_ids = [r["question_id"] for r in results]
            assert "q2" in result_ids
            assert "q3" in result_ids
            assert "q1" not in result_ids

    def test_batch_judge_no_resume(self):
        """Test that batch_judge starts fresh with resume=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.jsonl"

            # Simulate previous run
            import json
            with open(output_path, "w") as f:
                f.write(json.dumps({"question_id": "q1", "total_score": 60}) + "\n")

            judge = self._create_mock_judge()

            items = [
                {"question_id": "q1", "question": "Q1", "expected_answer": "A1", "response": "R1"},
                {"question_id": "q2", "question": "Q2", "expected_answer": "A2", "response": "R2"},
            ]

            results = judge.batch_judge(items, progress=False, output_path=output_path, resume=False)

            # All items should be processed (previous checkpoint cleared)
            assert len(results) == 2

    def test_batch_judge_handles_missing_question_id(self):
        """Test that items without question_id are processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results.jsonl"

            # Create checkpoint with one item
            import json
            with open(output_path, "w") as f:
                f.write(json.dumps({"question_id": "q1", "total_score": 60}) + "\n")

            judge = self._create_mock_judge()

            # Items without question_id should NOT be skipped
            items = [
                {"question": "Q1", "expected_answer": "A1", "response": "R1"},  # No question_id
                {"question": "Q2", "expected_answer": "A2", "response": "R2"},  # No question_id
            ]

            results = judge.batch_judge(items, progress=False, output_path=output_path, resume=True)

            # Both items should be processed since they don't have question_ids
            assert len(results) == 2

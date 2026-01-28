"""Tests for judge base classes."""

import pytest

from metaeval.judges.base import JudgeSettings, JudgeBase
from metaeval.core.config import get_config, reset_config


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

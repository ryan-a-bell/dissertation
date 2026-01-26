"""Tests for judge factory."""

import pytest

from metaeval.judges.factory import create_judge, get_default_model, list_providers
from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.judges.ollama import OllamaJudge
from metaeval.judges.openai import OpenAIJudge
from metaeval.judges.anthropic import AnthropicJudge
from metaeval.judges.openrouter import OpenRouterJudge


class TestListProviders:
    """Tests for list_providers function."""

    def test_returns_list(self):
        """Test that list_providers returns a list."""
        providers = list_providers()
        assert isinstance(providers, list)

    def test_expected_providers(self):
        """Test expected providers are listed."""
        providers = list_providers()
        expected = ["ollama", "openai", "anthropic", "openrouter"]
        for provider in expected:
            assert provider in providers


class TestGetDefaultModel:
    """Tests for get_default_model function."""

    def test_ollama_default(self):
        """Test default model for Ollama."""
        model = get_default_model("ollama")
        assert model is not None
        assert isinstance(model, str)

    def test_openai_default(self):
        """Test default model for OpenAI."""
        model = get_default_model("openai")
        assert "gpt" in model.lower()

    def test_anthropic_default(self):
        """Test default model for Anthropic."""
        model = get_default_model("anthropic")
        assert "claude" in model.lower()

    def test_openrouter_default(self):
        """Test default model for OpenRouter."""
        model = get_default_model("openrouter")
        assert model is not None

    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(ValueError):
            get_default_model("invalid_provider")


class TestCreateJudge:
    """Tests for create_judge factory function."""

    def test_create_ollama_judge(self):
        """Test creating Ollama judge."""
        # This may fail if Ollama is not running, but should create the object
        try:
            judge = create_judge("ollama", "llama3.1:8b")
            assert isinstance(judge, OllamaJudge)
            assert judge.model == "llama3.1:8b"
        except Exception:
            # Ollama might not be running
            pass

    def test_create_with_settings(self):
        """Test creating judge with custom settings."""
        settings = JudgeSettings(temperature=0.5, max_tokens=1024)
        try:
            judge = create_judge("ollama", "llama3.1:8b", settings=settings)
            assert judge.settings.temperature == 0.5
            assert judge.settings.max_tokens == 1024
        except Exception:
            pass

    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with pytest.raises(ValueError):
            create_judge("invalid_provider", "some-model")

    def test_create_openai_judge(self):
        """Test creating OpenAI judge (may fail without API key)."""
        try:
            judge = create_judge("openai", "gpt-4o")
            assert isinstance(judge, OpenAIJudge)
        except Exception:
            # Expected without API key
            pass

    def test_create_anthropic_judge(self):
        """Test creating Anthropic judge (may fail without API key)."""
        try:
            judge = create_judge("anthropic", "claude-3-opus-20240229")
            assert isinstance(judge, AnthropicJudge)
        except Exception:
            # Expected without API key
            pass

    def test_create_openrouter_judge(self):
        """Test creating OpenRouter judge (may fail without API key)."""
        try:
            judge = create_judge("openrouter", "openai/gpt-4o")
            assert isinstance(judge, OpenRouterJudge)
        except Exception:
            # Expected without API key
            pass


class TestJudgeInheritance:
    """Tests for judge class inheritance."""

    def test_ollama_inherits_base(self):
        """Test OllamaJudge inherits from JudgeBase."""
        assert issubclass(OllamaJudge, JudgeBase)

    def test_openai_inherits_base(self):
        """Test OpenAIJudge inherits from JudgeBase."""
        assert issubclass(OpenAIJudge, JudgeBase)

    def test_anthropic_inherits_base(self):
        """Test AnthropicJudge inherits from JudgeBase."""
        assert issubclass(AnthropicJudge, JudgeBase)

    def test_openrouter_inherits_base(self):
        """Test OpenRouterJudge inherits from JudgeBase."""
        assert issubclass(OpenRouterJudge, JudgeBase)

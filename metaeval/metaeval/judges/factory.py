"""Factory for creating judge instances."""

from __future__ import annotations

from typing import Literal, Any

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.core.logging import get_logger

logger = get_logger(__name__)

Provider = Literal["ollama", "openai", "anthropic", "openrouter"]


def create_judge(
    provider: Provider,
    model: str,
    settings: JudgeSettings | None = None,
    **kwargs: Any,
) -> JudgeBase:
    """
    Create a judge instance for the specified provider.

    Args:
        provider: Provider name ("ollama", "openai", "anthropic", "openrouter")
        model: Model identifier
        settings: Optional judge settings
        **kwargs: Provider-specific arguments

    Returns:
        JudgeBase instance

    Examples:
        >>> judge = create_judge("ollama", "llama3.1:8b")
        >>> judge = create_judge("openai", "gpt-4o")
        >>> judge = create_judge("anthropic", "claude-3-5-sonnet-20241022")
        >>> judge = create_judge("openrouter", "meta-llama/llama-3.1-70b-instruct")

    Raises:
        ValueError: If provider is unknown
    """
    if provider == "ollama":
        from metaeval.judges.ollama import OllamaJudge
        return OllamaJudge(model=model, settings=settings, **kwargs)

    elif provider == "openai":
        from metaeval.judges.openai import OpenAIJudge
        return OpenAIJudge(model=model, settings=settings, **kwargs)

    elif provider == "anthropic":
        from metaeval.judges.anthropic import AnthropicJudge
        return AnthropicJudge(model=model, settings=settings, **kwargs)

    elif provider == "openrouter":
        from metaeval.judges.openrouter import OpenRouterJudge
        return OpenRouterJudge(model=model, settings=settings, **kwargs)

    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Available providers: ollama, openai, anthropic, openrouter"
        )


def get_default_model(provider: Provider) -> str:
    """
    Get the default model for a provider.

    Args:
        provider: Provider name

    Returns:
        Default model identifier
    """
    defaults = {
        "ollama": "llama3.1:8b",
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "openrouter": "anthropic/claude-3.5-sonnet",
    }
    return defaults.get(provider, "")


def list_providers() -> list[str]:
    """List available providers."""
    return ["ollama", "openai", "anthropic", "openrouter"]

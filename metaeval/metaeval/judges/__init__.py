"""
LLM-as-a-Judge implementations for multiple providers.

This module provides judge classes for evaluating LLM responses using various providers:
- OllamaJudge: Local models via Ollama
- OpenAIJudge: OpenAI API (GPT-4o, etc.)
- AnthropicJudge: Anthropic API (Claude, etc.)
- OpenRouterJudge: Multi-provider via OpenRouter

Usage:
    from metaeval.judges import create_judge, JudgeSettings

    # Using factory (recommended)
    judge = create_judge("openai", "gpt-4o")
    result = judge.judge(question, expected_answer, response)

    # Direct instantiation with custom settings
    settings = JudgeSettings(temperature=0.1, prompt_style="chain_of_thought")
    judge = OpenAIJudge("gpt-4o", settings=settings)

    # Batch judging
    results = judge.batch_judge(items, progress=True)
"""

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.judges.ollama import OllamaJudge
from metaeval.judges.openai import OpenAIJudge
from metaeval.judges.anthropic import AnthropicJudge
from metaeval.judges.openrouter import OpenRouterJudge
from metaeval.judges.factory import create_judge, get_default_model, list_providers

__all__ = [
    # Base
    "JudgeBase",
    "JudgeSettings",
    # Providers
    "OllamaJudge",
    "OpenAIJudge",
    "AnthropicJudge",
    "OpenRouterJudge",
    # Factory
    "create_judge",
    "get_default_model",
    "list_providers",
]

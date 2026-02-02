"""OpenRouter-based LLM judge (multi-provider)."""

from __future__ import annotations

from typing import Any

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.core.config import get_config
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class OpenRouterJudge(JudgeBase):
    """
    LLM-as-a-Judge using OpenRouter API.

    OpenRouter provides unified access to multiple LLM providers.
    Model names use format: provider/model-name
    Examples:
        - anthropic/claude-3.5-sonnet
        - meta-llama/llama-3.1-70b-instruct
        - openai/gpt-4o
        - google/gemini-pro-1.5
    """

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        model: str = "anthropic/claude-3.5-sonnet",
        settings: JudgeSettings | None = None,
        api_key: str | None = None,
        site_url: str | None = None,
        site_name: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize OpenRouter judge.

        Args:
            model: OpenRouter model path (e.g., "anthropic/claude-3.5-sonnet")
            settings: Judge settings
            api_key: OpenRouter API key (default from config/env)
            site_url: Optional site URL for rankings
            site_name: Optional site name for rankings
            **kwargs: Additional arguments passed to JudgeBase (e.g., enable_cache)
        """
        config = get_config()
        self.api_key = api_key or config.api.openrouter_api_key

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.site_url = site_url
        self.site_name = site_name or "metaeval"

        super().__init__(model, settings, **kwargs)

    def _setup(self, **kwargs: Any) -> None:
        """Initialize OpenAI-compatible client for OpenRouter."""
        from openai import OpenAI

        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.OPENROUTER_BASE_URL,
        )
        logger.debug(f"Initialized OpenRouter judge with model: {self.model}")

    def _generate(self, prompt: str) -> str:
        """Generate response using OpenRouter."""
        extra_headers = {
            "HTTP-Referer": self.site_url or "https://github.com/metaeval",
            "X-Title": self.site_name,
        }

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            extra_headers=extra_headers,
        )

        return response.choices[0].message.content or ""

    def list_models(self) -> list[str]:
        """List popular available models."""
        return [
            # Anthropic
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3.5-haiku",
            "anthropic/claude-3-opus",
            # OpenAI
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "openai/gpt-4-turbo",
            # Meta
            "meta-llama/llama-3.1-405b-instruct",
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct",
            # Google
            "google/gemini-pro-1.5",
            "google/gemini-flash-1.5",
            # Mistral
            "mistralai/mistral-large",
            "mistralai/mixtral-8x22b-instruct",
            # DeepSeek
            "deepseek/deepseek-chat",
            # Qwen
            "qwen/qwen-2.5-72b-instruct",
        ]

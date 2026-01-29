"""Anthropic-based LLM judge."""

from __future__ import annotations

from typing import Any

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.core.config import get_config
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class AnthropicJudge(JudgeBase):
    """LLM-as-a-Judge using Anthropic API."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        settings: JudgeSettings | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize Anthropic judge.

        Args:
            model: Anthropic model name (e.g., "claude-3-5-sonnet-20241022")
            settings: Judge settings
            api_key: Anthropic API key (default from config/env)
            **kwargs: Additional arguments passed to JudgeBase (e.g., enable_cache)
        """
        config = get_config()
        self.api_key = api_key or config.api.anthropic_api_key

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        super().__init__(model, settings, **kwargs)

    def _setup(self, **kwargs: Any) -> None:
        """Initialize Anthropic client."""
        import anthropic
        self._client = anthropic.Anthropic(api_key=self.api_key)
        logger.debug(f"Initialized Anthropic judge with model: {self.model}")

    def _generate(self, prompt: str) -> str:
        """Generate response using Anthropic."""
        message = self._client.messages.create(
            model=self.model,
            max_tokens=self.settings.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.settings.temperature,
        )

        # Extract text from response
        if message.content and len(message.content) > 0:
            return message.content[0].text
        return ""

    def list_models(self) -> list[str]:
        """List available models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

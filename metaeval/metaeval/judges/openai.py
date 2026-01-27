"""OpenAI-based LLM judge."""

from __future__ import annotations

from typing import Any

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.core.config import get_config
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIJudge(JudgeBase):
    """LLM-as-a-Judge using OpenAI API."""

    def __init__(
        self,
        model: str = "gpt-4o",
        settings: JudgeSettings | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize OpenAI judge.

        Args:
            model: OpenAI model name (e.g., "gpt-4o", "gpt-4o-mini")
            settings: Judge settings
            api_key: OpenAI API key (default from config/env)
        """
        config = get_config()
        self.api_key = api_key or config.api.openai_api_key

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        super().__init__(model, settings)

    def _setup(self, **kwargs: Any) -> None:
        """Initialize OpenAI client."""
        from openai import OpenAI
        self._client = OpenAI(api_key=self.api_key)
        logger.debug(f"Initialized OpenAI judge with model: {self.model}")

    def _generate(self, prompt: str) -> str:
        """Generate response using OpenAI."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            timeout=self.settings.timeout,
        )

        return response.choices[0].message.content or ""

    def list_models(self) -> list[str]:
        """List available models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

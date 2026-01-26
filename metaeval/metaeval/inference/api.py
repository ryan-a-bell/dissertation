"""API-based model execution."""

from __future__ import annotations

import time
from typing import Any, Generator, Literal

from metaeval.inference.base import ExecutorBase, StreamingExecutorMixin
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class APIExecutor(ExecutorBase, StreamingExecutorMixin):
    """Execute models via provider APIs (OpenAI, Anthropic, Google)."""

    def __init__(
        self,
        model: str,
        provider: Literal["openai", "anthropic", "google", "openrouter"] = "openai",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 300,
        system_prompt: str | None = None,
    ):
        """
        Initialize API executor.

        Args:
            model: Model identifier
            provider: API provider
            api_key: API key (or from environment)
            base_url: Optional custom base URL
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            system_prompt: Optional system prompt
        """
        super().__init__(model, temperature, max_tokens, timeout)
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.system_prompt = system_prompt
        self._client = None

    def setup(self) -> None:
        """Set up API client."""
        if self.provider == "openai" or self.provider == "openrouter":
            from openai import OpenAI

            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            elif self.provider == "openrouter":
                kwargs["base_url"] = "https://openrouter.ai/api/v1"

            self._client = OpenAI(**kwargs)

        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic

                kwargs = {}
                if self.api_key:
                    kwargs["api_key"] = self.api_key

                self._client = Anthropic(**kwargs)
            except ImportError:
                raise ImportError("anthropic package required for Anthropic provider")

        elif self.provider == "google":
            try:
                import google.generativeai as genai

                if self.api_key:
                    genai.configure(api_key=self.api_key)

                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package required for Google provider")

        self._is_setup = True
        logger.info(f"API executor set up for {self.provider}/{self.model}")

    def teardown(self) -> None:
        """Clean up API client."""
        self._client = None
        self._is_setup = False

    def generate(self, prompt: str) -> str:
        """Generate a response using the API."""
        if not self._is_setup:
            self.setup()

        if self.provider in ("openai", "openrouter"):
            return self._generate_openai(prompt)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt)
        elif self.provider == "google":
            return self._generate_google(prompt)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI-compatible API."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )

        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic API."""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        if self.system_prompt:
            kwargs["system"] = self.system_prompt

        response = self._client.messages.create(**kwargs)

        return response.content[0].text

    def _generate_google(self, prompt: str) -> str:
        """Generate using Google Generative AI."""
        response = self._client.generate_content(
            prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            },
        )

        return response.text

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """Generate with streaming (OpenAI only for now)."""
        if not self._is_setup:
            self.setup()

        if self.provider not in ("openai", "openrouter"):
            # Fall back to non-streaming
            yield self.generate(prompt)
            return

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def generate_with_json(self, prompt: str) -> dict[str, Any]:
        """Generate with JSON response format (OpenAI only)."""
        if not self._is_setup:
            self.setup()

        if self.provider not in ("openai", "openrouter"):
            # Parse JSON from regular response
            import json
            response = self.generate(prompt)
            return json.loads(response)

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )

        import json
        return json.loads(response.choices[0].message.content)


class MultiProviderExecutor:
    """Execute across multiple providers with fallback."""

    def __init__(
        self,
        executors: list[APIExecutor],
        retry_delay: float = 1.0,
    ):
        """
        Initialize multi-provider executor.

        Args:
            executors: List of API executors in priority order
            retry_delay: Delay between retries in seconds
        """
        self.executors = executors
        self.retry_delay = retry_delay

    def generate(self, prompt: str) -> str:
        """
        Generate using first available provider.

        Args:
            prompt: Input prompt

        Returns:
            Generated response
        """
        last_error = None

        for executor in self.executors:
            try:
                return executor.generate(prompt)
            except Exception as e:
                logger.warning(f"Provider {executor.provider} failed: {e}")
                last_error = e
                time.sleep(self.retry_delay)

        raise RuntimeError(f"All providers failed. Last error: {last_error}")

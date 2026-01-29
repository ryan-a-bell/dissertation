"""Ollama-based LLM judge."""

from __future__ import annotations

import json
from typing import Any

import requests

from metaeval.judges.base import JudgeBase, JudgeSettings
from metaeval.core.config import get_config
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class OllamaJudge(JudgeBase):
    """LLM-as-a-Judge using local Ollama."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        settings: JudgeSettings | None = None,
        host: str | None = None,
        port: int | None = None,
        auto_pull: bool | None = None,
        **kwargs: Any,
    ):
        """
        Initialize Ollama judge.

        Args:
            model: Ollama model name (e.g., "llama3.1:8b", "mistral:7b")
            settings: Judge settings
            host: Ollama host (default from config)
            port: Ollama port (default from config)
            auto_pull: Whether to auto-pull missing models
            **kwargs: Additional arguments passed to JudgeBase (e.g., enable_cache)
        """
        config = get_config()
        self.host = host or config.ollama.host
        self.port = port or config.ollama.port
        self.auto_pull = auto_pull if auto_pull is not None else config.ollama.auto_pull
        self._base_url = f"http://{self.host}:{self.port}"

        super().__init__(model, settings, **kwargs)

    def _setup(self, **kwargs: Any) -> None:
        """Verify Ollama is running and model is available."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not connect to Ollama at {self._base_url}: {e}")
            return

        # Check if model is available
        models = response.json().get("models", [])
        model_names = [m.get("name", "").split(":")[0] for m in models]

        if self.model.split(":")[0] not in model_names:
            if self.auto_pull:
                logger.info(f"Model {self.model} not found, pulling...")
                self._pull_model()
            else:
                logger.warning(f"Model {self.model} not available locally")

    def _pull_model(self) -> None:
        """Pull model from Ollama registry."""
        try:
            response = requests.post(
                f"{self._base_url}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=600,
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get("status", "")
                    if "pulling" in status.lower() or "downloading" in status.lower():
                        logger.info(f"Pulling {self.model}: {status}")

        except Exception as e:
            logger.error(f"Failed to pull model {self.model}: {e}")

    def _generate(self, prompt: str) -> str:
        """Generate response using Ollama."""
        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.settings.temperature,
                    "num_predict": self.settings.max_tokens,
                },
            },
            timeout=self.settings.timeout,
        )

        response.raise_for_status()
        return response.json().get("response", "")

    def list_models(self) -> list[str]:
        """List available local models."""
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            models = response.json().get("models", [])
            return [m.get("name", "") for m in models]
        except Exception:
            return []

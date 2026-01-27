"""Local model execution via Ollama."""

from __future__ import annotations

import json
import subprocess
import time
from typing import Any, Generator

import requests

from metaeval.inference.base import ExecutorBase, StreamingExecutorMixin
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


class LocalExecutor(ExecutorBase, StreamingExecutorMixin):
    """Execute models locally via Ollama."""

    def __init__(
        self,
        model: str,
        host: str = "localhost",
        port: int = 11434,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 300,
        auto_pull: bool = True,
    ):
        """
        Initialize local executor.

        Args:
            model: Ollama model name
            host: Ollama host
            port: Ollama port
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            auto_pull: Whether to auto-pull missing models
        """
        super().__init__(model, temperature, max_tokens, timeout)
        self.host = host
        self.port = port
        self.auto_pull = auto_pull
        self._base_url = f"http://{host}:{port}"

    def setup(self) -> None:
        """Verify Ollama is running and model is available."""
        # Check if Ollama is running
        try:
            response = requests.get(f"{self._base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            # Try to start Ollama
            logger.info("Ollama not running, attempting to start...")
            try:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(5)
            except FileNotFoundError:
                raise RuntimeError("Ollama not installed. Install from https://ollama.com")

        # Check if model is available
        response = requests.get(f"{self._base_url}/api/tags")
        models = response.json().get("models", [])
        model_names = [m.get("name", "").split(":")[0] for m in models]

        if self.model.split(":")[0] not in model_names:
            if self.auto_pull:
                logger.info(f"Pulling model: {self.model}")
                self._pull_model()
            else:
                raise RuntimeError(f"Model {self.model} not available")

        self._is_setup = True
        logger.info(f"Local executor ready with model: {self.model}")

    def _pull_model(self) -> None:
        """Pull a model from Ollama registry."""
        response = requests.post(
            f"{self._base_url}/api/pull",
            json={"name": self.model},
            stream=True,
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                status = data.get("status", "")
                if "pulling" in status.lower():
                    logger.info(f"Pulling: {status}")

    def teardown(self) -> None:
        """Clean up (no-op for local executor)."""
        self._is_setup = False

    def generate(self, prompt: str) -> str:
        """Generate a response using Ollama."""
        if not self._is_setup:
            self.setup()

        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json().get("response", "")

    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """Generate with streaming."""
        if not self._is_setup:
            self.setup()

        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            },
            stream=True,
            timeout=self.timeout,
        )

        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]

    def chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
    ) -> str:
        """
        Chat completion with message history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt

        Returns:
            Assistant response
        """
        if not self._is_setup:
            self.setup()

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self._base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")

    def list_models(self) -> list[dict[str, Any]]:
        """List available local models."""
        response = requests.get(f"{self._base_url}/api/tags")
        return response.json().get("models", [])

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the current model."""
        response = requests.post(
            f"{self._base_url}/api/show",
            json={"name": self.model},
        )
        return response.json()


class OllamaJudge:
    """Specialized executor for LLM-as-a-Judge using Ollama."""

    def __init__(
        self,
        model: str = "llama3.1:8b",
        temperature: float = 0.0,
        host: str = "localhost",
        port: int = 11434,
        prompt_style: str = "multi_dimensional",
    ):
        """
        Initialize Ollama judge.

        Args:
            model: Ollama model for judging
            temperature: Generation temperature
            host: Ollama host
            port: Ollama port
            prompt_style: Name of judge prompt from registry
        """
        self.executor = LocalExecutor(
            model=model,
            host=host,
            port=port,
            temperature=temperature,
            max_tokens=2048,
        )
        self.prompt_style = prompt_style

    def judge(
        self,
        question: str,
        expected_answer: str,
        response: str,
        rubric: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Judge a response.

        Args:
            question: The question
            expected_answer: Expected answer
            response: Response to judge
            rubric: Optional grading rubric

        Returns:
            Judgment with scores
        """
        from metaeval.judge.prompts import build_judge_prompt
        from metaeval.judge.scorer import parse_judgment

        prompt = build_judge_prompt(
            question=question,
            expected_answer=expected_answer,
            response=response,
            rubric=rubric,
            prompt_style=self.prompt_style,
        )

        raw_judgment = self.executor.generate(prompt)
        parsed = parse_judgment(raw_judgment)

        return parsed.to_dict()

    def batch_judge(
        self,
        items: list[dict[str, Any]],
        progress: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Judge multiple items.

        Args:
            items: List of dicts with question, expected_answer, response
            progress: Whether to show progress

        Returns:
            List of judgments
        """
        from tqdm import tqdm

        results = []
        iterator = tqdm(items, disable=not progress, desc="Judging")

        for item in iterator:
            judgment = self.judge(
                question=item["question"],
                expected_answer=item["expected_answer"],
                response=item["response"],
                rubric=item.get("rubric"),
            )
            results.append(judgment)

        return results

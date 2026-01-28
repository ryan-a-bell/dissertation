"""Base classes for model execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generator

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class InferenceResult:
    """Result from model inference."""

    question_id: int
    prompt: str
    response: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "prompt": self.prompt,
            "response": self.response,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
        }


class ExecutorBase(ABC):
    """Abstract base class for model execution environments."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        timeout: int = 300,
    ):
        """
        Initialize executor.

        Args:
            model: Model identifier
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._is_setup = False

    @abstractmethod
    def setup(self) -> None:
        """Set up the execution environment."""
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Clean up the execution environment."""
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response for a single prompt.

        Args:
            prompt: Input prompt

        Returns:
            Generated response string
        """
        pass

    def batch_generate(
        self,
        prompts: list[str],
        progress: bool = True,
    ) -> list[str]:
        """
        Generate responses for multiple prompts.

        Args:
            prompts: List of input prompts
            progress: Whether to show progress

        Returns:
            List of generated responses
        """
        from tqdm import tqdm

        responses = []
        iterator = tqdm(prompts, disable=not progress, desc="Generating")

        for prompt in iterator:
            response = self.generate(prompt)
            responses.append(response)

        return responses

    def run_inference(
        self,
        samples: list[dict[str, Any]],
        prompt_key: str = "prompt",
        id_key: str = "question_id",
        progress: bool = True,
    ) -> list[InferenceResult]:
        """
        Run inference on a list of samples.

        Args:
            samples: List of sample dictionaries
            prompt_key: Key for prompt in sample dict
            id_key: Key for question ID in sample dict
            progress: Whether to show progress

        Returns:
            List of InferenceResult objects
        """
        import time
        from tqdm import tqdm

        results = []
        iterator = tqdm(samples, disable=not progress, desc="Inference")

        for sample in iterator:
            prompt = sample[prompt_key]
            question_id = sample.get(id_key, len(results))

            start_time = time.time()
            response = self.generate(prompt)
            latency = (time.time() - start_time) * 1000

            results.append(InferenceResult(
                question_id=question_id,
                prompt=prompt,
                response=response,
                model=self.model,
                latency_ms=latency,
                metadata={"sample": sample},
            ))

        return results

    def __enter__(self) -> "ExecutorBase":
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.teardown()


class StreamingExecutorMixin:
    """Mixin for executors that support streaming."""

    @abstractmethod
    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """
        Generate a response with streaming.

        Args:
            prompt: Input prompt

        Yields:
            Response chunks
        """
        pass


class BatchExecutorMixin:
    """Mixin for executors that support native batching."""

    @abstractmethod
    def generate_batch(
        self,
        prompts: list[str],
        batch_size: int = 10,
    ) -> list[str]:
        """
        Generate responses in batches.

        Args:
            prompts: List of input prompts
            batch_size: Batch size for processing

        Returns:
            List of generated responses
        """
        pass

"""Base class for LLM-as-a-Judge implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from tqdm import tqdm

from metaeval.core.logging import get_logger
from metaeval.core.config import get_config, JudgeConfig

logger = get_logger(__name__)


@dataclass
class JudgeSettings:
    """Runtime settings for a judge instance."""

    temperature: float = 0.0
    max_tokens: int = 2048
    timeout: int = 300
    prompt_style: str = "multi_dimensional"

    @classmethod
    def from_config(cls, config: JudgeConfig | None = None) -> "JudgeSettings":
        """Create settings from config."""
        if config is None:
            config = get_config().judge
        return cls(
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            prompt_style=config.default_prompt,
        )


class JudgeBase(ABC):
    """Abstract base class for LLM judges."""

    def __init__(
        self,
        model: str,
        settings: JudgeSettings | None = None,
        **kwargs: Any,
    ):
        """
        Initialize judge.

        Args:
            model: Model identifier
            settings: Judge settings (uses config defaults if None)
            **kwargs: Additional provider-specific arguments
        """
        self.model = model
        self.settings = settings or JudgeSettings.from_config()
        self._setup(**kwargs)

    def _setup(self, **kwargs: Any) -> None:
        """Provider-specific setup. Override in subclasses."""
        pass

    @abstractmethod
    def _generate(self, prompt: str) -> str:
        """
        Generate a response from the model.

        Args:
            prompt: The prompt to send

        Returns:
            Model response text
        """
        ...

    def judge(
        self,
        question: str,
        expected_answer: str,
        response: str,
        rubric: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Judge a single response.

        Args:
            question: The question
            expected_answer: Expected/model answer
            response: Response to evaluate
            rubric: Optional grading rubric

        Returns:
            Judgment result dictionary
        """
        from metaeval.judge.prompts import build_judge_prompt
        from metaeval.judge.scorer import parse_judgment

        prompt = build_judge_prompt(
            question=question,
            expected_answer=expected_answer,
            response=response,
            rubric=rubric,
            prompt_style=self.settings.prompt_style,
        )

        raw_judgment = self._generate(prompt)
        parsed = parse_judgment(raw_judgment)

        result = parsed.to_dict()
        result["judge_model"] = self.model
        result["prompt_style"] = self.settings.prompt_style

        return result

    def batch_judge(
        self,
        items: list[dict[str, Any]],
        progress: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Judge multiple items.

        Args:
            items: List of dicts with question, expected_answer, response
            progress: Whether to show progress bar

        Returns:
            List of judgment results
        """
        results = []
        iterator = tqdm(items, disable=not progress, desc=f"Judging with {self.model}")

        for item in iterator:
            try:
                judgment = self.judge(
                    question=item["question"],
                    expected_answer=item["expected_answer"],
                    response=item["response"],
                    rubric=item.get("rubric"),
                )
                judgment["question_id"] = item.get("question_id")
                results.append(judgment)
            except Exception as e:
                logger.warning(f"Failed to judge item {item.get('question_id')}: {e}")
                results.append({
                    "question_id": item.get("question_id"),
                    "error": str(e),
                    "judge_model": self.model,
                })

        return results

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"

"""Base class for LLM-as-a-Judge implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tqdm import tqdm

from metaeval.core.logging import get_logger
from metaeval.core.config import get_config, JudgeConfig
from metaeval.core.cache import JudgeCache, get_cache
from metaeval.core.progress import CheckpointManager, BatchProgress

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
        cache: JudgeCache | None = None,
        enable_cache: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize judge.

        Args:
            model: Model identifier
            settings: Judge settings (uses config defaults if None)
            cache: Optional cache instance (uses global cache if None)
            enable_cache: Whether to enable response caching
            **kwargs: Additional provider-specific arguments
        """
        self.model = model
        self.settings = settings or JudgeSettings.from_config()
        self._cache = cache if cache is not None else get_cache()
        self._cache.enabled = enable_cache
        self._cache_hits = 0
        self._cache_misses = 0
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
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Judge a single response.

        Args:
            question: The question
            expected_answer: Expected/model answer
            response: Response to evaluate
            rubric: Optional grading rubric
            use_cache: Whether to use cache for this judgment

        Returns:
            Judgment result dictionary
        """
        from metaeval.judge.prompts import build_judge_prompt
        from metaeval.judge.scorer import parse_judgment

        # Check cache first
        if use_cache and self._cache.enabled:
            cached = self._cache.get(
                model=self.model,
                question=question,
                response=response,
                prompt_style=self.settings.prompt_style,
            )
            if cached is not None:
                self._cache_hits += 1
                cached["from_cache"] = True
                return cached

        self._cache_misses += 1

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
        result["from_cache"] = False

        # Store in cache
        if use_cache and self._cache.enabled:
            self._cache.put(
                model=self.model,
                question=question,
                response=response,
                prompt_style=self.settings.prompt_style,
                judgment=result,
            )

        return result

    def batch_judge(
        self,
        items: list[dict[str, Any]],
        progress: bool = True,
        output_path: Path | str | None = None,
        resume: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Judge multiple items with optional checkpointing for resumability.

        Args:
            items: List of dicts with question, expected_answer, response
            progress: Whether to show progress bar
            output_path: Optional path for JSONL output (enables checkpointing)
            resume: Whether to resume from existing checkpoint (if output_path exists)

        Returns:
            List of judgment results
        """
        # Set up checkpointing if output path provided
        checkpoint: CheckpointManager | None = None
        completed_ids: set[str] = set()

        if output_path is not None:
            output_path = Path(output_path)
            checkpoint = CheckpointManager(output_path)

            if resume:
                completed_ids = checkpoint.load_completed_ids()
            else:
                checkpoint.clear()

        # Filter items if resuming
        items_to_process = []
        skipped_count = 0

        for item in items:
            question_id = str(item.get("question_id", ""))
            if question_id in completed_ids:
                skipped_count += 1
            else:
                items_to_process.append(item)

        total = len(items)
        cached_count = 0

        # Build progress description
        desc = f"Judging with {self.model}"
        if skipped_count > 0:
            desc += f" ({skipped_count} resumed)"

        iterator = tqdm(
            items_to_process,
            disable=not progress,
            desc=desc,
            total=len(items_to_process),
        )

        results = []

        for item in iterator:
            try:
                judgment = self.judge(
                    question=item["question"],
                    expected_answer=item["expected_answer"],
                    response=item["response"],
                    rubric=item.get("rubric"),
                )
                judgment["question_id"] = item.get("question_id")

                if judgment.get("from_cache"):
                    cached_count += 1

                results.append(judgment)

                # Save to checkpoint
                if checkpoint is not None:
                    checkpoint.save_result(judgment)

                # Update progress bar postfix
                if progress and cached_count > 0:
                    iterator.set_postfix(cached=cached_count)

            except Exception as e:
                logger.warning(f"Failed to judge item {item.get('question_id')}: {e}")
                error_result = {
                    "question_id": item.get("question_id"),
                    "error": str(e),
                    "judge_model": self.model,
                }
                results.append(error_result)

                if checkpoint is not None:
                    checkpoint.save_result(error_result)

        # Log summary
        logger.info(
            f"Batch complete: {len(results)} processed, "
            f"{skipped_count} resumed, {cached_count} from cache"
        )

        return results

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache hit/miss statistics for this judge instance."""
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": (
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"

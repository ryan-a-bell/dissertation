"""MCQ result parsing utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class MCQResult:
    """Parsed MCQ result for a single question."""

    question_id: int
    question: str
    choices: dict[str, str]
    correct_answer: str
    model_answer: str
    is_correct: bool
    model: str
    benchmark_variant: str = ""
    logprobs: dict[str, float] | None = None
    raw_response: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "choices": self.choices,
            "correct_answer": self.correct_answer,
            "model_answer": self.model_answer,
            "is_correct": self.is_correct,
            "model": self.model,
            "benchmark_variant": self.benchmark_variant,
            "logprobs": self.logprobs,
        }


def parse_mcq_samples(
    samples: list[dict[str, Any]],
    model: str,
    benchmark_variant: str = "",
) -> list[MCQResult]:
    """
    Parse MCQ samples from lm-eval output format.

    Args:
        samples: List of sample dictionaries from lm-eval
        model: Model name
        benchmark_variant: Benchmark variant identifier (e.g., "A", "B", "C", "D")

    Returns:
        List of MCQResult objects
    """
    results = []

    for idx, sample in enumerate(samples):
        # Extract document data
        doc = sample.get("doc", {})

        # Get question and choices
        question = doc.get("question", "")
        choices = {
            "A": doc.get("choice_a", ""),
            "B": doc.get("choice_b", ""),
            "C": doc.get("choice_c", ""),
            "D": doc.get("choice_d", ""),
        }

        # Get correct answer
        correct_answer = doc.get("answer", "")

        # Get model answer from filtered_resps or acc
        model_answer = ""
        if "filtered_resps" in sample:
            resps = sample["filtered_resps"]
            if isinstance(resps, list) and len(resps) > 0:
                # Find the choice with highest logprob
                if isinstance(resps[0], (list, tuple)):
                    # Format: [[logprob, is_correct], ...]
                    max_idx = max(range(len(resps)), key=lambda i: resps[i][0])
                    model_answer = ["A", "B", "C", "D"][max_idx]
                else:
                    model_answer = str(resps[0])

        # Determine if correct
        is_correct = sample.get("acc", 0) == 1 or model_answer == correct_answer

        # Extract logprobs if available
        logprobs = None
        if "resps" in sample:
            resps = sample["resps"]
            if isinstance(resps, list) and len(resps) == 4:
                logprobs = {
                    "A": resps[0][0] if isinstance(resps[0], (list, tuple)) else resps[0],
                    "B": resps[1][0] if isinstance(resps[1], (list, tuple)) else resps[1],
                    "C": resps[2][0] if isinstance(resps[2], (list, tuple)) else resps[2],
                    "D": resps[3][0] if isinstance(resps[3], (list, tuple)) else resps[3],
                }

        results.append(MCQResult(
            question_id=doc.get("question_id", idx),
            question=question,
            choices=choices,
            correct_answer=correct_answer,
            model_answer=model_answer,
            is_correct=is_correct,
            model=model,
            benchmark_variant=benchmark_variant,
            logprobs=logprobs,
        ))

    return results


def parse_mcq_results(
    results_path: Path | str,
    samples_path: Path | str | None = None,
    model: str | None = None,
    benchmark_variant: str = "",
) -> tuple[dict[str, Any], list[MCQResult]]:
    """
    Parse MCQ results from lm-eval output files.

    Args:
        results_path: Path to results.json
        samples_path: Path to samples JSONL file (optional)
        model: Model name (inferred from path if not provided)
        benchmark_variant: Benchmark variant identifier

    Returns:
        Tuple of (aggregated results dict, list of MCQResult)
    """
    results_path = Path(results_path)

    # Load aggregated results
    with open(results_path) as f:
        agg_results = json.load(f)

    # Infer model name if not provided
    if model is None:
        model = results_path.parent.name

    # Parse samples if path provided
    parsed_samples = []
    if samples_path:
        samples_path = Path(samples_path)
        if samples_path.exists():
            samples = []
            with open(samples_path) as f:
                for line in f:
                    if line.strip():
                        samples.append(json.loads(line))
            parsed_samples = parse_mcq_samples(samples, model, benchmark_variant)

    return agg_results, parsed_samples


def load_mcq_results(
    results_dir: Path | str,
    variants: list[str] | None = None,
) -> dict[str, dict[str, list[MCQResult]]]:
    """
    Load MCQ results for multiple models and variants.

    Expects directory structure:
    results_dir/
        model_name/
            results.json
            model_benchmark.jsonl

    Args:
        results_dir: Root directory containing results
        variants: List of variant identifiers to load (default: A, B, C, D)

    Returns:
        Nested dict: {model: {variant: [MCQResult, ...]}}
    """
    results_dir = Path(results_dir)
    if variants is None:
        variants = ["A", "B", "C", "D"]

    all_results: dict[str, dict[str, list[MCQResult]]] = {}

    for model_dir in results_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name
        all_results[model_name] = {}

        for variant in variants:
            # Look for samples file matching pattern
            pattern = f"*{variant.lower()}*.jsonl"
            samples_files = list(model_dir.glob(pattern))

            if not samples_files:
                # Try alternative patterns
                pattern = f"*_{variant.lower()}.jsonl"
                samples_files = list(model_dir.glob(pattern))

            if samples_files:
                samples_path = samples_files[0]
                _, parsed = parse_mcq_results(
                    results_path=model_dir / "results.json",
                    samples_path=samples_path,
                    model=model_name,
                    benchmark_variant=variant,
                )
                all_results[model_name][variant] = parsed
                logger.info(f"Loaded {len(parsed)} results for {model_name} variant {variant}")

    return all_results


def results_to_dataframe(
    results: list[MCQResult],
) -> pd.DataFrame:
    """
    Convert MCQ results to a DataFrame.

    Args:
        results: List of MCQResult objects

    Returns:
        DataFrame with result data
    """
    records = [r.to_dict() for r in results]
    return pd.DataFrame(records)


def aggregate_by_model(
    results: dict[str, dict[str, list[MCQResult]]],
) -> pd.DataFrame:
    """
    Aggregate results by model and variant.

    Args:
        results: Nested dict from load_mcq_results

    Returns:
        DataFrame with accuracy by model and variant
    """
    records = []

    for model, variants in results.items():
        for variant, mcq_results in variants.items():
            correct = sum(1 for r in mcq_results if r.is_correct)
            total = len(mcq_results)
            accuracy = correct / total if total > 0 else 0.0

            records.append({
                "model": model,
                "variant": variant,
                "correct": correct,
                "total": total,
                "accuracy": accuracy,
            })

    return pd.DataFrame(records)

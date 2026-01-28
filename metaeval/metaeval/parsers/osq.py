"""OSQ result parsing utilities."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from metaeval.core.logging import get_logger
from metaeval.core.types import DimensionScores

logger = get_logger(__name__)


@dataclass
class OSQResult:
    """Parsed OSQ result for a single question."""

    question_id: int
    question: str
    expected_answer: str
    model_response: str
    model: str
    rubric: dict[str, str] | None = None
    raw_response: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "model_response": self.model_response,
            "model": self.model,
            "rubric": self.rubric,
        }


@dataclass
class JudgedResult:
    """Parsed judged OSQ result."""

    question_id: int
    question: str
    expected_answer: str
    model_response: str
    model: str
    judge_model: str
    scores: DimensionScores | None = None
    total_score: int = 0
    justification: str = ""
    raw_judgment: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "model_response": self.model_response,
            "model": self.model,
            "judge_model": self.judge_model,
            "scores": self.scores.to_dict() if self.scores else None,
            "total_score": self.total_score,
            "justification": self.justification,
            "metadata": self.metadata,
        }


def parse_osq_results(
    samples: list[dict[str, Any]],
    model: str,
) -> list[OSQResult]:
    """
    Parse OSQ samples from lm-eval output format.

    Args:
        samples: List of sample dictionaries
        model: Model name

    Returns:
        List of OSQResult objects
    """
    results = []

    for idx, sample in enumerate(samples):
        doc = sample.get("doc", {})

        # Get question and expected answer
        question = doc.get("osq_prompt", doc.get("question", ""))
        expected = doc.get("expected_answer", "")

        # Get model response
        model_response = ""
        if "resps" in sample:
            resps = sample["resps"]
            if isinstance(resps, list) and len(resps) > 0:
                if isinstance(resps[0], list) and len(resps[0]) > 0:
                    model_response = resps[0][0]
                else:
                    model_response = str(resps[0])

        # Get rubric if available
        rubric = None
        if "full_credit" in doc:
            rubric = {
                "full_credit": doc.get("full_credit", ""),
                "partial_credit": doc.get("partial_credit", ""),
                "no_credit": doc.get("no_credit", ""),
            }

        results.append(OSQResult(
            question_id=doc.get("question_id", idx),
            question=question,
            expected_answer=expected,
            model_response=model_response,
            model=model,
            rubric=rubric,
        ))

    return results


def parse_dimension_scores(text: str) -> DimensionScores | None:
    """
    Parse dimension scores from judge response text.

    Expected format includes lines like:
    - Technical Accuracy: 18/20
    - Conceptual Understanding: 15/20
    etc.

    Args:
        text: Judge response text

    Returns:
        DimensionScores if parsing succeeds, None otherwise
    """
    patterns = {
        "technical_accuracy": r"technical\s*accuracy[:\s]*(\d+)",
        "conceptual_understanding": r"conceptual\s*understanding[:\s]*(\d+)",
        "completeness": r"completeness[:\s]*(\d+)",
        "clarity_organization": r"clarity[:\s]*(?:and\s*)?(?:organization)?[:\s]*(\d+)",
        "professional_relevance": r"professional\s*relevance[:\s]*(\d+)",
    }

    scores = {}
    text_lower = text.lower()

    for key, pattern in patterns.items():
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            scores[key] = min(20, max(0, int(match.group(1))))

    # Check if we got all dimensions
    if len(scores) == 5:
        return DimensionScores(**scores)

    # Try JSON parsing as fallback
    try:
        json_match = re.search(r"\{[^{}]*\}", text)
        if json_match:
            data = json.loads(json_match.group())
            if all(k in data for k in patterns.keys()):
                return DimensionScores(
                    technical_accuracy=min(20, max(0, int(data.get("technical_accuracy", 0)))),
                    conceptual_understanding=min(20, max(0, int(data.get("conceptual_understanding", 0)))),
                    completeness=min(20, max(0, int(data.get("completeness", 0)))),
                    clarity_organization=min(20, max(0, int(data.get("clarity_organization", 0)))),
                    professional_relevance=min(20, max(0, int(data.get("professional_relevance", 0)))),
                )
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def parse_total_score(text: str) -> int:
    """
    Parse total score from judge response.

    Args:
        text: Judge response text

    Returns:
        Total score (0-100)
    """
    # Try to find total score pattern
    patterns = [
        r"total[:\s]*(\d+)\s*/?\s*100",
        r"total\s*score[:\s]*(\d+)",
        r"score[:\s]*(\d+)\s*/?\s*100",
        r"(\d+)\s*/\s*100",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return min(100, max(0, int(match.group(1))))

    return 0


def parse_osq_judged(
    judged_data: list[dict[str, Any]],
    model: str,
    judge_model: str,
) -> list[JudgedResult]:
    """
    Parse judged OSQ results.

    Args:
        judged_data: List of judged result dictionaries
        model: Model that generated responses
        judge_model: Model that performed judging

    Returns:
        List of JudgedResult objects
    """
    results = []

    for idx, item in enumerate(judged_data):
        # Get raw judgment
        raw_judgment = item.get("judgment", item.get("judge_response", ""))

        # Parse scores
        scores = parse_dimension_scores(raw_judgment)

        # Get total score
        if scores:
            total = scores.total
        else:
            total = parse_total_score(raw_judgment)

        # Extract justification
        justification = ""
        just_match = re.search(
            r"justification[:\s]*(.+?)(?=total|score|$)",
            raw_judgment,
            re.IGNORECASE | re.DOTALL,
        )
        if just_match:
            justification = just_match.group(1).strip()

        results.append(JudgedResult(
            question_id=item.get("question_id", idx),
            question=item.get("question", item.get("osq_prompt", "")),
            expected_answer=item.get("expected_answer", ""),
            model_response=item.get("model_response", item.get("response", "")),
            model=model,
            judge_model=judge_model,
            scores=scores,
            total_score=total,
            justification=justification,
            raw_judgment=raw_judgment,
            metadata=item.get("metadata", {}),
        ))

    return results


def load_osq_results(
    results_dir: Path | str,
    model: str | None = None,
    judge_model: str | None = None,
) -> list[JudgedResult]:
    """
    Load judged OSQ results from a directory.

    Args:
        results_dir: Directory containing judged results
        model: Filter by model (optional)
        judge_model: Filter by judge model (optional)

    Returns:
        List of JudgedResult objects
    """
    results_dir = Path(results_dir)
    all_results = []

    # Look for JSONL files
    for jsonl_file in results_dir.glob("*.jsonl"):
        # Try to infer model and judge from filename
        filename = jsonl_file.stem
        parts = filename.split("_")

        inferred_model = parts[0] if len(parts) > 0 else "unknown"
        inferred_judge = parts[-1] if len(parts) > 1 else "unknown"

        # Apply filters
        if model and inferred_model != model:
            continue
        if judge_model and inferred_judge != judge_model:
            continue

        # Load and parse
        judged_data = []
        with open(jsonl_file) as f:
            for line in f:
                if line.strip():
                    judged_data.append(json.loads(line))

        results = parse_osq_judged(judged_data, inferred_model, inferred_judge)
        all_results.extend(results)
        logger.info(f"Loaded {len(results)} judged results from {jsonl_file}")

    return all_results


def results_to_dataframe(results: list[JudgedResult]) -> pd.DataFrame:
    """
    Convert judged results to a DataFrame.

    Args:
        results: List of JudgedResult objects

    Returns:
        DataFrame with result data
    """
    records = []
    for r in results:
        record = {
            "question_id": r.question_id,
            "model": r.model,
            "judge_model": r.judge_model,
            "total_score": r.total_score,
        }
        if r.scores:
            record.update(r.scores.to_dict())
        records.append(record)

    return pd.DataFrame(records)


def align_mcq_osq_results(
    mcq_results: list[Any],
    osq_results: list[JudgedResult],
    key: str = "question_id",
) -> pd.DataFrame:
    """
    Align MCQ and OSQ results for comparison.

    Args:
        mcq_results: List of MCQ results
        osq_results: List of judged OSQ results
        key: Key to align on

    Returns:
        DataFrame with aligned results
    """
    # Convert to DataFrames
    mcq_df = pd.DataFrame([
        {"question_id": r.question_id, "mcq_correct": r.is_correct, "model": r.model}
        for r in mcq_results
    ])

    osq_df = pd.DataFrame([
        {"question_id": r.question_id, "osq_score": r.total_score, "model": r.model}
        for r in osq_results
    ])

    # Merge
    aligned = mcq_df.merge(osq_df, on=[key, "model"], how="inner")

    logger.info(f"Aligned {len(aligned)} results")
    return aligned

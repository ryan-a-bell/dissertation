"""Consensus scoring from multiple judges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np

from metaeval.core.types import DimensionScores, JudgmentResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConsensusResult:
    """Result from consensus scoring."""

    scores: DimensionScores
    total_score: int
    method: str
    n_judges: int
    judge_scores: list[DimensionScores]
    agreement_score: float  # 0-1, how much judges agreed
    outlier_judges: list[int]  # Indices of outlier judges

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scores": self.scores.to_dict(),
            "total_score": self.total_score,
            "method": self.method,
            "n_judges": self.n_judges,
            "judge_scores": [s.to_dict() for s in self.judge_scores],
            "agreement_score": self.agreement_score,
            "outlier_judges": self.outlier_judges,
        }


class ConsensusScorer:
    """Aggregate scores from multiple LLM judges."""

    def __init__(
        self,
        method: Literal["mean", "median", "trimmed_mean", "majority"] = "mean",
        trim_fraction: float = 0.1,
        outlier_threshold: float = 2.0,
    ):
        """
        Initialize consensus scorer.

        Args:
            method: Aggregation method
            trim_fraction: Fraction to trim for trimmed_mean
            outlier_threshold: Z-score threshold for outlier detection
        """
        self.method = method
        self.trim_fraction = trim_fraction
        self.outlier_threshold = outlier_threshold

    def score(
        self,
        judgments: list[JudgmentResult] | list[DimensionScores],
    ) -> ConsensusResult:
        """
        Compute consensus score from multiple judgments.

        Args:
            judgments: List of judgments or dimension scores

        Returns:
            ConsensusResult with aggregated scores
        """
        # Extract DimensionScores
        if judgments and isinstance(judgments[0], JudgmentResult):
            scores = [j.scores for j in judgments if j.scores]
        else:
            scores = [s for s in judgments if s]

        if not scores:
            return ConsensusResult(
                scores=DimensionScores(0, 0, 0, 0, 0),
                total_score=0,
                method=self.method,
                n_judges=0,
                judge_scores=[],
                agreement_score=0.0,
                outlier_judges=[],
            )

        # Aggregate each dimension
        dims = ["technical_accuracy", "conceptual_understanding", "completeness",
                "clarity_organization", "professional_relevance"]

        aggregated = {}
        for dim in dims:
            values = [getattr(s, dim) for s in scores]
            aggregated[dim] = self._aggregate(values)

        consensus_scores = DimensionScores(**aggregated)

        # Calculate agreement
        agreement = self._calculate_agreement(scores)

        # Detect outliers
        outliers = self._detect_outliers(scores)

        return ConsensusResult(
            scores=consensus_scores,
            total_score=consensus_scores.total,
            method=self.method,
            n_judges=len(scores),
            judge_scores=scores,
            agreement_score=agreement,
            outlier_judges=outliers,
        )

    def _aggregate(self, values: list[int]) -> int:
        """Aggregate values using configured method."""
        if not values:
            return 0

        arr = np.array(values)

        if self.method == "mean":
            return int(round(np.mean(arr)))
        elif self.method == "median":
            return int(round(np.median(arr)))
        elif self.method == "trimmed_mean":
            from scipy import stats
            return int(round(stats.trim_mean(arr, self.trim_fraction)))
        elif self.method == "majority":
            # Most common value
            from collections import Counter
            counter = Counter(values)
            return counter.most_common(1)[0][0]
        else:
            return int(round(np.mean(arr)))

    def _calculate_agreement(self, scores: list[DimensionScores]) -> float:
        """Calculate agreement score (0-1) among judges."""
        if len(scores) < 2:
            return 1.0

        # Calculate coefficient of variation for total scores
        totals = [s.total for s in scores]
        mean = np.mean(totals)
        std = np.std(totals)

        if mean == 0:
            return 1.0

        cv = std / mean

        # Convert CV to agreement score (lower CV = higher agreement)
        # CV of 0 = perfect agreement (1.0)
        # CV of 0.5 or higher = low agreement (approaching 0)
        agreement = max(0, 1 - cv * 2)

        return float(agreement)

    def _detect_outliers(self, scores: list[DimensionScores]) -> list[int]:
        """Detect outlier judges using z-score."""
        if len(scores) < 3:
            return []

        totals = np.array([s.total for s in scores])
        mean = np.mean(totals)
        std = np.std(totals)

        if std == 0:
            return []

        z_scores = np.abs((totals - mean) / std)
        outliers = np.where(z_scores > self.outlier_threshold)[0].tolist()

        return outliers


def majority_vote(judgments: list[JudgmentResult], threshold: float = 0.5) -> str:
    """
    Determine majority credit level from judgments.

    Args:
        judgments: List of judgment results
        threshold: Minimum fraction for majority

    Returns:
        Credit level ("full", "partial", "none")
    """
    from collections import Counter

    if not judgments:
        return "none"

    # Determine credit level for each judgment
    levels = []
    for j in judgments:
        if j.scores:
            pct = j.scores.total / 100
            if pct >= 0.8:
                levels.append("full")
            elif pct >= 0.4:
                levels.append("partial")
            else:
                levels.append("none")

    if not levels:
        return "none"

    counter = Counter(levels)
    most_common, count = counter.most_common(1)[0]

    if count / len(levels) >= threshold:
        return most_common

    # No clear majority, return median-equivalent
    return "partial"


def mean_aggregation(scores: list[DimensionScores]) -> DimensionScores:
    """
    Simple mean aggregation of dimension scores.

    Args:
        scores: List of dimension scores

    Returns:
        Aggregated DimensionScores
    """
    scorer = ConsensusScorer(method="mean")
    result = scorer.score(scores)
    return result.scores


def median_aggregation(scores: list[DimensionScores]) -> DimensionScores:
    """
    Median aggregation of dimension scores.

    Args:
        scores: List of dimension scores

    Returns:
        Aggregated DimensionScores
    """
    scorer = ConsensusScorer(method="median")
    result = scorer.score(scores)
    return result.scores


def weighted_consensus(
    judgments: list[JudgmentResult],
    weights: list[float] | None = None,
) -> DimensionScores:
    """
    Weighted consensus of judgment scores.

    Args:
        judgments: List of judgment results
        weights: Optional weights per judge (default: equal)

    Returns:
        Weighted consensus DimensionScores
    """
    scores = [j.scores for j in judgments if j.scores]

    if not scores:
        return DimensionScores(0, 0, 0, 0, 0)

    if weights is None:
        weights = [1.0] * len(scores)

    if len(weights) != len(scores):
        weights = [1.0] * len(scores)

    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Weighted average for each dimension
    dims = ["technical_accuracy", "conceptual_understanding", "completeness",
            "clarity_organization", "professional_relevance"]

    aggregated = {}
    for dim in dims:
        values = [getattr(s, dim) for s in scores]
        weighted_sum = sum(v * w for v, w in zip(values, weights))
        aggregated[dim] = int(round(weighted_sum))

    return DimensionScores(**aggregated)

"""Format comparison analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from metaeval.core.types import (
    ComparisonResult,
    CorrelationResult,
    TestResult,
    EffectSize,
    BootstrapCI,
)
from metaeval.core.logging import get_logger
from metaeval.compare.stats.correlation import pearson_correlation, spearman_correlation
from metaeval.compare.stats.paired import wilcoxon_signed_rank, paired_t_test
from metaeval.compare.stats.effects import cohens_d
from metaeval.compare.stats.bootstrap import bootstrap_difference, bootstrap_correlation

logger = get_logger(__name__)


@dataclass
class FormatComparisonReport:
    """Comprehensive report of format comparison analysis."""

    model: str
    mcq_accuracy: float
    osq_mean_score: float
    osq_normalized: float  # OSQ score normalized to 0-1
    n_questions: int
    correlations: dict[str, CorrelationResult]
    paired_tests: dict[str, TestResult]
    effect_sizes: dict[str, EffectSize]
    bootstrap_cis: dict[str, BootstrapCI]
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "mcq_accuracy": self.mcq_accuracy,
            "osq_mean_score": self.osq_mean_score,
            "osq_normalized": self.osq_normalized,
            "n_questions": self.n_questions,
            "correlations": {k: v.to_dict() for k, v in self.correlations.items()},
            "paired_tests": {k: v.to_dict() for k, v in self.paired_tests.items()},
            "effect_sizes": {k: v.to_dict() for k, v in self.effect_sizes.items()},
            "bootstrap_cis": {k: v.to_dict() for k, v in self.bootstrap_cis.items()},
            "summary": self.summary,
        }


class FormatComparator:
    """Analyzer for comparing MCQ and OSQ evaluation formats."""

    def __init__(
        self,
        data: pd.DataFrame,
        mcq_col: str = "mcq_score",
        osq_col: str = "osq_score",
        model_col: str = "model",
        question_col: str = "question_id",
        alpha: float = 0.05,
        osq_max_score: float = 100.0,
    ):
        """
        Initialize the comparator.

        Args:
            data: Aligned DataFrame with MCQ and OSQ scores
            mcq_col: Column name for MCQ scores (0/1)
            osq_col: Column name for OSQ scores
            model_col: Column name for model
            question_col: Column name for question ID
            alpha: Significance level
            osq_max_score: Maximum OSQ score for normalization
        """
        self.data = data.copy()
        self.mcq_col = mcq_col
        self.osq_col = osq_col
        self.model_col = model_col
        self.question_col = question_col
        self.alpha = alpha
        self.osq_max_score = osq_max_score

        # Normalize OSQ scores to 0-1
        self.data["osq_normalized"] = self.data[osq_col] / osq_max_score

    def analyze(self, model: str) -> FormatComparisonReport:
        """
        Perform comprehensive comparison analysis for a model.

        Args:
            model: Model name to analyze

        Returns:
            FormatComparisonReport with all analysis results
        """
        model_data = self.data[self.data[self.model_col] == model].copy()

        if len(model_data) == 0:
            raise ValueError(f"No data found for model: {model}")

        mcq_scores = model_data[self.mcq_col].values.astype(float)
        osq_scores = model_data["osq_normalized"].values.astype(float)

        # Basic statistics
        mcq_accuracy = float(np.mean(mcq_scores))
        osq_mean = float(np.mean(model_data[self.osq_col].values))
        osq_normalized = float(np.mean(osq_scores))

        # Correlations
        correlations = {
            "pearson": pearson_correlation(mcq_scores, osq_scores, alpha=self.alpha),
            "spearman": spearman_correlation(mcq_scores, osq_scores, alpha=self.alpha),
        }

        # Paired tests
        paired_tests = {
            "wilcoxon": wilcoxon_signed_rank(mcq_scores, osq_scores, alpha=self.alpha),
            "paired_t": paired_t_test(mcq_scores, osq_scores, alpha=self.alpha),
        }

        # Effect sizes
        effect_sizes = {
            "cohens_d": cohens_d(mcq_scores, osq_scores, paired=True),
        }

        # Bootstrap CIs
        bootstrap_cis = {
            "mean_diff": bootstrap_difference(
                mcq_scores, osq_scores, statistic=np.mean, paired=True
            ),
            "pearson_corr": bootstrap_correlation(
                mcq_scores, osq_scores, method="pearson"
            ),
        }

        # Generate summary
        summary = self._generate_summary(
            model,
            mcq_accuracy,
            osq_normalized,
            correlations,
            paired_tests,
            effect_sizes,
        )

        return FormatComparisonReport(
            model=model,
            mcq_accuracy=mcq_accuracy,
            osq_mean_score=osq_mean,
            osq_normalized=osq_normalized,
            n_questions=len(model_data),
            correlations=correlations,
            paired_tests=paired_tests,
            effect_sizes=effect_sizes,
            bootstrap_cis=bootstrap_cis,
            summary=summary,
        )

    def analyze_all_models(self) -> dict[str, FormatComparisonReport]:
        """
        Analyze all models in the dataset.

        Returns:
            Dictionary mapping model name to FormatComparisonReport
        """
        models = self.data[self.model_col].unique()
        reports = {}

        for model in models:
            try:
                reports[model] = self.analyze(model)
                logger.info(f"Analyzed {model}")
            except Exception as e:
                logger.error(f"Failed to analyze {model}: {e}")

        return reports

    def _generate_summary(
        self,
        model: str,
        mcq_acc: float,
        osq_norm: float,
        correlations: dict[str, CorrelationResult],
        paired_tests: dict[str, TestResult],
        effect_sizes: dict[str, EffectSize],
    ) -> str:
        """Generate a human-readable summary."""
        lines = [f"Format Comparison for {model}"]
        lines.append("=" * 50)

        # Scores
        lines.append(f"\nMCQ Accuracy: {mcq_acc:.1%}")
        lines.append(f"OSQ Score (normalized): {osq_norm:.1%}")
        lines.append(f"Difference: {(mcq_acc - osq_norm):.1%}")

        # Correlations
        lines.append("\nCorrelations:")
        for name, corr in correlations.items():
            sig = "✓" if corr.significant else "✗"
            lines.append(f"  {name}: r={corr.coefficient:.3f} (p={corr.p_value:.4f}) {sig}")

        # Paired tests
        lines.append("\nPaired Tests:")
        for name, test in paired_tests.items():
            sig = "✓" if test.significant else "✗"
            lines.append(f"  {name}: stat={test.statistic:.3f} (p={test.p_value:.4f}) {sig}")

        # Effect sizes
        lines.append("\nEffect Sizes:")
        for name, effect in effect_sizes.items():
            lines.append(f"  {name}: {effect.value:.3f} ({effect.interpretation})")

        return "\n".join(lines)


def compare_formats(
    data: pd.DataFrame,
    model: str | None = None,
    **kwargs: Any,
) -> FormatComparisonReport | dict[str, FormatComparisonReport]:
    """
    Convenience function to compare formats.

    Args:
        data: Aligned DataFrame
        model: Specific model to analyze (None for all)
        **kwargs: Additional arguments for FormatComparator

    Returns:
        FormatComparisonReport or dict of reports
    """
    comparator = FormatComparator(data, **kwargs)

    if model:
        return comparator.analyze(model)
    else:
        return comparator.analyze_all_models()


def compare_by_category(
    data: pd.DataFrame,
    category_col: str = "incose_category",
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
) -> pd.DataFrame:
    """
    Compare MCQ and OSQ performance by category.

    Args:
        data: Aligned DataFrame with category information
        category_col: Column name for category
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores

    Returns:
        DataFrame with comparison by category
    """
    if category_col not in data.columns:
        logger.warning(f"Category column {category_col} not found")
        return pd.DataFrame()

    results = []
    for category in data[category_col].unique():
        cat_data = data[data[category_col] == category]

        mcq = cat_data[mcq_col].values
        osq = cat_data[osq_col].values / 100  # Normalize

        corr = spearman_correlation(mcq, osq)

        results.append({
            "category": category,
            "n": len(cat_data),
            "mcq_mean": np.mean(mcq),
            "osq_mean": np.mean(osq),
            "correlation": corr.coefficient,
            "corr_p_value": corr.p_value,
        })

    return pd.DataFrame(results)


def compare_by_blooms(
    data: pd.DataFrame,
    blooms_col: str = "blooms_level",
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
) -> pd.DataFrame:
    """
    Compare MCQ and OSQ performance by Bloom's taxonomy level.

    Args:
        data: Aligned DataFrame with Bloom's level information
        blooms_col: Column name for Bloom's level
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores

    Returns:
        DataFrame with comparison by Bloom's level
    """
    if blooms_col not in data.columns:
        logger.warning(f"Bloom's column {blooms_col} not found")
        return pd.DataFrame()

    # Define cognitive level order
    level_order = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

    results = []
    for level in level_order:
        level_data = data[data[blooms_col] == level]

        if len(level_data) == 0:
            continue

        mcq = level_data[mcq_col].values
        osq = level_data[osq_col].values / 100  # Normalize

        effect = cohens_d(mcq, osq, paired=True)

        results.append({
            "blooms_level": level,
            "n": len(level_data),
            "mcq_mean": np.mean(mcq),
            "osq_mean": np.mean(osq),
            "difference": np.mean(mcq) - np.mean(osq),
            "cohens_d": effect.value,
            "effect_interpretation": effect.interpretation,
        })

    return pd.DataFrame(results)

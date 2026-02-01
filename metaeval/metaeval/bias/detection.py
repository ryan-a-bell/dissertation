"""Position bias detection and analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from metaeval.core.types import BiasResult, TestResult, EffectSize
from metaeval.core.logging import get_logger
from metaeval.bias.stats.tests import (
    chi_square_test,
    kruskal_wallis_test,
    friedman_test,
    pairwise_mcnemar,
    anova_test,
)
from metaeval.bias.stats.effects import (
    cramers_v_from_result,
    epsilon_squared_from_result,
    kendalls_w_from_result,
)

logger = get_logger(__name__)


@dataclass
class PositionBiasReport:
    """Comprehensive report of position bias analysis."""

    model: str
    accuracy_by_position: dict[str, float]
    overall_accuracy: float
    test_results: dict[str, TestResult]
    effect_sizes: dict[str, EffectSize]
    pairwise_results: list[tuple[str, str, TestResult]]
    has_significant_bias: bool
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "accuracy_by_position": self.accuracy_by_position,
            "overall_accuracy": self.overall_accuracy,
            "test_results": {k: v.to_dict() for k, v in self.test_results.items()},
            "effect_sizes": {k: v.to_dict() for k, v in self.effect_sizes.items()},
            "pairwise_results": [
                {"pos_a": a, "pos_b": b, "result": r.to_dict()}
                for a, b, r in self.pairwise_results
            ],
            "has_significant_bias": self.has_significant_bias,
            "summary": self.summary,
        }


class PositionBiasAnalyzer:
    """Analyzer for detecting and quantifying position bias in MCQ responses."""

    def __init__(
        self,
        data: pd.DataFrame,
        model_col: str = "model",
        position_col: str = "variant",
        correct_col: str = "is_correct",
        question_col: str = "question_id",
        alpha: float = 0.05,
    ):
        """
        Initialize the analyzer.

        Args:
            data: DataFrame with MCQ results across positions
            model_col: Column name for model
            position_col: Column name for position variant (A, B, C, D)
            correct_col: Column name for correctness (0/1 or bool)
            question_col: Column name for question identifier
            alpha: Significance level for statistical tests
        """
        self.data = data.copy()
        self.model_col = model_col
        self.position_col = position_col
        self.correct_col = correct_col
        self.question_col = question_col
        self.alpha = alpha

        # Ensure correct_col is numeric
        self.data[correct_col] = self.data[correct_col].astype(int)

    def get_accuracy_by_position(self, model: str | None = None) -> dict[str, float]:
        """
        Calculate accuracy for each position.

        Args:
            model: Specific model to analyze (None for all)

        Returns:
            Dictionary mapping position to accuracy
        """
        data = self.data
        if model:
            data = data[data[self.model_col] == model]

        accuracy = data.groupby(self.position_col)[self.correct_col].mean()
        return accuracy.to_dict()

    def validate_model_data(self, model: str) -> dict[str, Any]:
        """
        Validate that a model has sufficient data for bias analysis.

        Args:
            model: Model name to validate

        Returns:
            Dict with 'valid', 'n_variants', 'variants', 'message'
        """
        model_data = self.data[self.data[self.model_col] == model]

        if len(model_data) == 0:
            return {
                "valid": False,
                "n_variants": 0,
                "variants": [],
                "message": f"No data found for model: {model}",
            }

        variants = sorted(model_data[self.position_col].unique().tolist())
        n_variants = len(variants)

        if n_variants < 2:
            return {
                "valid": False,
                "n_variants": n_variants,
                "variants": variants,
                "message": (
                    f"Insufficient variants for {model}: found {n_variants} ({', '.join(variants)}). "
                    f"Position bias analysis requires at least 2 variants."
                ),
            }

        if n_variants < 4:
            expected = {"A", "B", "C", "D"}
            missing = sorted(expected - set(variants))
            return {
                "valid": True,
                "n_variants": n_variants,
                "variants": variants,
                "message": (
                    f"Suboptimal coverage for {model}: {n_variants}/4 variants ({', '.join(variants)}). "
                    f"Missing: {', '.join(missing)}. Results may be less reliable."
                ),
            }

        return {
            "valid": True,
            "n_variants": n_variants,
            "variants": variants,
            "message": None,
        }

    def analyze(self, model: str) -> PositionBiasReport:
        """
        Perform comprehensive bias analysis for a model.

        Args:
            model: Model name to analyze

        Returns:
            PositionBiasReport with all analysis results

        Raises:
            ValueError: If model has insufficient data or variants
        """
        # Validate before analysis
        validation = self.validate_model_data(model)
        if not validation["valid"]:
            raise ValueError(validation["message"])

        if validation["message"]:
            logger.warning(validation["message"])

        model_data = self.data[self.data[self.model_col] == model].copy()

        if len(model_data) == 0:
            raise ValueError(f"No data found for model: {model}")

        # Get accuracy by position
        accuracy_by_pos = self.get_accuracy_by_position(model)
        overall_accuracy = model_data[self.correct_col].mean()

        # Prepare test results
        test_results: dict[str, TestResult] = {}
        effect_sizes: dict[str, EffectSize] = {}

        # 1. Chi-square test
        chi_result = chi_square_test(
            model_data,
            position_col=self.position_col,
            correct_col=self.correct_col,
            alpha=self.alpha,
        )
        test_results["chi_square"] = chi_result

        # Chi-square effect size (Cramér's V)
        n_samples = len(model_data)
        positions = model_data[self.position_col].nunique()
        effect_sizes["cramers_v"] = cramers_v_from_result(
            chi_result, n_samples, positions, 2  # 2 for correct/incorrect
        )

        # 2. Kruskal-Wallis test
        groups = {
            pos: model_data[model_data[self.position_col] == pos][self.correct_col].values
            for pos in sorted(model_data[self.position_col].unique())
        }
        kw_result = kruskal_wallis_test(groups, alpha=self.alpha)
        test_results["kruskal_wallis"] = kw_result
        effect_sizes["epsilon_squared"] = epsilon_squared_from_result(kw_result)

        # 3. Friedman test (requires pivot table)
        try:
            pivot = model_data.pivot_table(
                index=self.question_col,
                columns=self.position_col,
                values=self.correct_col,
                aggfunc="first",
            ).dropna()

            if len(pivot) > 0:
                friedman_result = friedman_test(pivot, alpha=self.alpha)
                test_results["friedman"] = friedman_result
                effect_sizes["kendalls_w"] = kendalls_w_from_result(friedman_result)
        except Exception as e:
            logger.warning(f"Could not perform Friedman test: {e}")

        # 4. Pairwise McNemar tests
        pairwise = pairwise_mcnemar(
            model_data,
            position_col=self.position_col,
            correct_col=self.correct_col,
            question_col=self.question_col,
            alpha=self.alpha,
        )

        # 5. ANOVA (for comparison, though assumptions may not hold)
        anova_result = anova_test(groups, alpha=self.alpha)
        test_results["anova"] = anova_result

        # Determine if significant bias exists
        significant_tests = sum(1 for r in test_results.values() if r.significant)
        has_bias = significant_tests >= 2  # Majority of tests significant

        # Generate summary
        summary = self._generate_summary(
            model, accuracy_by_pos, test_results, effect_sizes, has_bias
        )

        return PositionBiasReport(
            model=model,
            accuracy_by_position=accuracy_by_pos,
            overall_accuracy=overall_accuracy,
            test_results=test_results,
            effect_sizes=effect_sizes,
            pairwise_results=pairwise,
            has_significant_bias=has_bias,
            summary=summary,
        )

    def analyze_all_models(self) -> dict[str, PositionBiasReport]:
        """
        Analyze all models in the dataset.

        Returns:
            Dictionary mapping model name to PositionBiasReport
        """
        models = self.data[self.model_col].unique()
        reports = {}

        for model in models:
            try:
                reports[model] = self.analyze(model)
                logger.info(f"Analyzed {model}: bias={reports[model].has_significant_bias}")
            except Exception as e:
                logger.error(f"Failed to analyze {model}: {e}")

        return reports

    def _generate_summary(
        self,
        model: str,
        accuracy_by_pos: dict[str, float],
        test_results: dict[str, TestResult],
        effect_sizes: dict[str, EffectSize],
        has_bias: bool,
    ) -> str:
        """Generate a human-readable summary."""
        lines = [f"Position Bias Analysis for {model}"]
        lines.append("=" * 50)

        # Accuracy summary
        lines.append("\nAccuracy by Position:")
        for pos, acc in sorted(accuracy_by_pos.items()):
            lines.append(f"  {pos}: {acc:.1%}")

        max_pos = max(accuracy_by_pos, key=accuracy_by_pos.get)
        min_pos = min(accuracy_by_pos, key=accuracy_by_pos.get)
        spread = accuracy_by_pos[max_pos] - accuracy_by_pos[min_pos]
        lines.append(f"\nSpread: {spread:.1%} ({max_pos} - {min_pos})")

        # Test results
        lines.append("\nStatistical Tests:")
        for name, result in test_results.items():
            sig = "✓" if result.significant else "✗"
            lines.append(f"  {name}: p={result.p_value:.4f} {sig}")

        # Effect sizes
        lines.append("\nEffect Sizes:")
        for name, effect in effect_sizes.items():
            lines.append(f"  {name}: {effect.value:.3f} ({effect.interpretation})")

        # Conclusion
        lines.append("\n" + "=" * 50)
        if has_bias:
            lines.append("CONCLUSION: Significant position bias detected")
        else:
            lines.append("CONCLUSION: No significant position bias detected")

        return "\n".join(lines)


def analyze_position_bias(
    data: pd.DataFrame,
    model: str | None = None,
    **kwargs: Any,
) -> PositionBiasReport | dict[str, PositionBiasReport]:
    """
    Convenience function to analyze position bias.

    Args:
        data: DataFrame with MCQ results
        model: Specific model to analyze (None for all)
        **kwargs: Additional arguments for PositionBiasAnalyzer

    Returns:
        PositionBiasReport or dict of reports
    """
    analyzer = PositionBiasAnalyzer(data, **kwargs)

    if model:
        return analyzer.analyze(model)
    else:
        return analyzer.analyze_all_models()


def detect_bias(
    data: pd.DataFrame,
    model: str,
    alpha: float = 0.05,
    **kwargs: Any,
) -> bool:
    """
    Quick check for position bias.

    Args:
        data: DataFrame with MCQ results
        model: Model to check
        alpha: Significance level
        **kwargs: Additional arguments for PositionBiasAnalyzer

    Returns:
        True if significant bias detected
    """
    analyzer = PositionBiasAnalyzer(data, alpha=alpha, **kwargs)
    report = analyzer.analyze(model)
    return report.has_significant_bias


def get_accuracy_by_position(
    data: pd.DataFrame,
    model: str | None = None,
    position_col: str = "variant",
    correct_col: str = "is_correct",
    model_col: str = "model",
) -> dict[str, float]:
    """
    Get accuracy by position for quick analysis.

    Args:
        data: DataFrame with MCQ results
        model: Specific model (None for all)
        position_col: Column name for position
        correct_col: Column name for correctness
        model_col: Column name for model

    Returns:
        Dictionary mapping position to accuracy
    """
    if model:
        data = data[data[model_col] == model]

    return data.groupby(position_col)[correct_col].mean().to_dict()

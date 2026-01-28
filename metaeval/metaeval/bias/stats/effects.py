"""Effect size calculations for position bias analysis."""

from __future__ import annotations

from typing import Literal

import numpy as np

from metaeval.core.types import EffectSize, TestResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


# Effect size interpretation thresholds
EFFECT_THRESHOLDS = {
    "cramers_v": {"small": 0.1, "medium": 0.3, "large": 0.5},
    "kendalls_w": {"small": 0.1, "medium": 0.3, "large": 0.5},
    "epsilon_squared": {"small": 0.01, "medium": 0.06, "large": 0.14},
    "cohens_d": {"small": 0.2, "medium": 0.5, "large": 0.8},
    "eta_squared": {"small": 0.01, "medium": 0.06, "large": 0.14},
}


def interpret_effect_size(
    value: float,
    measure: str,
) -> str:
    """
    Interpret an effect size value.

    Args:
        value: Effect size value
        measure: Name of effect size measure

    Returns:
        Interpretation string ("negligible", "small", "medium", "large")
    """
    thresholds = EFFECT_THRESHOLDS.get(measure, EFFECT_THRESHOLDS["cohens_d"])

    abs_value = abs(value)

    if abs_value < thresholds["small"]:
        return "negligible"
    elif abs_value < thresholds["medium"]:
        return "small"
    elif abs_value < thresholds["large"]:
        return "medium"
    else:
        return "large"


def cramers_v(
    chi2: float,
    n: int,
    min_dim: int,
) -> EffectSize:
    """
    Calculate Cramér's V effect size from chi-square test.

    Cramér's V measures the strength of association between two
    categorical variables. Range: 0 to 1.

    Args:
        chi2: Chi-square statistic
        n: Total sample size
        min_dim: Minimum of (rows - 1, cols - 1)

    Returns:
        EffectSize with Cramér's V value and interpretation
    """
    if n == 0 or min_dim == 0:
        value = 0.0
    else:
        value = np.sqrt(chi2 / (n * min_dim))

    interpretation = interpret_effect_size(value, "cramers_v")

    return EffectSize(
        measure="cramers_v",
        value=float(value),
        interpretation=interpretation,
    )


def cramers_v_from_result(
    chi_result: TestResult,
    n: int,
    n_rows: int,
    n_cols: int,
) -> EffectSize:
    """
    Calculate Cramér's V from a chi-square TestResult.

    Args:
        chi_result: TestResult from chi_square_test
        n: Total sample size
        n_rows: Number of rows in contingency table
        n_cols: Number of columns in contingency table

    Returns:
        EffectSize with Cramér's V value and interpretation
    """
    min_dim = min(n_rows - 1, n_cols - 1)
    return cramers_v(chi_result.statistic, n, min_dim)


def kendalls_w(
    friedman_stat: float,
    n: int,
    k: int,
) -> EffectSize:
    """
    Calculate Kendall's W (coefficient of concordance) from Friedman test.

    Kendall's W measures agreement among raters or consistency across
    conditions. Range: 0 (no agreement) to 1 (complete agreement).

    Args:
        friedman_stat: Friedman chi-square statistic
        n: Number of subjects
        k: Number of conditions/raters

    Returns:
        EffectSize with Kendall's W value and interpretation
    """
    if n == 0 or k <= 1:
        value = 0.0
    else:
        value = friedman_stat / (n * (k - 1))

    # Clamp to valid range
    value = max(0.0, min(1.0, value))

    interpretation = interpret_effect_size(value, "kendalls_w")

    return EffectSize(
        measure="kendalls_w",
        value=float(value),
        interpretation=interpretation,
    )


def kendalls_w_from_result(
    friedman_result: TestResult,
) -> EffectSize:
    """
    Calculate Kendall's W from a Friedman TestResult.

    Args:
        friedman_result: TestResult from friedman_test

    Returns:
        EffectSize with Kendall's W value and interpretation
    """
    n = friedman_result.additional_info.get("n_subjects", 0)
    k = friedman_result.additional_info.get("n_conditions", 0)
    return kendalls_w(friedman_result.statistic, n, k)


def epsilon_squared(
    h_stat: float,
    n: int,
) -> EffectSize:
    """
    Calculate epsilon-squared effect size from Kruskal-Wallis H statistic.

    Epsilon-squared (ε²) is an effect size for Kruskal-Wallis test.
    Range: 0 to 1.

    Args:
        h_stat: Kruskal-Wallis H statistic
        n: Total sample size

    Returns:
        EffectSize with epsilon-squared value and interpretation
    """
    if n <= 1:
        value = 0.0
    else:
        value = h_stat / (n - 1)

    # Clamp to valid range
    value = max(0.0, min(1.0, value))

    interpretation = interpret_effect_size(value, "epsilon_squared")

    return EffectSize(
        measure="epsilon_squared",
        value=float(value),
        interpretation=interpretation,
    )


def epsilon_squared_from_result(
    kw_result: TestResult,
) -> EffectSize:
    """
    Calculate epsilon-squared from a Kruskal-Wallis TestResult.

    Args:
        kw_result: TestResult from kruskal_wallis_test

    Returns:
        EffectSize with epsilon-squared value and interpretation
    """
    n = sum(kw_result.additional_info.get("group_sizes", [0]))
    return epsilon_squared(kw_result.statistic, n)


def eta_squared(
    ss_between: float,
    ss_total: float,
) -> EffectSize:
    """
    Calculate eta-squared effect size from ANOVA.

    Eta-squared (η²) is the proportion of variance explained.
    Range: 0 to 1.

    Args:
        ss_between: Sum of squares between groups
        ss_total: Total sum of squares

    Returns:
        EffectSize with eta-squared value and interpretation
    """
    if ss_total == 0:
        value = 0.0
    else:
        value = ss_between / ss_total

    interpretation = interpret_effect_size(value, "eta_squared")

    return EffectSize(
        measure="eta_squared",
        value=float(value),
        interpretation=interpretation,
    )


def compute_all_effect_sizes(
    chi_result: TestResult | None = None,
    kw_result: TestResult | None = None,
    friedman_result: TestResult | None = None,
    n_samples: int = 0,
    n_rows: int = 0,
    n_cols: int = 0,
) -> list[EffectSize]:
    """
    Compute all applicable effect sizes from test results.

    Args:
        chi_result: Chi-square test result
        kw_result: Kruskal-Wallis test result
        friedman_result: Friedman test result
        n_samples: Total sample size
        n_rows: Number of rows (for chi-square)
        n_cols: Number of columns (for chi-square)

    Returns:
        List of EffectSize objects
    """
    effects = []

    if chi_result is not None and n_samples > 0 and n_rows > 0 and n_cols > 0:
        effects.append(cramers_v_from_result(chi_result, n_samples, n_rows, n_cols))

    if kw_result is not None:
        effects.append(epsilon_squared_from_result(kw_result))

    if friedman_result is not None:
        effects.append(kendalls_w_from_result(friedman_result))

    return effects

"""Statistical tests for position bias detection."""

from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from metaeval.core.types import TestResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def chi_square_test(
    data: pd.DataFrame,
    position_col: str = "variant",
    correct_col: str = "is_correct",
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform chi-square test for independence between position and correctness.

    Tests whether the distribution of correct/incorrect answers is independent
    of the answer position (A, B, C, D).

    Args:
        data: DataFrame with position and correctness columns
        position_col: Column name for position
        correct_col: Column name for correctness
        alpha: Significance level

    Returns:
        TestResult with chi-square statistic and p-value
    """
    # Create contingency table
    contingency = pd.crosstab(data[position_col], data[correct_col])

    # Perform chi-square test
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    return TestResult(
        test_name="chi_square",
        statistic=chi2,
        p_value=p_value,
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "degrees_of_freedom": dof,
            "expected_frequencies": expected.tolist(),
            "contingency_table": contingency.to_dict(),
        },
    )


def kruskal_wallis_test(
    groups: list[np.ndarray] | dict[str, np.ndarray],
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform Kruskal-Wallis H-test for independent samples.

    Non-parametric test to determine if samples originate from the same
    distribution. Used when normality assumption is violated.

    Args:
        groups: List or dict of arrays, one per group
        alpha: Significance level

    Returns:
        TestResult with H-statistic and p-value
    """
    if isinstance(groups, dict):
        group_arrays = list(groups.values())
        group_names = list(groups.keys())
    else:
        group_arrays = groups
        group_names = [f"group_{i}" for i in range(len(groups))]

    # Perform test
    h_stat, p_value = stats.kruskal(*group_arrays)

    return TestResult(
        test_name="kruskal_wallis",
        statistic=h_stat,
        p_value=p_value,
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_groups": len(group_arrays),
            "group_names": group_names,
            "group_sizes": [len(g) for g in group_arrays],
        },
    )


def friedman_test(
    data: pd.DataFrame | np.ndarray,
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform Friedman test for repeated measures.

    Non-parametric alternative to repeated measures ANOVA. Tests whether
    the distributions of related samples are identical.

    Args:
        data: DataFrame or 2D array where rows are subjects and columns are conditions
        alpha: Significance level

    Returns:
        TestResult with Friedman statistic and p-value
    """
    if isinstance(data, pd.DataFrame):
        data_array = data.values
        condition_names = data.columns.tolist()
    else:
        data_array = data
        condition_names = [f"condition_{i}" for i in range(data.shape[1])]

    # Perform test
    friedman_stat, p_value = stats.friedmanchisquare(*data_array.T)

    return TestResult(
        test_name="friedman",
        statistic=friedman_stat,
        p_value=p_value,
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_subjects": data_array.shape[0],
            "n_conditions": data_array.shape[1],
            "condition_names": condition_names,
        },
    )


def mcnemar_test(
    correct_a: np.ndarray,
    correct_b: np.ndarray,
    alpha: float = 0.05,
    correction: bool = True,
) -> TestResult:
    """
    Perform McNemar's test for paired nominal data.

    Tests the null hypothesis that the row and column marginal frequencies
    are equal (i.e., symmetry of the contingency table).

    Args:
        correct_a: Binary array of correctness for condition A
        correct_b: Binary array of correctness for condition B
        alpha: Significance level
        correction: Whether to apply continuity correction

    Returns:
        TestResult with McNemar statistic and p-value
    """
    # Create 2x2 contingency table
    # [both correct, a correct b wrong]
    # [a wrong b correct, both wrong]
    both_correct = np.sum((correct_a == 1) & (correct_b == 1))
    a_only = np.sum((correct_a == 1) & (correct_b == 0))
    b_only = np.sum((correct_a == 0) & (correct_b == 1))
    both_wrong = np.sum((correct_a == 0) & (correct_b == 0))

    table = np.array([[both_correct, a_only], [b_only, both_wrong]])

    # Perform McNemar test
    # Using the exact binomial test when b + c < 25
    b, c = a_only, b_only

    if b + c < 25:
        # Exact binomial test
        p_value = stats.binom_test(min(b, c), b + c, 0.5) * 2  # Two-sided
        statistic = min(b, c)
        method = "exact"
    else:
        # Chi-square approximation
        if correction:
            statistic = (abs(b - c) - 1) ** 2 / (b + c) if (b + c) > 0 else 0
        else:
            statistic = (b - c) ** 2 / (b + c) if (b + c) > 0 else 0
        p_value = 1 - stats.chi2.cdf(statistic, 1)
        method = "chi2_corrected" if correction else "chi2"

    return TestResult(
        test_name="mcnemar",
        statistic=statistic,
        p_value=p_value,
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "contingency_table": table.tolist(),
            "b": int(b),
            "c": int(c),
            "method": method,
        },
    )


def pairwise_mcnemar(
    data: pd.DataFrame,
    position_col: str = "variant",
    correct_col: str = "is_correct",
    question_col: str = "question_id",
    alpha: float = 0.05,
    correction: str = "bonferroni",
) -> list[tuple[str, str, TestResult]]:
    """
    Perform pairwise McNemar tests between all position pairs.

    Args:
        data: DataFrame with position, correctness, and question columns
        position_col: Column name for position
        correct_col: Column name for correctness
        question_col: Column name for question ID
        alpha: Significance level
        correction: Multiple comparison correction method

    Returns:
        List of (position_a, position_b, TestResult) tuples
    """
    positions = sorted(data[position_col].unique())
    n_comparisons = len(list(combinations(positions, 2)))

    # Adjust alpha for multiple comparisons
    if correction == "bonferroni":
        adjusted_alpha = alpha / n_comparisons
    else:
        adjusted_alpha = alpha

    results = []

    # Pivot data to get correctness by question and position
    pivot = data.pivot_table(
        index=question_col,
        columns=position_col,
        values=correct_col,
        aggfunc="first",
    )

    for pos_a, pos_b in combinations(positions, 2):
        # Get paired correctness data
        valid_idx = pivot[[pos_a, pos_b]].dropna().index
        correct_a = pivot.loc[valid_idx, pos_a].values.astype(int)
        correct_b = pivot.loc[valid_idx, pos_b].values.astype(int)

        result = mcnemar_test(correct_a, correct_b, alpha=adjusted_alpha)
        result.additional_info["comparison"] = f"{pos_a} vs {pos_b}"
        result.additional_info["n_pairs"] = len(valid_idx)

        results.append((pos_a, pos_b, result))

    return results


def anova_test(
    groups: list[np.ndarray] | dict[str, np.ndarray],
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform one-way ANOVA test.

    Parametric test assuming normality and homogeneity of variance.

    Args:
        groups: List or dict of arrays, one per group
        alpha: Significance level

    Returns:
        TestResult with F-statistic and p-value
    """
    if isinstance(groups, dict):
        group_arrays = list(groups.values())
        group_names = list(groups.keys())
    else:
        group_arrays = groups
        group_names = [f"group_{i}" for i in range(len(groups))]

    # Perform test
    f_stat, p_value = stats.f_oneway(*group_arrays)

    return TestResult(
        test_name="anova",
        statistic=f_stat,
        p_value=p_value,
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_groups": len(group_arrays),
            "group_names": group_names,
            "group_sizes": [len(g) for g in group_arrays],
            "group_means": [float(np.mean(g)) for g in group_arrays],
            "group_stds": [float(np.std(g)) for g in group_arrays],
        },
    )


def shapiro_wilk_test(
    data: np.ndarray,
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform Shapiro-Wilk test for normality.

    Args:
        data: Array of values to test
        alpha: Significance level

    Returns:
        TestResult indicating whether data is normally distributed
    """
    stat, p_value = stats.shapiro(data)

    return TestResult(
        test_name="shapiro_wilk",
        statistic=stat,
        p_value=p_value,
        significant=p_value < alpha,  # Significant = NOT normal
        alpha=alpha,
        additional_info={
            "n": len(data),
            "is_normal": p_value >= alpha,
        },
    )

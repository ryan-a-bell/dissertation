"""Paired statistical tests for format comparison."""

from __future__ import annotations

import numpy as np
from scipy import stats

from metaeval.core.types import TestResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def wilcoxon_signed_rank(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> TestResult:
    """
    Perform Wilcoxon signed-rank test for paired samples.

    Non-parametric test for comparing two related samples.
    Does not assume normality.

    Args:
        x: First sample array
        y: Second sample array
        alpha: Significance level
        alternative: Alternative hypothesis ("two-sided", "less", "greater")

    Returns:
        TestResult with statistic and p-value
    """
    # Remove pairs with NaN or zero difference
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    # Filter out zero differences
    diff = x_clean - y_clean
    nonzero_mask = diff != 0
    x_nz = x_clean[nonzero_mask]
    y_nz = y_clean[nonzero_mask]

    if len(x_nz) < 10:
        logger.warning("Sample size too small for Wilcoxon test, results may be unreliable")

    if len(x_nz) == 0:
        return TestResult(
            test_name="wilcoxon_signed_rank",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            alpha=alpha,
            additional_info={"n_pairs": 0, "warning": "No non-zero differences"},
        )

    try:
        statistic, p_value = stats.wilcoxon(x_nz, y_nz, alternative=alternative)
    except ValueError as e:
        return TestResult(
            test_name="wilcoxon_signed_rank",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            alpha=alpha,
            additional_info={"error": str(e)},
        )

    return TestResult(
        test_name="wilcoxon_signed_rank",
        statistic=float(statistic),
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_pairs": len(x_nz),
            "alternative": alternative,
            "mean_diff": float(np.mean(x_nz - y_nz)),
            "median_diff": float(np.median(x_nz - y_nz)),
        },
    )


def paired_t_test(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> TestResult:
    """
    Perform paired t-test for related samples.

    Parametric test assuming normally distributed differences.

    Args:
        x: First sample array
        y: Second sample array
        alpha: Significance level
        alternative: Alternative hypothesis ("two-sided", "less", "greater")

    Returns:
        TestResult with t-statistic and p-value
    """
    # Remove pairs with NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 2:
        return TestResult(
            test_name="paired_t_test",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            alpha=alpha,
            additional_info={"n_pairs": len(x_clean), "warning": "Sample size too small"},
        )

    t_stat, p_value = stats.ttest_rel(x_clean, y_clean, alternative=alternative)

    # Calculate difference statistics
    diff = x_clean - y_clean
    diff_mean = np.mean(diff)
    diff_std = np.std(diff, ddof=1)
    diff_se = diff_std / np.sqrt(len(diff))

    return TestResult(
        test_name="paired_t_test",
        statistic=float(t_stat),
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_pairs": len(x_clean),
            "alternative": alternative,
            "mean_diff": float(diff_mean),
            "std_diff": float(diff_std),
            "se_diff": float(diff_se),
            "df": len(x_clean) - 1,
        },
    )


def sign_test(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform sign test for paired samples.

    Simple non-parametric test based only on the signs of differences.
    More robust but less powerful than Wilcoxon.

    Args:
        x: First sample array
        y: Second sample array
        alpha: Significance level

    Returns:
        TestResult with test statistic and p-value
    """
    # Remove pairs with NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    # Calculate differences
    diff = x_clean - y_clean

    # Count positive and negative differences (excluding zeros)
    n_positive = np.sum(diff > 0)
    n_negative = np.sum(diff < 0)
    n_total = n_positive + n_negative

    if n_total == 0:
        return TestResult(
            test_name="sign_test",
            statistic=0.0,
            p_value=1.0,
            significant=False,
            alpha=alpha,
            additional_info={"warning": "No non-zero differences"},
        )

    # Use binomial test
    # Under null hypothesis, P(positive) = 0.5
    k = min(n_positive, n_negative)
    p_value = 2 * stats.binom.cdf(k, n_total, 0.5)  # Two-sided
    p_value = min(1.0, p_value)

    return TestResult(
        test_name="sign_test",
        statistic=float(k),
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "n_positive": int(n_positive),
            "n_negative": int(n_negative),
            "n_zero": int(np.sum(diff == 0)),
            "n_total": int(n_total),
        },
    )


def mcnemar_bowker_test(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
) -> TestResult:
    """
    Perform McNemar-Bowker test for symmetry.

    Extension of McNemar test for more than 2 categories.

    Args:
        x: First sample array (categorical)
        y: Second sample array (categorical)
        alpha: Significance level

    Returns:
        TestResult with chi-square statistic and p-value
    """
    import pandas as pd

    # Create contingency table
    table = pd.crosstab(x, y)

    # Calculate test statistic
    n_categories = len(table)
    chi2 = 0.0
    df = 0

    for i in range(n_categories):
        for j in range(i + 1, n_categories):
            if i < len(table) and j < len(table.columns):
                n_ij = table.iloc[i, j] if j < table.shape[1] else 0
                n_ji = table.iloc[j, i] if i < table.shape[1] else 0

                if n_ij + n_ji > 0:
                    chi2 += (n_ij - n_ji) ** 2 / (n_ij + n_ji)
                    df += 1

    if df == 0:
        p_value = 1.0
    else:
        p_value = 1 - stats.chi2.cdf(chi2, df)

    return TestResult(
        test_name="mcnemar_bowker",
        statistic=float(chi2),
        p_value=float(p_value),
        significant=p_value < alpha,
        alpha=alpha,
        additional_info={
            "df": df,
            "n_categories": n_categories,
        },
    )

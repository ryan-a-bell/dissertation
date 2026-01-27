"""Correlation analysis for format comparison."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from metaeval.core.types import CorrelationResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def pearson_correlation(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
) -> CorrelationResult:
    """
    Calculate Pearson correlation coefficient.

    Measures linear correlation between two variables.
    Assumes normality and interval/ratio data.

    Args:
        x: First variable array
        y: Second variable array
        alpha: Significance level

    Returns:
        CorrelationResult with coefficient and p-value
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return CorrelationResult(
            method="pearson",
            coefficient=0.0,
            p_value=1.0,
            n=len(x_clean),
            significant=False,
            alpha=alpha,
        )

    r, p_value = stats.pearsonr(x_clean, y_clean)

    return CorrelationResult(
        method="pearson",
        coefficient=float(r),
        p_value=float(p_value),
        n=len(x_clean),
        significant=p_value < alpha,
        alpha=alpha,
    )


def spearman_correlation(
    x: np.ndarray,
    y: np.ndarray,
    alpha: float = 0.05,
) -> CorrelationResult:
    """
    Calculate Spearman rank correlation coefficient.

    Non-parametric measure of rank correlation. Does not assume
    normality or linearity.

    Args:
        x: First variable array
        y: Second variable array
        alpha: Significance level

    Returns:
        CorrelationResult with coefficient and p-value
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 3:
        return CorrelationResult(
            method="spearman",
            coefficient=0.0,
            p_value=1.0,
            n=len(x_clean),
            significant=False,
            alpha=alpha,
        )

    rho, p_value = stats.spearmanr(x_clean, y_clean)

    return CorrelationResult(
        method="spearman",
        coefficient=float(rho),
        p_value=float(p_value),
        n=len(x_clean),
        significant=p_value < alpha,
        alpha=alpha,
    )


def correlation_matrix(
    data: pd.DataFrame,
    method: str = "pearson",
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Calculate correlation matrix for multiple variables.

    Args:
        data: DataFrame with numeric columns
        method: Correlation method ("pearson" or "spearman")
        columns: Specific columns to include (default: all numeric)

    Returns:
        Correlation matrix as DataFrame
    """
    if columns:
        data = data[columns]

    # Select only numeric columns
    numeric_data = data.select_dtypes(include=[np.number])

    if method == "pearson":
        return numeric_data.corr(method="pearson")
    elif method == "spearman":
        return numeric_data.corr(method="spearman")
    else:
        raise ValueError(f"Unknown correlation method: {method}")


def correlation_with_confidence(
    x: np.ndarray,
    y: np.ndarray,
    method: str = "pearson",
    confidence: float = 0.95,
    n_bootstrap: int = 10000,
) -> dict[str, Any]:
    """
    Calculate correlation with bootstrap confidence interval.

    Args:
        x: First variable array
        y: Second variable array
        method: Correlation method ("pearson" or "spearman")
        confidence: Confidence level
        n_bootstrap: Number of bootstrap iterations

    Returns:
        Dictionary with correlation, p-value, and CI
    """
    # Calculate point estimate
    if method == "pearson":
        result = pearson_correlation(x, y)
    else:
        result = spearman_correlation(x, y)

    # Bootstrap CI
    n = len(x)
    bootstrap_corrs = []

    for _ in range(n_bootstrap):
        indices = np.random.randint(0, n, n)
        x_boot = x[indices]
        y_boot = y[indices]

        if method == "pearson":
            r, _ = stats.pearsonr(x_boot, y_boot)
        else:
            r, _ = stats.spearmanr(x_boot, y_boot)

        bootstrap_corrs.append(r)

    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_corrs, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_corrs, (1 - alpha / 2) * 100)

    return {
        "method": method,
        "coefficient": result.coefficient,
        "p_value": result.p_value,
        "n": result.n,
        "significant": result.significant,
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "confidence": confidence,
    }

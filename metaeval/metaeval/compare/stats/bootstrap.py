"""Bootstrap confidence interval calculations."""

from __future__ import annotations

from typing import Callable, Any

import numpy as np

from metaeval.core.types import BootstrapCI
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def bootstrap_ci(
    data: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_iterations: int = 10000,
    confidence: float = 0.95,
    random_state: int | None = None,
) -> BootstrapCI:
    """
    Calculate bootstrap confidence interval for a statistic.

    Args:
        data: Sample data array
        statistic: Function to compute statistic (default: mean)
        n_iterations: Number of bootstrap iterations
        confidence: Confidence level (default: 0.95)
        random_state: Random seed for reproducibility

    Returns:
        BootstrapCI with point estimate and confidence bounds
    """
    if random_state is not None:
        np.random.seed(random_state)

    # Remove NaN values
    data_clean = data[~np.isnan(data)]
    n = len(data_clean)

    if n == 0:
        return BootstrapCI(
            statistic="unknown",
            point_estimate=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            confidence_level=confidence,
            n_iterations=n_iterations,
        )

    # Point estimate
    point_estimate = statistic(data_clean)

    # Bootstrap resampling
    bootstrap_stats = []
    for _ in range(n_iterations):
        sample = np.random.choice(data_clean, size=n, replace=True)
        bootstrap_stats.append(statistic(sample))

    bootstrap_stats = np.array(bootstrap_stats)

    # Calculate percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_stats, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)

    # Get statistic name
    stat_name = getattr(statistic, "__name__", "unknown")

    return BootstrapCI(
        statistic=stat_name,
        point_estimate=float(point_estimate),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence,
        n_iterations=n_iterations,
    )


def bootstrap_difference(
    x: np.ndarray,
    y: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_iterations: int = 10000,
    confidence: float = 0.95,
    paired: bool = True,
    random_state: int | None = None,
) -> BootstrapCI:
    """
    Calculate bootstrap CI for the difference between two samples.

    Args:
        x: First sample array
        y: Second sample array
        statistic: Function to compute statistic (default: mean)
        n_iterations: Number of bootstrap iterations
        confidence: Confidence level
        paired: Whether samples are paired
        random_state: Random seed for reproducibility

    Returns:
        BootstrapCI for the difference
    """
    if random_state is not None:
        np.random.seed(random_state)

    # Remove NaN values
    if paired:
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]
        n = len(x_clean)
    else:
        x_clean = x[~np.isnan(x)]
        y_clean = y[~np.isnan(y)]

    if len(x_clean) == 0 or len(y_clean) == 0:
        return BootstrapCI(
            statistic="difference",
            point_estimate=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            confidence_level=confidence,
            n_iterations=n_iterations,
        )

    # Point estimate
    point_estimate = statistic(x_clean) - statistic(y_clean)

    # Bootstrap resampling
    bootstrap_diffs = []

    for _ in range(n_iterations):
        if paired:
            indices = np.random.randint(0, n, n)
            x_sample = x_clean[indices]
            y_sample = y_clean[indices]
        else:
            x_sample = np.random.choice(x_clean, size=len(x_clean), replace=True)
            y_sample = np.random.choice(y_clean, size=len(y_clean), replace=True)

        diff = statistic(x_sample) - statistic(y_sample)
        bootstrap_diffs.append(diff)

    bootstrap_diffs = np.array(bootstrap_diffs)

    # Calculate percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_diffs, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_diffs, (1 - alpha / 2) * 100)

    return BootstrapCI(
        statistic="difference",
        point_estimate=float(point_estimate),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence,
        n_iterations=n_iterations,
    )


def bootstrap_correlation(
    x: np.ndarray,
    y: np.ndarray,
    method: str = "pearson",
    n_iterations: int = 10000,
    confidence: float = 0.95,
    random_state: int | None = None,
) -> BootstrapCI:
    """
    Calculate bootstrap CI for correlation coefficient.

    Args:
        x: First variable array
        y: Second variable array
        method: Correlation method ("pearson" or "spearman")
        n_iterations: Number of bootstrap iterations
        confidence: Confidence level
        random_state: Random seed for reproducibility

    Returns:
        BootstrapCI for the correlation
    """
    from scipy import stats as sp_stats

    if random_state is not None:
        np.random.seed(random_state)

    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]
    n = len(x_clean)

    if n < 3:
        return BootstrapCI(
            statistic=f"{method}_correlation",
            point_estimate=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            confidence_level=confidence,
            n_iterations=n_iterations,
        )

    # Point estimate
    if method == "pearson":
        point_estimate, _ = sp_stats.pearsonr(x_clean, y_clean)
    else:
        point_estimate, _ = sp_stats.spearmanr(x_clean, y_clean)

    # Bootstrap resampling
    bootstrap_corrs = []

    for _ in range(n_iterations):
        indices = np.random.randint(0, n, n)
        x_sample = x_clean[indices]
        y_sample = y_clean[indices]

        try:
            if method == "pearson":
                r, _ = sp_stats.pearsonr(x_sample, y_sample)
            else:
                r, _ = sp_stats.spearmanr(x_sample, y_sample)
            bootstrap_corrs.append(r)
        except Exception:
            # Skip failed iterations
            continue

    if len(bootstrap_corrs) == 0:
        return BootstrapCI(
            statistic=f"{method}_correlation",
            point_estimate=float(point_estimate),
            ci_lower=float(point_estimate),
            ci_upper=float(point_estimate),
            confidence_level=confidence,
            n_iterations=n_iterations,
        )

    bootstrap_corrs = np.array(bootstrap_corrs)

    # Calculate percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_corrs, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_corrs, (1 - alpha / 2) * 100)

    return BootstrapCI(
        statistic=f"{method}_correlation",
        point_estimate=float(point_estimate),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence,
        n_iterations=n_iterations,
    )


def bootstrap_effect_size(
    x: np.ndarray,
    y: np.ndarray,
    effect_func: Callable[[np.ndarray, np.ndarray], float],
    n_iterations: int = 10000,
    confidence: float = 0.95,
    paired: bool = True,
    random_state: int | None = None,
) -> BootstrapCI:
    """
    Calculate bootstrap CI for any effect size measure.

    Args:
        x: First sample array
        y: Second sample array
        effect_func: Function that takes (x, y) and returns effect size
        n_iterations: Number of bootstrap iterations
        confidence: Confidence level
        paired: Whether samples are paired
        random_state: Random seed for reproducibility

    Returns:
        BootstrapCI for the effect size
    """
    if random_state is not None:
        np.random.seed(random_state)

    # Remove NaN values
    if paired:
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]
        n = len(x_clean)
    else:
        x_clean = x[~np.isnan(x)]
        y_clean = y[~np.isnan(y)]

    # Point estimate
    point_estimate = effect_func(x_clean, y_clean)

    # Bootstrap resampling
    bootstrap_effects = []

    for _ in range(n_iterations):
        if paired:
            indices = np.random.randint(0, n, n)
            x_sample = x_clean[indices]
            y_sample = y_clean[indices]
        else:
            x_sample = np.random.choice(x_clean, size=len(x_clean), replace=True)
            y_sample = np.random.choice(y_clean, size=len(y_clean), replace=True)

        try:
            effect = effect_func(x_sample, y_sample)
            bootstrap_effects.append(effect)
        except Exception:
            continue

    bootstrap_effects = np.array(bootstrap_effects)

    # Calculate percentile CI
    alpha = 1 - confidence
    ci_lower = np.percentile(bootstrap_effects, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_effects, (1 - alpha / 2) * 100)

    func_name = getattr(effect_func, "__name__", "effect_size")

    return BootstrapCI(
        statistic=func_name,
        point_estimate=float(point_estimate),
        ci_lower=float(ci_lower),
        ci_upper=float(ci_upper),
        confidence_level=confidence,
        n_iterations=n_iterations,
    )

"""Effect size calculations for format comparison."""

from __future__ import annotations

import numpy as np

from metaeval.core.types import EffectSize
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def interpret_cohens_d(value: float) -> str:
    """
    Interpret Cohen's d effect size.

    Args:
        value: Cohen's d value

    Returns:
        Interpretation string
    """
    abs_value = abs(value)
    if abs_value < 0.2:
        return "negligible"
    elif abs_value < 0.5:
        return "small"
    elif abs_value < 0.8:
        return "medium"
    else:
        return "large"


def cohens_d(
    x: np.ndarray,
    y: np.ndarray,
    paired: bool = True,
) -> EffectSize:
    """
    Calculate Cohen's d effect size.

    For paired samples, uses the standard deviation of differences.
    For independent samples, uses pooled standard deviation.

    Args:
        x: First sample array
        y: Second sample array
        paired: Whether samples are paired

    Returns:
        EffectSize with Cohen's d value and interpretation
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 2:
        return EffectSize(measure="cohens_d", value=0.0, interpretation="negligible")

    mean_diff = np.mean(x_clean) - np.mean(y_clean)

    if paired:
        # For paired samples, use SD of differences
        diff = x_clean - y_clean
        sd = np.std(diff, ddof=1)
    else:
        # For independent samples, use pooled SD
        n1, n2 = len(x_clean), len(y_clean)
        var1 = np.var(x_clean, ddof=1)
        var2 = np.var(y_clean, ddof=1)
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)
        sd = np.sqrt(pooled_var)

    if sd == 0:
        d = 0.0
    else:
        d = mean_diff / sd

    return EffectSize(
        measure="cohens_d",
        value=float(d),
        interpretation=interpret_cohens_d(d),
    )


def hedges_g(
    x: np.ndarray,
    y: np.ndarray,
    paired: bool = True,
) -> EffectSize:
    """
    Calculate Hedges' g effect size (bias-corrected Cohen's d).

    Applies small sample correction to Cohen's d.

    Args:
        x: First sample array
        y: Second sample array
        paired: Whether samples are paired

    Returns:
        EffectSize with Hedges' g value and interpretation
    """
    # Get Cohen's d first
    d_result = cohens_d(x, y, paired)
    d = d_result.value

    # Apply correction factor
    mask = ~(np.isnan(x) | np.isnan(y))
    n = np.sum(mask)

    if paired:
        df = n - 1
    else:
        df = 2 * n - 2

    # Correction factor (approximation)
    if df > 0:
        correction = 1 - (3 / (4 * df - 1))
    else:
        correction = 1

    g = d * correction

    return EffectSize(
        measure="hedges_g",
        value=float(g),
        interpretation=interpret_cohens_d(g),  # Same interpretation scale
    )


def glass_delta(
    x: np.ndarray,
    y: np.ndarray,
    control_group: int = 1,
) -> EffectSize:
    """
    Calculate Glass's delta effect size.

    Uses only the control group's standard deviation as denominator.
    Useful when group variances differ substantially.

    Args:
        x: Treatment/experimental group array
        y: Control group array
        control_group: Which group to use as control (1 for x, 2 for y)

    Returns:
        EffectSize with Glass's delta value and interpretation
    """
    # Remove NaN values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 2:
        return EffectSize(measure="glass_delta", value=0.0, interpretation="negligible")

    mean_diff = np.mean(x_clean) - np.mean(y_clean)

    if control_group == 1:
        sd_control = np.std(x_clean, ddof=1)
    else:
        sd_control = np.std(y_clean, ddof=1)

    if sd_control == 0:
        delta = 0.0
    else:
        delta = mean_diff / sd_control

    return EffectSize(
        measure="glass_delta",
        value=float(delta),
        interpretation=interpret_cohens_d(delta),
    )


def common_language_effect_size(
    x: np.ndarray,
    y: np.ndarray,
) -> EffectSize:
    """
    Calculate Common Language Effect Size (CLES).

    The probability that a randomly selected value from x
    is greater than a randomly selected value from y.

    Args:
        x: First sample array
        y: Second sample array

    Returns:
        EffectSize with CLES value (0-1) and interpretation
    """
    # Remove NaN values
    mask_x = ~np.isnan(x)
    mask_y = ~np.isnan(y)
    x_clean = x[mask_x]
    y_clean = y[mask_y]

    if len(x_clean) == 0 or len(y_clean) == 0:
        return EffectSize(measure="cles", value=0.5, interpretation="negligible")

    # Count pairs where x > y
    count = 0
    ties = 0
    total = len(x_clean) * len(y_clean)

    for xi in x_clean:
        count += np.sum(xi > y_clean)
        ties += np.sum(xi == y_clean)

    # CLES = P(x > y) + 0.5 * P(x = y)
    cles = (count + 0.5 * ties) / total

    # Interpretation based on deviation from 0.5
    deviation = abs(cles - 0.5)
    if deviation < 0.06:
        interpretation = "negligible"
    elif deviation < 0.14:
        interpretation = "small"
    elif deviation < 0.21:
        interpretation = "medium"
    else:
        interpretation = "large"

    return EffectSize(
        measure="cles",
        value=float(cles),
        interpretation=interpretation,
    )


def probability_of_superiority(
    x: np.ndarray,
    y: np.ndarray,
) -> float:
    """
    Calculate probability of superiority (same as CLES).

    Alias for common_language_effect_size.

    Args:
        x: First sample array
        y: Second sample array

    Returns:
        Probability value (0-1)
    """
    return common_language_effect_size(x, y).value


def compute_all_effect_sizes(
    x: np.ndarray,
    y: np.ndarray,
    paired: bool = True,
) -> dict[str, EffectSize]:
    """
    Compute all effect sizes for a comparison.

    Args:
        x: First sample array
        y: Second sample array
        paired: Whether samples are paired

    Returns:
        Dictionary of effect sizes by name
    """
    return {
        "cohens_d": cohens_d(x, y, paired),
        "hedges_g": hedges_g(x, y, paired),
        "glass_delta": glass_delta(x, y),
        "cles": common_language_effect_size(x, y),
    }

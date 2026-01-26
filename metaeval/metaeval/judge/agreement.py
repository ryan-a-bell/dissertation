"""Inter-rater agreement metrics for LLM judges."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgreementResult:
    """Result from agreement calculation."""

    metric: str
    value: float
    interpretation: str
    n_raters: int
    n_items: int
    additional_info: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric": self.metric,
            "value": self.value,
            "interpretation": self.interpretation,
            "n_raters": self.n_raters,
            "n_items": self.n_items,
            **self.additional_info,
        }


def interpret_kappa(kappa: float) -> str:
    """
    Interpret kappa value using Landis & Koch guidelines.

    Args:
        kappa: Kappa coefficient

    Returns:
        Interpretation string
    """
    if kappa < 0:
        return "poor"
    elif kappa < 0.20:
        return "slight"
    elif kappa < 0.40:
        return "fair"
    elif kappa < 0.60:
        return "moderate"
    elif kappa < 0.80:
        return "substantial"
    else:
        return "almost perfect"


def interpret_icc(icc: float) -> str:
    """
    Interpret ICC value using Cicchetti guidelines.

    Args:
        icc: ICC coefficient

    Returns:
        Interpretation string
    """
    if icc < 0.40:
        return "poor"
    elif icc < 0.60:
        return "fair"
    elif icc < 0.75:
        return "good"
    else:
        return "excellent"


def cohens_kappa(
    rater1: np.ndarray | list,
    rater2: np.ndarray | list,
) -> AgreementResult:
    """
    Calculate Cohen's kappa for two raters.

    Args:
        rater1: Ratings from first rater
        rater2: Ratings from second rater

    Returns:
        AgreementResult with kappa value
    """
    r1 = np.array(rater1)
    r2 = np.array(rater2)

    if len(r1) != len(r2):
        raise ValueError("Raters must have same number of ratings")

    # Get unique categories
    categories = np.unique(np.concatenate([r1, r2]))
    n = len(r1)

    # Build confusion matrix
    confusion = np.zeros((len(categories), len(categories)))
    for i, j in zip(r1, r2):
        idx_i = np.where(categories == i)[0][0]
        idx_j = np.where(categories == j)[0][0]
        confusion[idx_i, idx_j] += 1

    # Calculate observed agreement
    po = np.trace(confusion) / n

    # Calculate expected agreement
    row_sums = confusion.sum(axis=1)
    col_sums = confusion.sum(axis=0)
    pe = np.sum((row_sums * col_sums) / n) / n

    # Calculate kappa
    if pe == 1:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1 - pe)

    return AgreementResult(
        metric="cohens_kappa",
        value=float(kappa),
        interpretation=interpret_kappa(kappa),
        n_raters=2,
        n_items=n,
        additional_info={
            "observed_agreement": float(po),
            "expected_agreement": float(pe),
        },
    )


def fleiss_kappa(
    ratings: np.ndarray,
) -> AgreementResult:
    """
    Calculate Fleiss' kappa for multiple raters.

    Args:
        ratings: 2D array where rows are items and columns are raters

    Returns:
        AgreementResult with kappa value
    """
    ratings = np.array(ratings)
    n_items, n_raters = ratings.shape

    # Get unique categories
    categories = np.unique(ratings)
    n_categories = len(categories)

    # Create category count matrix
    # counts[i, j] = number of raters who assigned category j to item i
    counts = np.zeros((n_items, n_categories))
    for i in range(n_items):
        for k, cat in enumerate(categories):
            counts[i, k] = np.sum(ratings[i] == cat)

    # Calculate P_i (agreement for each item)
    P_i = (1 / (n_raters * (n_raters - 1))) * (
        np.sum(counts ** 2, axis=1) - n_raters
    )

    # Calculate P_bar (mean agreement)
    P_bar = np.mean(P_i)

    # Calculate p_j (proportion of all assignments to category j)
    p_j = np.sum(counts, axis=0) / (n_items * n_raters)

    # Calculate P_e (expected agreement)
    P_e = np.sum(p_j ** 2)

    # Calculate kappa
    if P_e == 1:
        kappa = 1.0
    else:
        kappa = (P_bar - P_e) / (1 - P_e)

    return AgreementResult(
        metric="fleiss_kappa",
        value=float(kappa),
        interpretation=interpret_kappa(kappa),
        n_raters=n_raters,
        n_items=n_items,
        additional_info={
            "P_bar": float(P_bar),
            "P_e": float(P_e),
            "category_proportions": p_j.tolist(),
        },
    )


def krippendorff_alpha(
    ratings: np.ndarray,
    level: str = "interval",
) -> AgreementResult:
    """
    Calculate Krippendorff's alpha.

    Args:
        ratings: 2D array (items x raters), NaN for missing
        level: Measurement level ("nominal", "ordinal", "interval", "ratio")

    Returns:
        AgreementResult with alpha value
    """
    ratings = np.array(ratings, dtype=float)
    n_items, n_raters = ratings.shape

    # Define distance functions
    def nominal_distance(v1, v2):
        return 0 if v1 == v2 else 1

    def interval_distance(v1, v2):
        return (v1 - v2) ** 2

    def ordinal_distance(v1, v2):
        return (v1 - v2) ** 2  # Simplified

    def ratio_distance(v1, v2):
        return ((v1 - v2) / (v1 + v2)) ** 2 if (v1 + v2) != 0 else 0

    distance_funcs = {
        "nominal": nominal_distance,
        "ordinal": ordinal_distance,
        "interval": interval_distance,
        "ratio": ratio_distance,
    }
    distance = distance_funcs.get(level, interval_distance)

    # Calculate observed disagreement
    Do = 0
    n_pairs = 0

    for i in range(n_items):
        valid = ratings[i][~np.isnan(ratings[i])]
        if len(valid) >= 2:
            for v1, v2 in combinations(valid, 2):
                Do += distance(v1, v2)
                n_pairs += 1

    if n_pairs > 0:
        Do /= n_pairs

    # Calculate expected disagreement
    all_valid = ratings[~np.isnan(ratings)]
    De = 0
    n_total_pairs = 0

    for v1, v2 in combinations(all_valid, 2):
        De += distance(v1, v2)
        n_total_pairs += 1

    if n_total_pairs > 0:
        De /= n_total_pairs

    # Calculate alpha
    if De == 0:
        alpha = 1.0
    else:
        alpha = 1 - (Do / De)

    return AgreementResult(
        metric="krippendorff_alpha",
        value=float(alpha),
        interpretation=interpret_kappa(alpha),
        n_raters=n_raters,
        n_items=n_items,
        additional_info={
            "level": level,
            "observed_disagreement": float(Do),
            "expected_disagreement": float(De),
        },
    )


def intraclass_correlation(
    ratings: np.ndarray,
    model: str = "two_way_random",
    agreement: str = "consistency",
) -> AgreementResult:
    """
    Calculate Intraclass Correlation Coefficient (ICC).

    Args:
        ratings: 2D array (items x raters)
        model: ICC model ("one_way", "two_way_random", "two_way_fixed")
        agreement: Type ("consistency" or "absolute")

    Returns:
        AgreementResult with ICC value
    """
    ratings = np.array(ratings, dtype=float)
    n_items, n_raters = ratings.shape

    # Calculate means
    grand_mean = np.nanmean(ratings)
    item_means = np.nanmean(ratings, axis=1)
    rater_means = np.nanmean(ratings, axis=0)

    # Calculate sum of squares
    # Between items
    SS_items = n_raters * np.sum((item_means - grand_mean) ** 2)

    # Between raters
    SS_raters = n_items * np.sum((rater_means - grand_mean) ** 2)

    # Total
    SS_total = np.nansum((ratings - grand_mean) ** 2)

    # Error (residual)
    SS_error = SS_total - SS_items - SS_raters

    # Mean squares
    MS_items = SS_items / (n_items - 1)
    MS_raters = SS_raters / (n_raters - 1)
    MS_error = SS_error / ((n_items - 1) * (n_raters - 1))

    # Calculate ICC based on model
    if model == "one_way":
        # ICC(1,1)
        MS_within = (SS_total - SS_items) / (n_items * (n_raters - 1))
        icc = (MS_items - MS_within) / (MS_items + (n_raters - 1) * MS_within)

    elif model == "two_way_random":
        if agreement == "consistency":
            # ICC(2,1) consistency
            icc = (MS_items - MS_error) / (MS_items + (n_raters - 1) * MS_error)
        else:
            # ICC(2,1) absolute agreement
            icc = (MS_items - MS_error) / (
                MS_items + (n_raters - 1) * MS_error +
                n_raters * (MS_raters - MS_error) / n_items
            )

    elif model == "two_way_fixed":
        if agreement == "consistency":
            # ICC(3,1) consistency
            icc = (MS_items - MS_error) / (MS_items + (n_raters - 1) * MS_error)
        else:
            # ICC(3,1) absolute agreement
            icc = (MS_items - MS_error) / (MS_items + (n_raters - 1) * MS_error)

    else:
        icc = 0.0

    return AgreementResult(
        metric="icc",
        value=float(icc),
        interpretation=interpret_icc(icc),
        n_raters=n_raters,
        n_items=n_items,
        additional_info={
            "model": model,
            "agreement_type": agreement,
            "MS_items": float(MS_items),
            "MS_raters": float(MS_raters),
            "MS_error": float(MS_error),
        },
    )


def pairwise_agreement(
    ratings: np.ndarray,
    metric: str = "kappa",
) -> list[tuple[int, int, AgreementResult]]:
    """
    Calculate pairwise agreement between all rater pairs.

    Args:
        ratings: 2D array (items x raters)
        metric: Agreement metric ("kappa", "correlation", "percent")

    Returns:
        List of (rater1_idx, rater2_idx, AgreementResult)
    """
    ratings = np.array(ratings)
    n_raters = ratings.shape[1]

    results = []

    for i, j in combinations(range(n_raters), 2):
        r1 = ratings[:, i]
        r2 = ratings[:, j]

        # Remove pairs with missing values
        valid = ~(np.isnan(r1) | np.isnan(r2))
        r1_valid = r1[valid]
        r2_valid = r2[valid]

        if metric == "kappa":
            # Discretize for kappa
            r1_disc = np.round(r1_valid).astype(int)
            r2_disc = np.round(r2_valid).astype(int)
            result = cohens_kappa(r1_disc, r2_disc)

        elif metric == "correlation":
            from scipy import stats
            corr, p = stats.spearmanr(r1_valid, r2_valid)
            result = AgreementResult(
                metric="spearman_correlation",
                value=float(corr),
                interpretation="strong" if abs(corr) > 0.7 else "moderate" if abs(corr) > 0.4 else "weak",
                n_raters=2,
                n_items=len(r1_valid),
                additional_info={"p_value": float(p)},
            )

        elif metric == "percent":
            # Percent exact agreement (within tolerance)
            tolerance = 5  # Within 5 points
            agree = np.abs(r1_valid - r2_valid) <= tolerance
            pct = np.mean(agree)
            result = AgreementResult(
                metric="percent_agreement",
                value=float(pct),
                interpretation="high" if pct > 0.8 else "moderate" if pct > 0.6 else "low",
                n_raters=2,
                n_items=len(r1_valid),
                additional_info={"tolerance": tolerance},
            )

        else:
            continue

        results.append((i, j, result))

    return results

"""Data alignment utilities for format comparison."""

from __future__ import annotations

from typing import Any

import pandas as pd

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def align_results(
    mcq_data: pd.DataFrame,
    osq_data: pd.DataFrame,
    key: str = "question_id",
    model_key: str = "model",
    mcq_score_col: str = "is_correct",
    osq_score_col: str = "total_score",
) -> pd.DataFrame:
    """
    Align MCQ and OSQ results by question and model.

    Args:
        mcq_data: DataFrame with MCQ results
        osq_data: DataFrame with OSQ results
        key: Column to join on (question identifier)
        model_key: Column for model name
        mcq_score_col: Column name for MCQ score/correctness
        osq_score_col: Column name for OSQ score

    Returns:
        Aligned DataFrame with both MCQ and OSQ scores
    """
    # Ensure required columns exist
    for col in [key, model_key, mcq_score_col]:
        if col not in mcq_data.columns:
            raise ValueError(f"MCQ data missing required column: {col}")

    for col in [key, model_key, osq_score_col]:
        if col not in osq_data.columns:
            raise ValueError(f"OSQ data missing required column: {col}")

    # Select relevant columns
    mcq_subset = mcq_data[[key, model_key, mcq_score_col]].copy()
    mcq_subset = mcq_subset.rename(columns={mcq_score_col: "mcq_score"})

    osq_subset = osq_data[[key, model_key, osq_score_col]].copy()
    osq_subset = osq_subset.rename(columns={osq_score_col: "osq_score"})

    # Merge on key and model
    aligned = mcq_subset.merge(osq_subset, on=[key, model_key], how="inner")

    logger.info(
        f"Aligned {len(aligned)} results from {len(mcq_data)} MCQ and {len(osq_data)} OSQ records"
    )

    return aligned


def merge_mcq_osq(
    mcq_data: pd.DataFrame,
    osq_data: pd.DataFrame,
    key: str = "question_id",
    suffixes: tuple[str, str] = ("_mcq", "_osq"),
) -> pd.DataFrame:
    """
    Merge MCQ and OSQ datasets preserving all columns.

    Args:
        mcq_data: DataFrame with MCQ data
        osq_data: DataFrame with OSQ data
        key: Column to join on
        suffixes: Suffixes for overlapping column names

    Returns:
        Merged DataFrame
    """
    merged = mcq_data.merge(osq_data, on=key, how="outer", suffixes=suffixes)

    logger.info(f"Merged datasets: {len(merged)} total records")
    return merged


def filter_common_questions(
    mcq_data: pd.DataFrame,
    osq_data: pd.DataFrame,
    key: str = "question_id",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Filter both datasets to only include questions present in both.

    Args:
        mcq_data: DataFrame with MCQ data
        osq_data: DataFrame with OSQ data
        key: Column to compare

    Returns:
        Tuple of (filtered_mcq, filtered_osq) DataFrames
    """
    common_keys = set(mcq_data[key]) & set(osq_data[key])

    mcq_filtered = mcq_data[mcq_data[key].isin(common_keys)].copy()
    osq_filtered = osq_data[osq_data[key].isin(common_keys)].copy()

    logger.info(
        f"Filtered to {len(common_keys)} common questions: "
        f"MCQ {len(mcq_data)} -> {len(mcq_filtered)}, "
        f"OSQ {len(osq_data)} -> {len(osq_filtered)}"
    )

    return mcq_filtered, osq_filtered


def aggregate_by_model(
    data: pd.DataFrame,
    model_col: str = "model",
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
) -> pd.DataFrame:
    """
    Aggregate aligned data by model.

    Args:
        data: Aligned DataFrame
        model_col: Column name for model
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores

    Returns:
        Aggregated DataFrame with mean scores per model
    """
    agg = data.groupby(model_col).agg(
        mcq_mean=(mcq_col, "mean"),
        mcq_std=(mcq_col, "std"),
        osq_mean=(osq_col, "mean"),
        osq_std=(osq_col, "std"),
        n=(mcq_col, "count"),
    ).reset_index()

    return agg


def aggregate_by_category(
    data: pd.DataFrame,
    category_col: str = "incose_category",
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
) -> pd.DataFrame:
    """
    Aggregate aligned data by category.

    Args:
        data: Aligned DataFrame with category information
        category_col: Column name for category
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores

    Returns:
        Aggregated DataFrame with mean scores per category
    """
    if category_col not in data.columns:
        logger.warning(f"Category column {category_col} not found")
        return pd.DataFrame()

    agg = data.groupby(category_col).agg(
        mcq_mean=(mcq_col, "mean"),
        osq_mean=(osq_col, "mean"),
        n=(mcq_col, "count"),
    ).reset_index()

    return agg


def pivot_for_correlation(
    data: pd.DataFrame,
    model_col: str = "model",
    score_col: str = "osq_score",
    question_col: str = "question_id",
) -> pd.DataFrame:
    """
    Pivot data for correlation analysis between models.

    Args:
        data: DataFrame with results
        model_col: Column name for model
        score_col: Column name for score
        question_col: Column name for question

    Returns:
        Pivoted DataFrame with models as columns
    """
    pivoted = data.pivot_table(
        index=question_col,
        columns=model_col,
        values=score_col,
        aggfunc="first",
    )

    return pivoted

"""Benchmark download and loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BenchmarkStats:
    """Statistics about a benchmark dataset."""

    total_questions: int
    categories: dict[str, int]
    answer_distribution: dict[str, int]
    avg_question_length: float
    avg_choice_length: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_questions": self.total_questions,
            "categories": self.categories,
            "answer_distribution": self.answer_distribution,
            "avg_question_length": self.avg_question_length,
            "avg_choice_length": self.avg_choice_length,
        }


def download_benchmark(
    dataset_id: str,
    split: str = "test",
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """
    Download a benchmark dataset from HuggingFace.

    Args:
        dataset_id: HuggingFace dataset identifier (e.g., "ryan-a-bell/SysEngBench")
        split: Dataset split to download (default: "test")
        cache_dir: Optional cache directory

    Returns:
        DataFrame containing the benchmark questions
    """
    logger.info(f"Downloading benchmark: {dataset_id}")

    cache_path = str(cache_dir) if cache_dir else None
    dataset = load_dataset(dataset_id, split=split, cache_dir=cache_path)

    df = pd.DataFrame(dataset)
    logger.info(f"Downloaded {len(df)} questions from {dataset_id}")

    return df


def load_benchmark(path: Path | str) -> pd.DataFrame:
    """
    Load a benchmark dataset from a local file.

    Args:
        path: Path to CSV or JSON file

    Returns:
        DataFrame containing the benchmark questions
    """
    path = Path(path)

    if path.suffix == ".csv":
        df = pd.read_csv(path)
    elif path.suffix == ".json":
        df = pd.read_json(path)
    elif path.suffix == ".jsonl":
        df = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    logger.info(f"Loaded {len(df)} questions from {path}")
    return df


def explode_categories(
    df: pd.DataFrame,
    category_column: str = "incose_handbook_category",
    delimiter: str = ";",
) -> pd.DataFrame:
    """
    Expand multi-category questions into separate rows.

    Some questions may belong to multiple categories (semicolon-separated).
    This function creates separate rows for each category.

    Args:
        df: DataFrame with questions
        category_column: Column containing categories
        delimiter: Delimiter for multiple categories

    Returns:
        DataFrame with exploded categories
    """
    if category_column not in df.columns:
        logger.warning(f"Column {category_column} not found, returning original DataFrame")
        return df

    # Split categories and explode
    df = df.copy()
    df[category_column] = df[category_column].fillna("").astype(str)
    df[category_column] = df[category_column].str.split(delimiter)
    df = df.explode(category_column)

    # Clean up whitespace
    df[category_column] = df[category_column].str.strip()

    # Remove empty categories
    df = df[df[category_column] != ""]

    logger.info(f"Exploded categories: {len(df)} rows")
    return df


def get_benchmark_stats(df: pd.DataFrame) -> BenchmarkStats:
    """
    Calculate statistics for a benchmark dataset.

    Args:
        df: DataFrame containing benchmark questions

    Returns:
        BenchmarkStats with computed statistics
    """
    # Category distribution
    category_col = None
    for col in ["incose_category", "incose_handbook_category", "category"]:
        if col in df.columns:
            category_col = col
            break

    if category_col:
        categories = df[category_col].value_counts().to_dict()
    else:
        categories = {}

    # Answer distribution
    answer_col = "answer" if "answer" in df.columns else None
    if answer_col:
        answer_dist = df[answer_col].value_counts().to_dict()
    else:
        answer_dist = {}

    # Question length
    question_col = "question" if "question" in df.columns else None
    if question_col:
        avg_q_len = df[question_col].str.len().mean()
    else:
        avg_q_len = 0.0

    # Choice length
    choice_cols = [c for c in df.columns if c.startswith("choice_")]
    if choice_cols:
        choice_lengths = []
        for col in choice_cols:
            choice_lengths.extend(df[col].str.len().tolist())
        avg_c_len = sum(choice_lengths) / len(choice_lengths) if choice_lengths else 0.0
    else:
        avg_c_len = 0.0

    return BenchmarkStats(
        total_questions=len(df),
        categories=categories,
        answer_distribution=answer_dist,
        avg_question_length=avg_q_len,
        avg_choice_length=avg_c_len,
    )

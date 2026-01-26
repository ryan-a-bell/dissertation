"""Position variant generation for MCQ benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VariantStats:
    """Statistics about generated variants."""

    variant_name: str
    num_questions: int
    target_position: str
    answer_distribution: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variant_name": self.variant_name,
            "num_questions": self.num_questions,
            "target_position": self.target_position,
            "answer_distribution": self.answer_distribution,
        }


def rotate_choices(
    choices: dict[str, str],
    current_answer: str,
    target_position: str,
) -> tuple[dict[str, str], str]:
    """
    Rotate choices so the correct answer is at the target position.

    Args:
        choices: Dictionary of current choices (A, B, C, D)
        current_answer: Current position of correct answer
        target_position: Desired position for correct answer

    Returns:
        Tuple of (new_choices, new_answer)
    """
    positions = ["A", "B", "C", "D"]

    # Get the choice values in order
    choice_values = [choices.get(p, "") for p in positions]

    # Find current answer index
    current_idx = positions.index(current_answer)

    # Find target index
    target_idx = positions.index(target_position)

    # Calculate rotation amount
    rotation = target_idx - current_idx

    # Rotate the choices
    rotated_values = choice_values[-rotation:] + choice_values[:-rotation] if rotation else choice_values

    # Build new choices dict
    new_choices = {p: v for p, v in zip(positions, rotated_values)}

    return new_choices, target_position


def create_variant(
    df: pd.DataFrame,
    target_position: str,
    question_col: str = "question",
    answer_col: str = "answer",
) -> pd.DataFrame:
    """
    Create a variant where all correct answers are at the target position.

    Args:
        df: DataFrame with MCQ questions
        target_position: Target position for correct answers (A, B, C, D)
        question_col: Column name for question text
        answer_col: Column name for answer

    Returns:
        DataFrame with rotated choices
    """
    if target_position not in ["A", "B", "C", "D"]:
        raise ValueError(f"Invalid target position: {target_position}")

    result_rows = []

    for _, row in df.iterrows():
        new_row = row.to_dict()

        # Get current choices
        choices = {}
        for letter in ["A", "B", "C", "D"]:
            col = f"choice_{letter.lower()}"
            if col in row:
                choices[letter] = row[col]

        current_answer = row[answer_col]

        # Rotate choices
        new_choices, new_answer = rotate_choices(
            choices=choices,
            current_answer=current_answer,
            target_position=target_position,
        )

        # Update row with new choices
        for letter, value in new_choices.items():
            new_row[f"choice_{letter.lower()}"] = value

        new_row[answer_col] = new_answer
        result_rows.append(new_row)

    result_df = pd.DataFrame(result_rows)
    logger.info(f"Created variant with answer at position {target_position}: {len(result_df)} questions")

    return result_df


def create_position_variants(
    df: pd.DataFrame,
    question_col: str = "question",
    answer_col: str = "answer",
) -> dict[str, pd.DataFrame]:
    """
    Create all four position variants (A, B, C, D).

    Args:
        df: DataFrame with MCQ questions
        question_col: Column name for question text
        answer_col: Column name for answer

    Returns:
        Dictionary mapping position to variant DataFrame
    """
    variants = {}

    for position in ["A", "B", "C", "D"]:
        variants[position] = create_variant(
            df=df,
            target_position=position,
            question_col=question_col,
            answer_col=answer_col,
        )

    logger.info(f"Created {len(variants)} position variants")
    return variants


def get_variant_stats(
    variants: dict[str, pd.DataFrame],
    answer_col: str = "answer",
) -> list[VariantStats]:
    """
    Get statistics for each variant.

    Args:
        variants: Dictionary of position variants
        answer_col: Column name for answer

    Returns:
        List of VariantStats for each variant
    """
    stats = []

    for position, df in variants.items():
        answer_dist = df[answer_col].value_counts().to_dict()

        stats.append(VariantStats(
            variant_name=f"variant_{position.lower()}",
            num_questions=len(df),
            target_position=position,
            answer_distribution=answer_dist,
        ))

    return stats


def save_variants(
    variants: dict[str, pd.DataFrame],
    output_dir: str,
    prefix: str = "benchmark",
) -> dict[str, str]:
    """
    Save variants to CSV files.

    Args:
        variants: Dictionary of position variants
        output_dir: Output directory
        prefix: Filename prefix

    Returns:
        Dictionary mapping position to file path
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    paths = {}

    for position, df in variants.items():
        filename = f"{prefix}_{position.lower()}.csv"
        filepath = output_path / filename
        df.to_csv(filepath, index=False)
        paths[position] = str(filepath)
        logger.info(f"Saved variant {position} to {filepath}")

    return paths

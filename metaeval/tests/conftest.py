"""Pytest fixtures for metaeval tests."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_mcq_data() -> pd.DataFrame:
    """Create sample MCQ data for testing."""
    np.random.seed(42)
    n_questions = 100
    n_models = 3
    positions = ["A", "B", "C", "D"]

    data = []
    for model_idx in range(n_models):
        model = f"model_{model_idx}"
        for q_id in range(n_questions):
            for pos in positions:
                # Simulate some position bias
                bias = 0.1 if pos == "A" else 0.0
                correct = np.random.random() < (0.7 + bias)
                data.append({
                    "question_id": q_id,
                    "model": model,
                    "variant": pos,
                    "is_correct": int(correct),
                })

    return pd.DataFrame(data)


@pytest.fixture
def sample_osq_data() -> pd.DataFrame:
    """Create sample OSQ judged data for testing."""
    np.random.seed(42)
    n_questions = 100
    n_models = 3

    data = []
    for model_idx in range(n_models):
        model = f"model_{model_idx}"
        for q_id in range(n_questions):
            score = np.random.randint(30, 100)
            data.append({
                "question_id": q_id,
                "model": model,
                "total_score": score,
                "technical_accuracy": np.random.randint(5, 20),
                "conceptual_understanding": np.random.randint(5, 20),
                "completeness": np.random.randint(5, 20),
                "clarity_organization": np.random.randint(5, 20),
                "professional_relevance": np.random.randint(5, 20),
            })

    return pd.DataFrame(data)


@pytest.fixture
def sample_aligned_data(sample_mcq_data, sample_osq_data) -> pd.DataFrame:
    """Create aligned MCQ/OSQ data for testing."""
    # Get MCQ accuracy (average across positions)
    mcq_agg = sample_mcq_data.groupby(["question_id", "model"])["is_correct"].mean().reset_index()
    mcq_agg = mcq_agg.rename(columns={"is_correct": "mcq_score"})

    # Get OSQ scores
    osq_subset = sample_osq_data[["question_id", "model", "total_score"]].copy()
    osq_subset = osq_subset.rename(columns={"total_score": "osq_score"})

    # Merge
    aligned = mcq_agg.merge(osq_subset, on=["question_id", "model"])
    return aligned


@pytest.fixture
def sample_dimension_scores():
    """Create sample dimension scores."""
    from metaeval.core.types import DimensionScores
    return DimensionScores(
        technical_accuracy=18,
        conceptual_understanding=15,
        completeness=16,
        clarity_organization=14,
        professional_relevance=12,
    )


@pytest.fixture
def sample_judgment_response() -> str:
    """Sample LLM judge response for parsing tests."""
    return """{
        "technical_accuracy": 18,
        "conceptual_understanding": 15,
        "completeness": 16,
        "clarity_organization": 14,
        "professional_relevance": 12,
        "total_score": 75,
        "justification": "The response demonstrates good technical understanding..."
    }"""

"""Tests for position variant generation."""

import tempfile
from pathlib import Path

import pytest
import pandas as pd

from metaeval.benchmark.variants import (
    create_position_variants,
    rotate_choices,
    save_variants,
)


class TestRotateChoices:
    """Tests for rotate_choices function."""

    def test_rotation_a(self):
        """Test rotation with A as correct answer."""
        choices = {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta"}
        correct = "A"

        new_choices, new_answer = rotate_choices(choices, correct, target_position="B")
        assert new_choices["B"] == "Alpha"  # Alpha should be at position B
        assert new_answer == "B"

    def test_rotation_preserves_count(self):
        """Test rotation preserves number of choices."""
        choices = {"A": "A1", "B": "B1", "C": "C1", "D": "D1"}
        new_choices, new_answer = rotate_choices(choices, "A", "C")
        assert len(new_choices) == 4

    def test_all_positions(self):
        """Test rotation to all positions."""
        choices = {"A": "First", "B": "Second", "C": "Third", "D": "Fourth"}
        positions = ["A", "B", "C", "D"]

        for pos in positions:
            new_choices, new_answer = rotate_choices(choices, "A", pos)
            assert new_choices[new_answer] == "First"


class TestCreatePositionVariants:
    """Tests for create_position_variants function."""

    @pytest.fixture
    def sample_mcq_df(self):
        """Create sample MCQ dataframe."""
        return pd.DataFrame({
            "question_id": ["q1", "q2"],
            "question": ["Question 1?", "Question 2?"],
            "choice_a": ["A1", "A2"],
            "choice_b": ["B1", "B2"],
            "choice_c": ["C1", "C2"],
            "choice_d": ["D1", "D2"],
            "answer": ["A", "B"],
        })

    def test_creates_four_variants(self, sample_mcq_df):
        """Test that four variants are created."""
        variants = create_position_variants(sample_mcq_df)
        assert len(variants) == 4
        assert set(variants.keys()) == {"A", "B", "C", "D"}

    def test_variant_size(self, sample_mcq_df):
        """Test that each variant has same number of questions."""
        variants = create_position_variants(sample_mcq_df)
        for pos, df in variants.items():
            assert len(df) == len(sample_mcq_df)

    def test_correct_answer_position(self, sample_mcq_df):
        """Test that correct answer moves to expected position."""
        variants = create_position_variants(sample_mcq_df)

        for pos, df in variants.items():
            # All correct answers should be at position `pos`
            assert all(df["answer"] == pos)

    def test_preserves_question_ids(self, sample_mcq_df):
        """Test that question IDs are preserved."""
        variants = create_position_variants(sample_mcq_df)

        for pos, df in variants.items():
            assert set(df["question_id"]) == set(sample_mcq_df["question_id"])


class TestSaveVariants:
    """Tests for save_variants function."""

    @pytest.fixture
    def sample_variants(self):
        """Create sample variants."""
        df = pd.DataFrame({
            "question_id": ["q1"],
            "question": ["Test?"],
            "choice_a": ["A"],
            "choice_b": ["B"],
            "choice_c": ["C"],
            "choice_d": ["D"],
            "answer": ["A"],
        })
        return {
            "A": df.copy(),
            "B": df.copy(),
            "C": df.copy(),
            "D": df.copy(),
        }

    def test_saves_all_variants(self, sample_variants):
        """Test that all variants are saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_variants(sample_variants, tmpdir)

            assert len(paths) == 4
            for pos in ["A", "B", "C", "D"]:
                assert pos in paths
                # paths values are strings, not Path objects
                assert Path(paths[pos]).exists()

    def test_file_contents(self, sample_variants):
        """Test that saved files contain correct data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_variants(sample_variants, tmpdir)

            for pos, path in paths.items():
                df = pd.read_csv(path)
                assert len(df) == 1
                assert "question_id" in df.columns

    def test_custom_prefix(self, sample_variants):
        """Test custom prefix in filenames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_variants(sample_variants, tmpdir, prefix="custom")

            for path in paths.values():
                # path is a string
                assert "custom" in path

    def test_creates_directory(self, sample_variants):
        """Test that output directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new_subdir"
            paths = save_variants(sample_variants, str(new_dir))

            assert new_dir.exists()
            assert len(list(new_dir.glob("*.csv"))) == 4

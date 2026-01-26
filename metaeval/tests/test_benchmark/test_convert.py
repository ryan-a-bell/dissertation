"""Tests for MCQ to OSQ conversion."""

import pytest
import pandas as pd

from metaeval.benchmark.convert import (
    MCQToOSQConverter,
    ConversionResult,
    conversions_to_dataframe,
)
from metaeval.core.types import GradingRubric, BloomsLevel


class TestConversionResult:
    """Tests for ConversionResult dataclass."""

    def test_creation(self):
        """Test creating a conversion result."""
        result = ConversionResult(
            question_id=1,
            original_question="What is SE?",
            original_answer="B",
            osq_prompt="Explain systems engineering.",
            expected_answer="Systems engineering is...",
            rubric={"full_credit": "Complete answer", "partial_credit": "Some points"},
            blooms_level="Understand",
            conversion_score=8,
        )
        assert result.question_id == 1
        assert result.conversion_score == 8
        assert result.blooms_level == "Understand"

    def test_default_conversion_score(self):
        """Test default conversion score is None."""
        result = ConversionResult(
            question_id=1,
            original_question="Test?",
            original_answer="A",
            osq_prompt="Test prompt",
            expected_answer="Test answer",
            rubric={"full": "good"},
            blooms_level="Apply",
        )
        assert result.conversion_score is None


class TestConversionsToDataFrame:
    """Tests for conversions_to_dataframe function."""

    def test_empty_list(self):
        """Test converting empty list."""
        df = conversions_to_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_single_conversion(self):
        """Test converting single result."""
        rubric = GradingRubric(
            full_credit="Full credit response",
            partial_credit="Partial credit response",
            no_credit="No credit response",
        )
        result = ConversionResult(
            question_id=1,
            original_question="Test?",
            original_answer="A",
            osq_prompt="Test prompt",
            expected_answer="Test answer",
            rubric=rubric,
            blooms_level=BloomsLevel.APPLY,
            conversion_score=9,
        )
        df = conversions_to_dataframe([result])

        assert len(df) == 1
        assert df.iloc[0]["question_id"] == 1

    def test_multiple_conversions(self):
        """Test converting multiple results."""
        results = [
            ConversionResult(
                question_id=i,
                original_question=f"Question {i}?",
                original_answer="A",
                osq_prompt=f"Prompt {i}",
                expected_answer=f"Answer {i}",
                rubric=GradingRubric(
                    full_credit="Full",
                    partial_credit="Partial",
                    no_credit="None",
                ),
                blooms_level=BloomsLevel.APPLY,
                conversion_score=i + 5,
            )
            for i in range(5)
        ]
        df = conversions_to_dataframe(results)

        assert len(df) == 5
        assert list(df["question_id"]) == [0, 1, 2, 3, 4]


class TestMCQToOSQConverter:
    """Tests for MCQToOSQConverter class."""

    @pytest.fixture
    def sample_mcq_df(self):
        """Create sample MCQ dataframe."""
        return pd.DataFrame({
            "question_id": ["q1", "q2"],
            "question": [
                "What is systems engineering?",
                "What methodology uses iterative cycles?",
            ],
            "choice_a": ["An art form", "Waterfall"],
            "choice_b": ["A discipline for complex systems", "Agile"],
            "choice_c": ["A programming language", "CMMI"],
            "choice_d": ["A database system", "TOGAF"],
            "answer": ["B", "B"],
            "justification": [
                "SE focuses on complex systems",
                "Agile uses iterations",
            ],
        })

    def test_init(self):
        """Test converter initialization."""
        converter = MCQToOSQConverter(
            api_key="test-key",
            model="gpt-4o",
            confidence_threshold=7,
        )
        assert converter.model == "gpt-4o"
        assert converter.confidence_threshold == 7

    def test_init_with_prompts(self):
        """Test converter with custom prompts."""
        converter = MCQToOSQConverter(
            api_key="test-key",
            classification_prompt="classification",
            conversion_prompt="standard",
        )
        # Actual attributes have '_name' suffix
        assert converter.classification_prompt_name == "classification"
        assert converter.conversion_prompt_name == "standard"

    def test_converter_attributes(self):
        """Test converter has expected attributes."""
        converter = MCQToOSQConverter(
            api_key="test-key",
            model="gpt-4-turbo",
            confidence_threshold=8,
            temperature=0.1,
        )
        assert converter.model == "gpt-4-turbo"
        assert converter.confidence_threshold == 8
        assert converter.temperature == 0.1

    def test_convert_single_requires_api(self, sample_mcq_df):
        """Test that conversion requires valid API key."""
        converter = MCQToOSQConverter(api_key="invalid-key")

        # This will fail without valid API key but tests the method exists
        with pytest.raises(Exception):
            converter.convert_single(sample_mcq_df.iloc[0])

    def test_batch_convert_exists(self, sample_mcq_df):
        """Test that batch_convert method exists."""
        converter = MCQToOSQConverter(api_key="invalid-key")
        assert hasattr(converter, "batch_convert")
        assert callable(converter.batch_convert)

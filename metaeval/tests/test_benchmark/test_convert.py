"""Tests for MCQ to OSQ conversion."""

import pytest
import pandas as pd

from metaeval.benchmark.convert import (
    MCQToOSQConverter,
    ConversionResult,
    conversions_to_dataframe,
)


class TestConversionResult:
    """Tests for ConversionResult dataclass."""

    def test_creation(self):
        """Test creating a conversion result."""
        result = ConversionResult(
            question_id="q1",
            original_question="What is SE?",
            osq_prompt="Explain systems engineering.",
            expected_answer="Systems engineering is...",
            rubric={"full_credit": "Complete answer", "partial_credit": "Some points"},
            blooms_level="Understand",
            suitability_score=8,
            conversion_success=True,
        )
        assert result.question_id == "q1"
        assert result.conversion_success is True
        assert result.suitability_score == 8

    def test_to_dict(self):
        """Test converting result to dict."""
        result = ConversionResult(
            question_id="q1",
            original_question="Test?",
            osq_prompt="Test prompt",
            expected_answer="Test answer",
            rubric={"full": "good"},
            blooms_level="Apply",
            suitability_score=9,
            conversion_success=True,
        )
        data = result.to_dict()

        assert isinstance(data, dict)
        assert data["question_id"] == "q1"
        assert data["conversion_success"] is True


class TestConversionsToDataFrame:
    """Tests for conversions_to_dataframe function."""

    def test_empty_list(self):
        """Test converting empty list."""
        df = conversions_to_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_single_conversion(self):
        """Test converting single result."""
        result = ConversionResult(
            question_id="q1",
            original_question="Test?",
            osq_prompt="Test prompt",
            expected_answer="Test answer",
            rubric={"full": "good"},
            blooms_level="Apply",
            suitability_score=9,
            conversion_success=True,
        )
        df = conversions_to_dataframe([result])

        assert len(df) == 1
        assert df.iloc[0]["question_id"] == "q1"

    def test_multiple_conversions(self):
        """Test converting multiple results."""
        results = [
            ConversionResult(
                question_id=f"q{i}",
                original_question=f"Question {i}?",
                osq_prompt=f"Prompt {i}",
                expected_answer=f"Answer {i}",
                rubric={},
                blooms_level="Apply",
                suitability_score=i + 5,
                conversion_success=True,
            )
            for i in range(5)
        ]
        df = conversions_to_dataframe(results)

        assert len(df) == 5
        assert list(df["question_id"]) == ["q0", "q1", "q2", "q3", "q4"]


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
        assert converter.classification_prompt == "classification"
        assert converter.conversion_prompt == "standard"

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

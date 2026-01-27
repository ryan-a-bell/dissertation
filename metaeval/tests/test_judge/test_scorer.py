"""Tests for judge scoring and parsing."""

import pytest

from metaeval.judge.scorer import JudgeScorer, parse_judgment, extract_justification
from metaeval.core.types import DimensionScores


class TestJudgeScorer:
    """Tests for JudgeScorer class."""

    def test_parse_json_response(self, sample_judgment_response):
        """Test parsing JSON response."""
        scorer = JudgeScorer()
        result = scorer.parse(sample_judgment_response)

        assert result.parse_success
        assert result.scores is not None
        assert result.scores.technical_accuracy == 18
        assert result.total_score == 75
        assert "technical understanding" in result.justification.lower()

    def test_parse_regex_fallback(self):
        """Test regex parsing when JSON fails."""
        response = """
        Technical Accuracy: 15
        Conceptual Understanding: 12
        Completeness: 14
        Clarity Organization: 10
        Professional Relevance: 9
        Total: 60
        """

        scorer = JudgeScorer()
        result = scorer.parse(response)

        assert result.scores is not None
        assert result.scores.technical_accuracy == 15
        assert result.total_score == 60

    def test_invalid_response(self):
        """Test handling of invalid response."""
        response = "This is not a valid judgment."

        scorer = JudgeScorer()
        result = scorer.parse(response)

        assert not result.parse_success
        assert result.scores is None
        assert len(result.parse_errors) > 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_parse_judgment(self, sample_judgment_response):
        """Test parse_judgment function."""
        result = parse_judgment(sample_judgment_response)
        assert result.parse_success
        assert result.total_score == 75

    def test_extract_justification(self, sample_judgment_response):
        """Test extract_justification function."""
        justification = extract_justification(sample_judgment_response)
        assert "technical" in justification.lower()

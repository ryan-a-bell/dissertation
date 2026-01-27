"""Tests for position bias detection."""

import pytest
import pandas as pd
import numpy as np

from metaeval.bias.detection import PositionBiasAnalyzer, detect_bias, get_accuracy_by_position


class TestPositionBiasAnalyzer:
    """Tests for PositionBiasAnalyzer class."""

    def test_init(self, sample_mcq_data):
        """Test analyzer initialization."""
        analyzer = PositionBiasAnalyzer(sample_mcq_data)
        assert analyzer.data is not None
        assert len(analyzer.data) == len(sample_mcq_data)

    def test_get_accuracy_by_position(self, sample_mcq_data):
        """Test accuracy calculation by position."""
        analyzer = PositionBiasAnalyzer(sample_mcq_data)
        accuracy = analyzer.get_accuracy_by_position("model_0")

        assert isinstance(accuracy, dict)
        assert set(accuracy.keys()) == {"A", "B", "C", "D"}
        for pos, acc in accuracy.items():
            assert 0 <= acc <= 1

    def test_analyze(self, sample_mcq_data):
        """Test full analysis."""
        analyzer = PositionBiasAnalyzer(sample_mcq_data)
        report = analyzer.analyze("model_0")

        assert report.model == "model_0"
        assert len(report.accuracy_by_position) == 4
        assert "chi_square" in report.test_results
        assert "cramers_v" in report.effect_sizes
        assert isinstance(report.has_significant_bias, bool)

    def test_analyze_all_models(self, sample_mcq_data):
        """Test analysis of all models."""
        analyzer = PositionBiasAnalyzer(sample_mcq_data)
        reports = analyzer.analyze_all_models()

        assert len(reports) == 3
        assert all(m in reports for m in ["model_0", "model_1", "model_2"])


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_detect_bias(self, sample_mcq_data):
        """Test detect_bias function."""
        result = detect_bias(sample_mcq_data, "model_0")
        assert isinstance(result, bool)

    def test_get_accuracy_by_position_func(self, sample_mcq_data):
        """Test get_accuracy_by_position function."""
        accuracy = get_accuracy_by_position(sample_mcq_data, "model_0")
        assert isinstance(accuracy, dict)
        assert len(accuracy) == 4

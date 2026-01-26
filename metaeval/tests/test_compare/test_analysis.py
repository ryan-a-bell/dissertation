"""Tests for format comparison analysis."""

import pytest
import numpy as np

from metaeval.compare.analysis import FormatComparator, compare_formats
from metaeval.compare.stats.correlation import pearson_correlation, spearman_correlation
from metaeval.compare.stats.effects import cohens_d


class TestFormatComparator:
    """Tests for FormatComparator class."""

    def test_init(self, sample_aligned_data):
        """Test comparator initialization."""
        comparator = FormatComparator(sample_aligned_data)
        assert comparator.data is not None
        assert "osq_normalized" in comparator.data.columns

    def test_analyze(self, sample_aligned_data):
        """Test full analysis."""
        comparator = FormatComparator(sample_aligned_data)
        report = comparator.analyze("model_0")

        assert report.model == "model_0"
        assert 0 <= report.mcq_accuracy <= 1
        assert 0 <= report.osq_normalized <= 1
        assert "pearson" in report.correlations
        assert "spearman" in report.correlations
        assert "cohens_d" in report.effect_sizes

    def test_analyze_all_models(self, sample_aligned_data):
        """Test analysis of all models."""
        comparator = FormatComparator(sample_aligned_data)
        reports = comparator.analyze_all_models()

        assert len(reports) == 3


class TestCorrelation:
    """Tests for correlation functions."""

    def test_pearson_correlation(self):
        """Test Pearson correlation."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = pearson_correlation(x, y)
        assert result.method == "pearson"
        assert result.coefficient == pytest.approx(1.0, abs=0.001)
        assert result.p_value < 0.05

    def test_spearman_correlation(self):
        """Test Spearman correlation."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        result = spearman_correlation(x, y)
        assert result.method == "spearman"
        assert result.coefficient == pytest.approx(1.0, abs=0.001)


class TestEffectSizes:
    """Tests for effect size calculations."""

    def test_cohens_d(self):
        """Test Cohen's d calculation."""
        # Use data with varying differences (not constant)
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([1.5, 2.2, 2.8, 4.3, 5.5])  # Different differences

        result = cohens_d(x, y, paired=True)
        assert result.measure == "cohens_d"
        # For paired samples with varying differences, d should be non-zero
        assert result.interpretation in ["negligible", "small", "medium", "large"]

    def test_cohens_d_constant_diff(self):
        """Test Cohen's d with constant differences returns 0 (undefined)."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 3, 4, 5, 6])  # Constant difference of -1

        result = cohens_d(x, y, paired=True)
        # When SD of differences is 0, d is returned as 0
        assert result.value == 0.0

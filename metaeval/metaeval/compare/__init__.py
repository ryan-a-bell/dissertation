"""Format comparison module for MCQ vs OSQ analysis."""

from metaeval.compare.alignment import (
    align_results,
    merge_mcq_osq,
    filter_common_questions,
)
from metaeval.compare.analysis import (
    FormatComparator,
    compare_formats,
    compare_by_category,
    compare_by_blooms,
)
from metaeval.compare.visualization import (
    plot_correlation_scatter,
    plot_format_comparison,
    plot_score_distributions,
)
from metaeval.compare import stats

__all__ = [
    # Alignment
    "align_results",
    "merge_mcq_osq",
    "filter_common_questions",
    # Analysis
    "FormatComparator",
    "compare_formats",
    "compare_by_category",
    "compare_by_blooms",
    # Visualization
    "plot_correlation_scatter",
    "plot_format_comparison",
    "plot_score_distributions",
    # Stats submodule
    "stats",
]

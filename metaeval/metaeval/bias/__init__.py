"""Position bias detection and analysis module."""

from metaeval.bias.detection import (
    PositionBiasAnalyzer,
    analyze_position_bias,
    detect_bias,
    get_accuracy_by_position,
)
from metaeval.bias.visualization import (
    plot_position_heatmap,
    plot_bias_deviation,
    plot_accuracy_comparison,
)
from metaeval.bias import stats

__all__ = [
    # Detection
    "PositionBiasAnalyzer",
    "analyze_position_bias",
    "detect_bias",
    "get_accuracy_by_position",
    # Visualization
    "plot_position_heatmap",
    "plot_bias_deviation",
    "plot_accuracy_comparison",
    # Stats submodule
    "stats",
]

"""Visualization utilities for position bias analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from metaeval.core.logging import get_logger
from metaeval.bias.detection import PositionBiasReport

logger = get_logger(__name__)


def plot_position_heatmap(
    data: pd.DataFrame | dict[str, dict[str, float]],
    title: str = "Accuracy by Position",
    figsize: tuple[int, int] = (10, 8),
    cmap: str = "RdYlGn",
    annot: bool = True,
    fmt: str = ".1%",
    output_path: Path | None = None,
    **kwargs: Any,
) -> plt.Figure:
    """
    Create a heatmap showing accuracy by model and position.

    Args:
        data: DataFrame with model/position accuracy or nested dict
        title: Plot title
        figsize: Figure size
        cmap: Colormap name
        annot: Whether to annotate cells
        fmt: Format string for annotations
        output_path: Optional path to save figure
        **kwargs: Additional arguments for seaborn.heatmap

    Returns:
        Matplotlib figure
    """
    # Convert dict to DataFrame if needed
    if isinstance(data, dict):
        data = pd.DataFrame(data).T

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    sns.heatmap(
        data,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        center=data.values.mean(),
        ax=ax,
        **kwargs,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Position", fontsize=12)
    ax.set_ylabel("Model", fontsize=12)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved heatmap to {output_path}")

    return fig


def plot_bias_deviation(
    reports: dict[str, PositionBiasReport],
    baseline: str = "mean",
    figsize: tuple[int, int] = (12, 6),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot deviation from baseline accuracy for each position.

    Args:
        reports: Dictionary of PositionBiasReports by model
        baseline: Baseline for deviation ("mean" or position letter)
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    positions = ["A", "B", "C", "D"]
    x = np.arange(len(positions))
    width = 0.8 / len(reports)

    for i, (model, report) in enumerate(reports.items()):
        accuracies = [report.accuracy_by_position.get(p, 0) for p in positions]

        if baseline == "mean":
            base = np.mean(accuracies)
        else:
            base = report.accuracy_by_position.get(baseline, np.mean(accuracies))

        deviations = [acc - base for acc in accuracies]

        offset = (i - len(reports) / 2 + 0.5) * width
        bars = ax.bar(x + offset, deviations, width, label=model)

        # Color bars based on direction
        for bar, dev in zip(bars, deviations):
            bar.set_color("green" if dev >= 0 else "red")
            bar.set_alpha(0.7)

    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.set_xlabel("Position", fontsize=12)
    ax.set_ylabel("Deviation from Baseline", fontsize=12)
    ax.set_title("Position Bias Deviation from Mean Accuracy", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(positions)
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved deviation plot to {output_path}")

    return fig


def plot_accuracy_comparison(
    reports: dict[str, PositionBiasReport],
    figsize: tuple[int, int] = (12, 6),
    style: str = "grouped",
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot accuracy comparison across models and positions.

    Args:
        reports: Dictionary of PositionBiasReports by model
        figsize: Figure size
        style: Plot style ("grouped" or "line")
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    positions = ["A", "B", "C", "D"]

    if style == "line":
        for model, report in reports.items():
            accuracies = [report.accuracy_by_position.get(p, 0) for p in positions]
            ax.plot(positions, accuracies, marker="o", label=model, linewidth=2)

        ax.set_xlabel("Position", fontsize=12)
        ax.set_ylabel("Accuracy", fontsize=12)

    else:  # grouped bar
        x = np.arange(len(positions))
        width = 0.8 / len(reports)

        for i, (model, report) in enumerate(reports.items()):
            accuracies = [report.accuracy_by_position.get(p, 0) for p in positions]
            offset = (i - len(reports) / 2 + 0.5) * width
            ax.bar(x + offset, accuracies, width, label=model)

        ax.set_xticks(x)
        ax.set_xticklabels(positions)
        ax.set_xlabel("Position", fontsize=12)
        ax.set_ylabel("Accuracy", fontsize=12)

    ax.set_title("Accuracy by Position", fontsize=14, fontweight="bold")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_ylim(0, 1)

    # Add grid
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved accuracy comparison to {output_path}")

    return fig


def plot_effect_sizes(
    reports: dict[str, PositionBiasReport],
    figsize: tuple[int, int] = (10, 6),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot effect sizes across models.

    Args:
        reports: Dictionary of PositionBiasReports by model
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    models = list(reports.keys())
    effect_types = ["cramers_v", "epsilon_squared", "kendalls_w"]

    x = np.arange(len(models))
    width = 0.25

    for i, effect_type in enumerate(effect_types):
        values = []
        for model in models:
            effect = reports[model].effect_sizes.get(effect_type)
            values.append(effect.value if effect else 0)

        offset = (i - 1) * width
        ax.bar(x + offset, values, width, label=effect_type.replace("_", " ").title())

    # Add interpretation thresholds
    ax.axhline(y=0.1, color="gray", linestyle="--", alpha=0.5, label="Small threshold")
    ax.axhline(y=0.3, color="gray", linestyle="-.", alpha=0.5, label="Medium threshold")

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Effect Size", fontsize=12)
    ax.set_title("Position Bias Effect Sizes", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved effect sizes plot to {output_path}")

    return fig


def create_bias_summary_figure(
    reports: dict[str, PositionBiasReport],
    figsize: tuple[int, int] = (16, 12),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Create a comprehensive summary figure with multiple subplots.

    Args:
        reports: Dictionary of PositionBiasReports by model
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # 1. Accuracy heatmap
    accuracy_data = {
        model: report.accuracy_by_position
        for model, report in reports.items()
    }
    df = pd.DataFrame(accuracy_data).T

    sns.heatmap(
        df,
        annot=True,
        fmt=".1%",
        cmap="RdYlGn",
        ax=axes[0, 0],
    )
    axes[0, 0].set_title("Accuracy by Position", fontweight="bold")

    # 2. Line plot
    positions = ["A", "B", "C", "D"]
    for model, report in reports.items():
        accuracies = [report.accuracy_by_position.get(p, 0) for p in positions]
        axes[0, 1].plot(positions, accuracies, marker="o", label=model)
    axes[0, 1].set_title("Accuracy Trends", fontweight="bold")
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(True, linestyle="--", alpha=0.7)

    # 3. Effect sizes
    models = list(reports.keys())
    effect_values = {
        "Cramér's V": [
            reports[m].effect_sizes.get("cramers_v", type("", (), {"value": 0})()).value
            if "cramers_v" in reports[m].effect_sizes else 0
            for m in models
        ],
        "ε²": [
            reports[m].effect_sizes.get("epsilon_squared", type("", (), {"value": 0})()).value
            if "epsilon_squared" in reports[m].effect_sizes else 0
            for m in models
        ],
    }

    x = np.arange(len(models))
    width = 0.35
    axes[1, 0].bar(x - width/2, effect_values["Cramér's V"], width, label="Cramér's V")
    axes[1, 0].bar(x + width/2, effect_values["ε²"], width, label="ε²")
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[1, 0].set_title("Effect Sizes", fontweight="bold")
    axes[1, 0].legend()
    axes[1, 0].axhline(y=0.1, color="gray", linestyle="--", alpha=0.5)

    # 4. Bias detection summary
    bias_detected = [1 if reports[m].has_significant_bias else 0 for m in models]
    colors = ["red" if b else "green" for b in bias_detected]
    axes[1, 1].bar(models, [1] * len(models), color=colors, alpha=0.7)
    axes[1, 1].set_title("Bias Detected", fontweight="bold")
    axes[1, 1].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[1, 1].set_yticks([])

    # Add legend for bias detection
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="red", alpha=0.7, label="Bias Detected"),
        Patch(facecolor="green", alpha=0.7, label="No Bias"),
    ]
    axes[1, 1].legend(handles=legend_elements, loc="upper right")

    plt.suptitle("Position Bias Analysis Summary", fontsize=16, fontweight="bold")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved summary figure to {output_path}")

    return fig

"""Visualization utilities for format comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from metaeval.core.logging import get_logger
from metaeval.compare.analysis import FormatComparisonReport

logger = get_logger(__name__)


def plot_correlation_scatter(
    data: pd.DataFrame,
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
    model_col: str | None = None,
    title: str = "MCQ vs OSQ Score Correlation",
    figsize: tuple[int, int] = (10, 8),
    add_regression: bool = True,
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Create a scatter plot showing MCQ vs OSQ correlation.

    Args:
        data: DataFrame with MCQ and OSQ scores
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores
        model_col: Optional column for model (for coloring)
        title: Plot title
        figsize: Figure size
        add_regression: Whether to add regression line
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    if model_col and model_col in data.columns:
        # Color by model
        models = data[model_col].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(models)))

        for model, color in zip(models, colors):
            model_data = data[data[model_col] == model]
            ax.scatter(
                model_data[mcq_col],
                model_data[osq_col],
                c=[color],
                label=model,
                alpha=0.6,
            )
    else:
        ax.scatter(data[mcq_col], data[osq_col], alpha=0.6)

    if add_regression:
        # Add regression line
        from scipy import stats
        x = data[mcq_col].values
        y = data[osq_col].values
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean, y_clean = x[mask], y[mask]

        if len(x_clean) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)
            x_line = np.linspace(x_clean.min(), x_clean.max(), 100)
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, "r--", label=f"r={r_value:.3f}")

    ax.set_xlabel("MCQ Score", fontsize=12)
    ax.set_ylabel("OSQ Score", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")

    if model_col:
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    ax.grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved scatter plot to {output_path}")

    return fig


def plot_format_comparison(
    reports: dict[str, FormatComparisonReport],
    figsize: tuple[int, int] = (12, 6),
    style: str = "grouped",
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot MCQ vs OSQ comparison across models.

    Args:
        reports: Dictionary of FormatComparisonReports by model
        figsize: Figure size
        style: Plot style ("grouped" or "paired")
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    models = list(reports.keys())
    mcq_scores = [reports[m].mcq_accuracy for m in models]
    osq_scores = [reports[m].osq_normalized for m in models]

    x = np.arange(len(models))
    width = 0.35

    bars1 = ax.bar(x - width/2, mcq_scores, width, label="MCQ", color="steelblue")
    bars2 = ax.bar(x + width/2, osq_scores, width, label="OSQ", color="coral")

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("MCQ vs OSQ Performance", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=45, ha="right")
    ax.legend()
    ax.set_ylim(0, 1)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)

    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1%}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1%}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved comparison plot to {output_path}")

    return fig


def plot_score_distributions(
    data: pd.DataFrame,
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
    model_col: str | None = None,
    figsize: tuple[int, int] = (12, 5),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot score distributions for MCQ and OSQ.

    Args:
        data: DataFrame with scores
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores
        model_col: Optional column for model faceting
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # MCQ distribution (binary, so use bar)
    mcq_counts = data[mcq_col].value_counts().sort_index()
    axes[0].bar(["Incorrect (0)", "Correct (1)"], [mcq_counts.get(0, 0), mcq_counts.get(1, 0)])
    axes[0].set_title("MCQ Score Distribution", fontweight="bold")
    axes[0].set_ylabel("Count")

    # OSQ distribution (continuous)
    sns.histplot(data[osq_col], bins=20, kde=True, ax=axes[1])
    axes[1].set_title("OSQ Score Distribution", fontweight="bold")
    axes[1].set_xlabel("OSQ Score")

    # Add statistics
    axes[1].axvline(data[osq_col].mean(), color="red", linestyle="--", label=f"Mean: {data[osq_col].mean():.1f}")
    axes[1].axvline(data[osq_col].median(), color="green", linestyle="--", label=f"Median: {data[osq_col].median():.1f}")
    axes[1].legend()

    plt.suptitle("Score Distributions", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved distribution plot to {output_path}")

    return fig


def plot_correlation_by_category(
    data: pd.DataFrame,
    category_col: str = "incose_category",
    mcq_col: str = "mcq_score",
    osq_col: str = "osq_score",
    figsize: tuple[int, int] = (14, 8),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Plot correlation scatter plots faceted by category.

    Args:
        data: DataFrame with category information
        category_col: Column name for category
        mcq_col: Column name for MCQ scores
        osq_col: Column name for OSQ scores
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    categories = data[category_col].unique()
    n_cats = len(categories)

    # Determine grid size
    n_cols = min(4, n_cats)
    n_rows = (n_cats + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = np.array(axes).flatten()

    for idx, cat in enumerate(categories):
        cat_data = data[data[category_col] == cat]
        ax = axes[idx]

        ax.scatter(cat_data[mcq_col], cat_data[osq_col], alpha=0.5)
        ax.set_title(cat[:30], fontsize=10)
        ax.set_xlabel("MCQ")
        ax.set_ylabel("OSQ")

        # Add correlation
        from scipy import stats
        r, p = stats.spearmanr(cat_data[mcq_col], cat_data[osq_col])
        ax.text(0.05, 0.95, f"r={r:.2f}", transform=ax.transAxes, fontsize=9)

    # Hide unused axes
    for idx in range(n_cats, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle("MCQ vs OSQ Correlation by Category", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved category correlation plot to {output_path}")

    return fig


def create_comparison_summary_figure(
    reports: dict[str, FormatComparisonReport],
    figsize: tuple[int, int] = (16, 12),
    output_path: Path | None = None,
) -> plt.Figure:
    """
    Create a comprehensive summary figure.

    Args:
        reports: Dictionary of FormatComparisonReports by model
        figsize: Figure size
        output_path: Optional path to save figure

    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    models = list(reports.keys())

    # 1. Score comparison
    mcq = [reports[m].mcq_accuracy for m in models]
    osq = [reports[m].osq_normalized for m in models]
    x = np.arange(len(models))
    width = 0.35

    axes[0, 0].bar(x - width/2, mcq, width, label="MCQ")
    axes[0, 0].bar(x + width/2, osq, width, label="OSQ")
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[0, 0].set_title("MCQ vs OSQ Scores", fontweight="bold")
    axes[0, 0].legend()
    axes[0, 0].set_ylim(0, 1)

    # 2. Correlations
    pearson = [reports[m].correlations["pearson"].coefficient for m in models]
    spearman = [reports[m].correlations["spearman"].coefficient for m in models]

    axes[0, 1].bar(x - width/2, pearson, width, label="Pearson")
    axes[0, 1].bar(x + width/2, spearman, width, label="Spearman")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[0, 1].set_title("Correlations", fontweight="bold")
    axes[0, 1].legend()
    axes[0, 1].axhline(y=0, color="gray", linestyle="-", linewidth=0.5)

    # 3. Effect sizes
    cohens = [reports[m].effect_sizes["cohens_d"].value for m in models]

    colors = ["green" if d >= 0 else "red" for d in cohens]
    axes[1, 0].bar(models, cohens, color=colors, alpha=0.7)
    axes[1, 0].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[1, 0].set_title("Cohen's d Effect Sizes", fontweight="bold")
    axes[1, 0].axhline(y=0, color="gray", linestyle="-", linewidth=0.5)
    axes[1, 0].axhline(y=0.2, color="gray", linestyle="--", alpha=0.5)
    axes[1, 0].axhline(y=-0.2, color="gray", linestyle="--", alpha=0.5)

    # 4. Difference with CI
    diffs = [reports[m].mcq_accuracy - reports[m].osq_normalized for m in models]
    ci_lower = [reports[m].bootstrap_cis["mean_diff"].ci_lower for m in models]
    ci_upper = [reports[m].bootstrap_cis["mean_diff"].ci_upper for m in models]
    errors = [[d - l for d, l in zip(diffs, ci_lower)],
              [u - d for d, u in zip(diffs, ci_upper)]]

    axes[1, 1].bar(models, diffs, yerr=errors, capsize=5, alpha=0.7)
    axes[1, 1].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
    axes[1, 1].set_title("Score Difference (MCQ - OSQ) with 95% CI", fontweight="bold")
    axes[1, 1].axhline(y=0, color="gray", linestyle="-", linewidth=0.5)

    plt.suptitle("Format Comparison Summary", fontsize=16, fontweight="bold")
    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        logger.info(f"Saved summary figure to {output_path}")

    return fig

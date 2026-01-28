"""Figure export utilities for publication-ready output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


# Publication-quality settings
PUBLICATION_SETTINGS = {
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.1,
}


class FigureExporter:
    """Export publication-ready figures."""

    def __init__(
        self,
        output_dir: Path | str = "figures",
        dpi: int = 300,
        format: str = "png",
        style: str = "seaborn-v0_8-whitegrid",
    ):
        """
        Initialize figure exporter.

        Args:
            output_dir: Output directory for figures
            dpi: Resolution in dots per inch
            format: Output format (png, pdf, svg)
            style: Matplotlib style
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.format = format
        self.style = style

    def _apply_settings(self) -> None:
        """Apply publication-quality settings."""
        try:
            plt.style.use(self.style)
        except OSError:
            plt.style.use("seaborn-v0_8-whitegrid" if "seaborn" in plt.style.available else "default")

        plt.rcParams.update(PUBLICATION_SETTINGS)

    def save_figure(
        self,
        fig: plt.Figure,
        name: str,
        tight_layout: bool = True,
    ) -> Path:
        """
        Save a figure to file.

        Args:
            fig: Matplotlib figure
            name: Figure name (without extension)
            tight_layout: Whether to apply tight layout

        Returns:
            Path to saved figure
        """
        if tight_layout:
            fig.tight_layout()

        filepath = self.output_dir / f"{name}.{self.format}"
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")

        logger.info(f"Saved figure to {filepath}")
        return filepath

    def heatmap(
        self,
        data: pd.DataFrame,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        cmap: str = "RdYlGn",
        annot: bool = True,
        fmt: str = ".2f",
        figsize: tuple[float, float] = (10, 8),
        name: str = "heatmap",
        **kwargs: Any,
    ) -> Path:
        """
        Create and save a heatmap.

        Args:
            data: DataFrame to plot
            title: Figure title
            xlabel: X-axis label
            ylabel: Y-axis label
            cmap: Colormap
            annot: Whether to annotate cells
            fmt: Annotation format
            figsize: Figure size in inches
            name: Output filename
            **kwargs: Additional arguments for seaborn.heatmap

        Returns:
            Path to saved figure
        """
        import seaborn as sns

        self._apply_settings()

        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(data, annot=annot, fmt=fmt, cmap=cmap, ax=ax, **kwargs)

        if title:
            ax.set_title(title, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        return self.save_figure(fig, name)

    def bar_chart(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        hue: str | None = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        figsize: tuple[float, float] = (10, 6),
        name: str = "bar_chart",
        **kwargs: Any,
    ) -> Path:
        """
        Create and save a bar chart.

        Args:
            data: DataFrame to plot
            x: Column for x-axis
            y: Column for y-axis
            hue: Optional column for color grouping
            title: Figure title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size
            name: Output filename
            **kwargs: Additional arguments for seaborn.barplot

        Returns:
            Path to saved figure
        """
        import seaborn as sns

        self._apply_settings()

        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(data=data, x=x, y=y, hue=hue, ax=ax, **kwargs)

        if title:
            ax.set_title(title, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        plt.xticks(rotation=45, ha="right")

        return self.save_figure(fig, name)

    def scatter_plot(
        self,
        x: np.ndarray | pd.Series,
        y: np.ndarray | pd.Series,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        add_regression: bool = True,
        figsize: tuple[float, float] = (8, 8),
        name: str = "scatter",
        **kwargs: Any,
    ) -> Path:
        """
        Create and save a scatter plot.

        Args:
            x: X values
            y: Y values
            title: Figure title
            xlabel: X-axis label
            ylabel: Y-axis label
            add_regression: Whether to add regression line
            figsize: Figure size
            name: Output filename
            **kwargs: Additional arguments for scatter

        Returns:
            Path to saved figure
        """
        from scipy import stats

        self._apply_settings()

        fig, ax = plt.subplots(figsize=figsize)
        ax.scatter(x, y, alpha=0.6, **kwargs)

        if add_regression:
            mask = ~(np.isnan(x) | np.isnan(y))
            x_clean, y_clean = np.array(x)[mask], np.array(y)[mask]

            if len(x_clean) > 2:
                slope, intercept, r_value, p_value, _ = stats.linregress(x_clean, y_clean)
                x_line = np.linspace(x_clean.min(), x_clean.max(), 100)
                y_line = slope * x_line + intercept
                ax.plot(x_line, y_line, "r--", label=f"r = {r_value:.3f}")
                ax.legend()

        if title:
            ax.set_title(title, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        ax.grid(True, linestyle="--", alpha=0.7)

        return self.save_figure(fig, name)

    def qq_plot(
        self,
        data: np.ndarray,
        title: str = "Q-Q Plot",
        figsize: tuple[float, float] = (8, 8),
        name: str = "qq_plot",
    ) -> Path:
        """
        Create and save a Q-Q plot for normality assessment.

        Args:
            data: Data to plot
            title: Figure title
            figsize: Figure size
            name: Output filename

        Returns:
            Path to saved figure
        """
        from scipy import stats

        self._apply_settings()

        fig, ax = plt.subplots(figsize=figsize)

        stats.probplot(data, dist="norm", plot=ax)

        ax.set_title(title, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.7)

        return self.save_figure(fig, name)

    def violin_plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        figsize: tuple[float, float] = (10, 6),
        name: str = "violin",
        **kwargs: Any,
    ) -> Path:
        """
        Create and save a violin plot.

        Args:
            data: DataFrame to plot
            x: Column for x-axis (categories)
            y: Column for y-axis (values)
            title: Figure title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size
            name: Output filename
            **kwargs: Additional arguments

        Returns:
            Path to saved figure
        """
        import seaborn as sns

        self._apply_settings()

        fig, ax = plt.subplots(figsize=figsize)
        sns.violinplot(data=data, x=x, y=y, ax=ax, **kwargs)

        if title:
            ax.set_title(title, fontweight="bold")
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        return self.save_figure(fig, name)


def save_figure(
    fig: plt.Figure,
    path: Path | str,
    dpi: int = 300,
    tight: bool = True,
) -> None:
    """
    Convenience function to save a figure.

    Args:
        fig: Matplotlib figure
        path: Output path
        dpi: Resolution
        tight: Whether to use tight layout
    """
    if tight:
        fig.tight_layout()

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    logger.info(f"Saved figure to {path}")


def create_publication_figure(
    n_rows: int = 1,
    n_cols: int = 1,
    figsize: tuple[float, float] | None = None,
    sharex: bool = False,
    sharey: bool = False,
) -> tuple[plt.Figure, np.ndarray | plt.Axes]:
    """
    Create a figure with publication-quality settings.

    Args:
        n_rows: Number of subplot rows
        n_cols: Number of subplot columns
        figsize: Figure size (auto-calculated if None)
        sharex: Share x-axis
        sharey: Share y-axis

    Returns:
        Tuple of (figure, axes)
    """
    plt.rcParams.update(PUBLICATION_SETTINGS)

    if figsize is None:
        # Calculate appropriate size
        width = 3.5 * n_cols  # ~3.5 inches per subplot
        height = 3.0 * n_rows
        figsize = (min(width, 10), min(height, 10))

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=figsize,
        sharex=sharex,
        sharey=sharey,
    )

    return fig, axes

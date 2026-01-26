"""LaTeX table generation for publication-ready output."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd

from metaeval.core.logging import get_logger
from metaeval.core.types import TestResult, EffectSize

logger = get_logger(__name__)


class LaTeXTableGenerator:
    """Generate publication-ready LaTeX tables."""

    def __init__(
        self,
        style: Literal["booktabs", "simple"] = "booktabs",
        float_format: str = ".3f",
        escape: bool = True,
    ):
        """
        Initialize LaTeX table generator.

        Args:
            style: Table style (booktabs for professional look)
            float_format: Format string for floating point numbers
            escape: Whether to escape special LaTeX characters
        """
        self.style = style
        self.float_format = float_format
        self.escape = escape

    def from_dataframe(
        self,
        df: pd.DataFrame,
        caption: str = "",
        label: str = "",
        column_format: str | None = None,
        bold_max: bool = False,
        bold_min: bool = False,
        highlight_significant: bool = False,
        p_value_col: str | None = None,
    ) -> str:
        """
        Convert DataFrame to LaTeX table.

        Args:
            df: DataFrame to convert
            caption: Table caption
            label: Table label for references
            column_format: LaTeX column format (e.g., "lccc")
            bold_max: Bold maximum values in numeric columns
            bold_min: Bold minimum values in numeric columns
            highlight_significant: Highlight significant p-values
            p_value_col: Column containing p-values

        Returns:
            LaTeX table string
        """
        df = df.copy()

        # Process numeric formatting
        for col in df.select_dtypes(include=["float64", "float32"]).columns:
            if bold_max:
                max_val = df[col].max()
                df[col] = df[col].apply(
                    lambda x: f"\\textbf{{{x:{self.float_format}}}}"
                    if x == max_val else f"{x:{self.float_format}}"
                )
            elif bold_min:
                min_val = df[col].min()
                df[col] = df[col].apply(
                    lambda x: f"\\textbf{{{x:{self.float_format}}}}"
                    if x == min_val else f"{x:{self.float_format}}"
                )
            else:
                df[col] = df[col].apply(lambda x: f"{x:{self.float_format}}")

        # Highlight significant p-values
        if highlight_significant and p_value_col and p_value_col in df.columns:
            df[p_value_col] = df[p_value_col].apply(
                lambda x: f"\\textbf{{{x}}}" if float(x.replace("\\textbf{", "").replace("}", "")) < 0.05 else x
            )

        # Generate LaTeX
        if column_format is None:
            column_format = "l" + "c" * (len(df.columns) - 1)

        if self.style == "booktabs":
            latex = df.to_latex(
                index=False,
                escape=False,  # We've already handled escaping
                column_format=column_format,
            )
            # Add booktabs commands
            latex = latex.replace("\\toprule", "\\toprule")
            latex = latex.replace("\\midrule", "\\midrule")
            latex = latex.replace("\\bottomrule", "\\bottomrule")
        else:
            latex = df.to_latex(index=False, escape=self.escape)

        # Wrap in table environment
        if caption or label:
            header = "\\begin{table}[htbp]\n\\centering\n"
            if caption:
                header += f"\\caption{{{caption}}}\n"
            if label:
                header += f"\\label{{{label}}}\n"
            footer = "\\end{table}"
            latex = header + latex + footer

        return latex

    def statistical_tests_table(
        self,
        results: dict[str, TestResult],
        caption: str = "Statistical Test Results",
        label: str = "tab:stats",
    ) -> str:
        """
        Generate table from statistical test results.

        Args:
            results: Dictionary of test name to TestResult
            caption: Table caption
            label: Table label

        Returns:
            LaTeX table string
        """
        rows = []
        for name, result in results.items():
            rows.append({
                "Test": name.replace("_", " ").title(),
                "Statistic": result.statistic,
                "p-value": result.p_value,
                "Significant": "Yes" if result.significant else "No",
            })

        df = pd.DataFrame(rows)
        return self.from_dataframe(
            df,
            caption=caption,
            label=label,
            highlight_significant=True,
            p_value_col="p-value",
        )

    def effect_sizes_table(
        self,
        effects: dict[str, EffectSize],
        caption: str = "Effect Sizes",
        label: str = "tab:effects",
    ) -> str:
        """
        Generate table from effect size results.

        Args:
            effects: Dictionary of effect name to EffectSize
            caption: Table caption
            label: Table label

        Returns:
            LaTeX table string
        """
        rows = []
        for name, effect in effects.items():
            rows.append({
                "Measure": name.replace("_", " ").title(),
                "Value": effect.value,
                "Interpretation": effect.interpretation.title(),
            })

        df = pd.DataFrame(rows)
        return self.from_dataframe(df, caption=caption, label=label)

    def save(self, content: str, path: Path) -> None:
        """Save LaTeX content to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            f.write(content)

        logger.info(f"Saved LaTeX table to {path}")


def dataframe_to_latex(
    df: pd.DataFrame,
    caption: str = "",
    label: str = "",
    **kwargs: Any,
) -> str:
    """
    Convenience function to convert DataFrame to LaTeX.

    Args:
        df: DataFrame to convert
        caption: Table caption
        label: Table label
        **kwargs: Additional arguments for LaTeXTableGenerator

    Returns:
        LaTeX table string
    """
    generator = LaTeXTableGenerator()
    return generator.from_dataframe(df, caption=caption, label=label, **kwargs)


def results_to_latex_table(
    results: dict[str, dict[str, float]],
    caption: str = "",
    label: str = "",
    row_label: str = "Model",
) -> str:
    """
    Convert nested results dict to LaTeX table.

    Args:
        results: Nested dict {row_key: {col_key: value}}
        caption: Table caption
        label: Table label
        row_label: Label for row index

    Returns:
        LaTeX table string
    """
    df = pd.DataFrame(results).T
    df.index.name = row_label
    df = df.reset_index()

    generator = LaTeXTableGenerator()
    return generator.from_dataframe(df, caption=caption, label=label)


def format_p_value(p: float) -> str:
    """Format p-value for LaTeX."""
    if p < 0.001:
        return "$<$0.001"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def format_with_ci(
    value: float,
    ci_lower: float,
    ci_upper: float,
    fmt: str = ".2f",
) -> str:
    """Format value with confidence interval."""
    return f"{value:{fmt}} [{ci_lower:{fmt}}, {ci_upper:{fmt}}]"

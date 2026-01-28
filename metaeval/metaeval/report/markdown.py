"""Markdown report generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from metaeval.core.logging import get_logger
from metaeval.core.types import TestResult, EffectSize
from metaeval.bias.detection import PositionBiasReport
from metaeval.compare.analysis import FormatComparisonReport

logger = get_logger(__name__)


class MarkdownReportGenerator:
    """Generate markdown analysis reports."""

    def __init__(self, title: str = "Analysis Report"):
        """
        Initialize report generator.

        Args:
            title: Report title
        """
        self.title = title
        self.sections: list[tuple[str, str]] = []
        self.created = datetime.now()

    def add_section(self, title: str, content: str) -> None:
        """
        Add a section to the report.

        Args:
            title: Section title
            content: Section content (markdown)
        """
        self.sections.append((title, content))

    def add_table(
        self,
        df: pd.DataFrame,
        title: str = "",
        description: str = "",
    ) -> None:
        """
        Add a table to the report.

        Args:
            df: DataFrame to add
            title: Table title
            description: Optional description
        """
        content = ""
        if description:
            content += f"{description}\n\n"
        content += dataframe_to_markdown(df)

        self.add_section(title or "Table", content)

    def add_figure(
        self,
        path: Path | str,
        caption: str = "",
        alt_text: str = "",
    ) -> None:
        """
        Add a figure reference to the report.

        Args:
            path: Path to figure file
            caption: Figure caption
            alt_text: Alt text for accessibility
        """
        alt = alt_text or caption or "Figure"
        content = f"![{alt}]({path})"
        if caption:
            content += f"\n\n*{caption}*"

        self.add_section("Figure", content)

    def add_statistical_results(
        self,
        results: dict[str, TestResult],
        title: str = "Statistical Tests",
    ) -> None:
        """
        Add statistical test results.

        Args:
            results: Dictionary of test results
            title: Section title
        """
        rows = []
        for name, result in results.items():
            sig = "✓" if result.significant else "✗"
            rows.append({
                "Test": name.replace("_", " ").title(),
                "Statistic": f"{result.statistic:.4f}",
                "p-value": f"{result.p_value:.4f}",
                "Significant": sig,
            })

        df = pd.DataFrame(rows)
        self.add_table(df, title)

    def add_effect_sizes(
        self,
        effects: dict[str, EffectSize],
        title: str = "Effect Sizes",
    ) -> None:
        """
        Add effect size results.

        Args:
            effects: Dictionary of effect sizes
            title: Section title
        """
        rows = []
        for name, effect in effects.items():
            rows.append({
                "Measure": name.replace("_", " ").title(),
                "Value": f"{effect.value:.4f}",
                "Interpretation": effect.interpretation.title(),
            })

        df = pd.DataFrame(rows)
        self.add_table(df, title)

    def render(self) -> str:
        """
        Render the complete report.

        Returns:
            Markdown string
        """
        lines = [
            f"# {self.title}",
            "",
            f"*Generated: {self.created.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "---",
            "",
        ]

        for i, (section_title, content) in enumerate(self.sections):
            lines.append(f"## {section_title}")
            lines.append("")
            lines.append(content)
            lines.append("")

        return "\n".join(lines)

    def save(self, path: Path) -> None:
        """Save report to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.render())

        logger.info(f"Saved markdown report to {path}")


def dataframe_to_markdown(df: pd.DataFrame, index: bool = False) -> str:
    """
    Convert DataFrame to markdown table.

    Args:
        df: DataFrame to convert
        index: Whether to include index

    Returns:
        Markdown table string
    """
    return df.to_markdown(index=index)


def generate_summary_report(
    bias_reports: dict[str, PositionBiasReport] | None = None,
    comparison_reports: dict[str, FormatComparisonReport] | None = None,
    title: str = "Meta-Evaluation Analysis Report",
) -> str:
    """
    Generate a comprehensive summary report.

    Args:
        bias_reports: Position bias analysis reports
        comparison_reports: Format comparison reports
        title: Report title

    Returns:
        Markdown report string
    """
    report = MarkdownReportGenerator(title)

    # Executive Summary
    summary_lines = ["This report presents the results of meta-evaluation analysis."]

    if bias_reports:
        n_biased = sum(1 for r in bias_reports.values() if r.has_significant_bias)
        summary_lines.append(
            f"- **Position Bias**: {n_biased}/{len(bias_reports)} models show significant position bias"
        )

    if comparison_reports:
        avg_corr = sum(
            r.correlations["spearman"].coefficient
            for r in comparison_reports.values()
        ) / len(comparison_reports)
        summary_lines.append(
            f"- **Format Correlation**: Average Spearman correlation = {avg_corr:.3f}"
        )

    report.add_section("Executive Summary", "\n".join(summary_lines))

    # Position Bias Results
    if bias_reports:
        report.add_section("Position Bias Analysis", _format_bias_section(bias_reports))

    # Format Comparison Results
    if comparison_reports:
        report.add_section("Format Comparison", _format_comparison_section(comparison_reports))

    return report.render()


def _format_bias_section(reports: dict[str, PositionBiasReport]) -> str:
    """Format position bias section."""
    lines = []

    # Summary table
    rows = []
    for model, report in reports.items():
        rows.append({
            "Model": model,
            "Overall Accuracy": f"{report.overall_accuracy:.1%}",
            "Position A": f"{report.accuracy_by_position.get('A', 0):.1%}",
            "Position B": f"{report.accuracy_by_position.get('B', 0):.1%}",
            "Position C": f"{report.accuracy_by_position.get('C', 0):.1%}",
            "Position D": f"{report.accuracy_by_position.get('D', 0):.1%}",
            "Bias Detected": "Yes" if report.has_significant_bias else "No",
        })

    df = pd.DataFrame(rows)
    lines.append(dataframe_to_markdown(df))
    lines.append("")

    # Effect sizes summary
    lines.append("### Effect Sizes")
    lines.append("")

    effect_rows = []
    for model, report in reports.items():
        row = {"Model": model}
        for name, effect in report.effect_sizes.items():
            row[name] = f"{effect.value:.3f} ({effect.interpretation})"
        effect_rows.append(row)

    df = pd.DataFrame(effect_rows)
    lines.append(dataframe_to_markdown(df))

    return "\n".join(lines)


def _format_comparison_section(reports: dict[str, FormatComparisonReport]) -> str:
    """Format comparison section."""
    lines = []

    # Summary table
    rows = []
    for model, report in reports.items():
        rows.append({
            "Model": model,
            "MCQ Accuracy": f"{report.mcq_accuracy:.1%}",
            "OSQ Score": f"{report.osq_normalized:.1%}",
            "Pearson r": f"{report.correlations['pearson'].coefficient:.3f}",
            "Spearman ρ": f"{report.correlations['spearman'].coefficient:.3f}",
            "Cohen's d": f"{report.effect_sizes['cohens_d'].value:.3f}",
        })

    df = pd.DataFrame(rows)
    lines.append(dataframe_to_markdown(df))
    lines.append("")

    # Interpretation
    lines.append("### Interpretation")
    lines.append("")

    for model, report in reports.items():
        corr = report.correlations["spearman"]
        if corr.coefficient > 0.7:
            strength = "strong"
        elif corr.coefficient > 0.4:
            strength = "moderate"
        else:
            strength = "weak"

        lines.append(
            f"- **{model}**: {strength} correlation between MCQ and OSQ performance "
            f"(ρ = {corr.coefficient:.3f}, p = {corr.p_value:.4f})"
        )

    return "\n".join(lines)

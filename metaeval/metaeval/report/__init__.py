"""Automated reporting module."""

from metaeval.report.latex import (
    LaTeXTableGenerator,
    dataframe_to_latex,
    results_to_latex_table,
)
from metaeval.report.markdown import (
    MarkdownReportGenerator,
    dataframe_to_markdown,
    generate_summary_report,
)
from metaeval.report.figures import (
    FigureExporter,
    save_figure,
    create_publication_figure,
)

__all__ = [
    # LaTeX
    "LaTeXTableGenerator",
    "dataframe_to_latex",
    "results_to_latex_table",
    # Markdown
    "MarkdownReportGenerator",
    "dataframe_to_markdown",
    "generate_summary_report",
    # Figures
    "FigureExporter",
    "save_figure",
    "create_publication_figure",
]

# Dissertation Manuscript - LaTeX Source

This directory contains LaTeX source files for the dissertation "Evaluating Large Language Models on Systems Engineering Knowledge: A Comparative Analysis of Assessment Formats, Position Bias, and Cost-Effectiveness."

## Files

### Main Content
- **`chapter3_materials_methods.tex`**: Complete Chapter 3 (Materials and Methods)
  - Section 3.1: Research Framework and Overview
  - Section 3.2: Infrastructure and Technical Environment
  - Section 3.3: Dataset Preparation (Phases 1-3)
  - Section 3.4: Evaluation Procedures (Phases 4-5)
  - Section 3.5: Analysis Metrics and Methods (Phase 6)

### Supporting Materials
- **`appendices.tex`**: Appendices containing:
  - Appendix A: Conversion and judging prompts (full text)
  - Appendix B: Complete model list with specifications
  - Appendix C: Dataset visualizations
  - Appendix D: Statistical test results tables
  - Appendix E: Example conversions and judging outputs
  - Appendix F: Code and data availability
  - Appendix G: Software versions and environment specs

## Integration with Main Dissertation

To integrate these files into your main dissertation document:

```latex
% In your main.tex or dissertation.tex file:

\documentclass[12pt,letterpaper]{report}

% ... preamble with packages ...

\begin{document}

% Front matter (title, abstract, TOC, etc.)
% ...

% Chapters 1-2 (Introduction, Literature Review)
% ...

% Chapter 3: Materials and Methods
\include{manuscript/chapter3_materials_methods}

% Chapters 4-6 (Results, Discussion, Conclusion)
% ...

% Appendices
\include{manuscript/appendices}

\end{document}
```

## Required LaTeX Packages

The following packages are used in the manuscript files:

```latex
\usepackage{graphicx}        % For figures
\usepackage{booktabs}        % For professional tables
\usepackage{tabularx}        % For flexible tables
\usepackage{multirow}        % For multi-row table cells
\usepackage{amsmath}         % For mathematical equations
\usepackage{amssymb}         % For mathematical symbols
\usepackage{listings}        % For code listings
\usepackage{xcolor}          % For colored text
\usepackage{hyperref}        % For clickable references
\usepackage{enumitem}        % For customized lists
\usepackage{threeparttable} % For table notes
\usepackage{tcolorbox}       % For colored boxes (appendices)
\usepackage{float}           % For figure placement control
```

## Figure Placeholders

The manuscript includes references to figures that need to be generated from the actual data:

### Required Figures (from PlantUML diagrams in `src/ARCHITECTURE_DIAGRAMS_PLANTUML.md`)

Convert these PlantUML diagrams to PDF for inclusion:

1. **`figures/data_flow_overview.pdf`** - Lines 795-835 (overall 6-phase data flow)
2. **`figures/phase1_download.pdf`** - Lines 13-36 (Phase 1 download)
3. **`figures/phase2_conversion.pdf`** - Lines 108-173 (Phase 2 conversion pipeline)
4. **`figures/phase3_rotation.pdf`** - Lines 208-257 (Phase 3 rotation)
5. **`figures/phase4_inference.pdf`** - Lines 365-432 (Phase 4 inference workflow)
6. **`figures/phase5_judge.pdf`** - Lines 493-556 (Phase 5 judging)

To convert PlantUML to PDF:
```bash
# Extract individual diagrams from markdown
# Save each @startuml...@enduml block to separate .puml files
# Then run:
plantuml -tpdf diagram_name.puml
```

### Required Figures (from Phase 6 analysis outputs)

These will be generated when you run the Phase 6 analysis scripts:

7. **`figures/position_bias_example.pdf`** - Position bias heatmap
8. **`figures/mcq_osq_scatter.pdf`** - MCQ vs OSQ accuracy scatter plot
9. **`figures/cost_accuracy.pdf`** - Cost-accuracy scatter with efficiency frontier

### Dataset Visualizations (from Phase 1)

From `src/phase1_prep/1.2_benchmark-summary.ipynb`:

10. **`figures/subcategory_distribution.pdf`** - Horizontal bar chart
11. **`figures/category_pie.pdf`** - Pie chart
12. **`figures/category_stacked.pdf`** - Stacked bar chart

## TODOs Before Final Compilation

1. **Fill in citation keys**: Replace `\citep{sysengbench_citation}`, `\citep{lm_eval_harness}`, etc. with actual BibTeX keys
2. **Generate figures**: Convert all PlantUML diagrams and run Phase 6 analysis to generate result figures
3. **Add actual data**: Tables marked with "XXX" or "TODO" need actual values from your results
4. **Cross-reference numbering**: Ensure chapter/section references (e.g., `\ref{ch:introduction}`) match your dissertation structure
5. **Appendix placement**: Decide whether appendices go at end of Chapter 3 or end of entire dissertation

## Table Placeholders Needing Data

- **Table 3.1** (`tab:incose_distribution`): Fill in remaining INCOSE categories and counts
- **Table 3.2** (`tab:conversion_example`): Verify example is representative
- **Table 3.3** (`tab:cost_example`): Replace with actual model performance data
- **Appendix Table B.1** (`tab:complete_model_list`): Add any additional models evaluated

## Notional Content

The manuscript contains **notional explanatory content** describing what should be in each section. You should:

1. **Review for accuracy**: Ensure descriptions match your actual implementation
2. **Expand where needed**: Add institution-specific details (e.g., IRB if applicable)
3. **Adjust terminology**: Match your preferred terms (e.g., "LLM-as-a-judge" vs "automated scoring")
4. **Add context**: Include any additional methodological decisions you made

## Statistical Test Notation

The manuscript uses standard statistical notation:
- $p < 0.05$ for significance thresholds
- Cohen's $d$ for effect sizes
- $\chi^2$ for Chi-Square tests
- Greek letters ($\mu$, $\sigma$, etc.) rendered properly in LaTeX

Ensure your bibliography manager handles statistics citations (e.g., Cohen 1988 for effect size guidelines).

## License

This LaTeX source is part of the dissertation repository at https://github.com/ryan-a-bell/dissertation

## Questions or Issues

If you find placeholders that need clarification or sections that need expansion, refer to:
- `src/ARCHITECTURE_DIAGRAMS.md` - Detailed phase descriptions
- `src/ARCHITECTURE_DIAGRAMS_PLANTUML.md` - PlantUML diagram specifications
- Original Jupyter notebooks in `src/phase*` directories - Implementation details

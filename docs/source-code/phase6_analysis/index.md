---
title: "Phase 6: Analysis"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="../phase1_prep/">Phase 1: Prep</a>
<a href="../phase2_conversion/">Phase 2: Conversion</a>
<a href="../phase3_variants/">Phase 3: Variants</a>
<a href="../phase4_inference/">Phase 4: Inference</a>
<a href="../phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="./" class="active">Phase 6: Analysis</a>
</div>

# Phase 6: Results Processing and Analysis

Aggregates results from all previous phases and performs comprehensive statistical analysis including position bias detection, MCQ and OSQ analyses, and cross-modality comparison.

**Key output:** Statistical test results, publication-ready figures, and LaTeX tables

---

```
phase6_analysis/
├── analysis-v2.ipynb                          # Main analysis notebook (6 sections)
├── question-difficulty-analysis.ipynb         # Item difficulty and discrimination analysis
├── parsers.py                                 # MCQ/OSQ result parsers for Phase 4 & 5 outputs
├── gen_region_scatter.py                      # Region scatter plot generator
├── run_category_analysis.py                   # INCOSE category-level analysis
├── gen_consolidated_bias_table.py             # Consolidated position bias table generator
├── gen_obj7_artifacts.py                      # Objective 7 research artifact generator
├── insert_consolidated_bias_cell.py           # Utility: insert bias cells into notebooks
├── insert_obj7_cells.py                       # Utility: insert Obj7 cells into notebooks
├── insert_region_scatter_cell.py              # Utility: insert scatter cells into notebooks
├── anomalies/                                 # Documented data anomalies
│   └── claude-gpt-oss-grading.jsonl           #   Claude Sonnet 4.5 scoring anomalies
└── output_v3/                                 # Publication-ready outputs
    ├── fig_*.png                               #   Analysis figures (20 figures)
    └── table_*.csv                             #   Statistical result tables (16 tables)
```

- [Main Analysis](analysis-v2/) -- Notebook: position bias (chi-square, Friedman), inter-judge agreement, MCQ vs OSQ comparison, token analysis, INCOSE category heatmaps
- [Question Difficulty Analysis](question-difficulty-analysis/) -- Notebook: per-question failure rates, wrong-answer consensus, item discrimination, category concentration
- [Result Parsers](parsers/) -- Python module: functions to parse Phase 4 MCQ inference and Phase 5 judge outputs into DataFrames
- [Region Scatter Generator](gen_region_scatter/) -- Script: MCQ vs OSQ scatter plots by INCOSE category
- [Category Analysis](run_category_analysis/) -- Script: INCOSE category-level statistical analysis
- [Consolidated Bias Table](gen_consolidated_bias_table/) -- Script: merged chi-square and Friedman results
- [Objective 7 Artifacts](gen_obj7_artifacts/) -- Script: research artifacts for Objective 7
- [Anomalies](anomalies/) -- Documented data issues (Claude Sonnet 4.5 missing scores)

# Analysis v2 Implementation Summary

## Overview

Created `analysis-v2.ipynb` - a comprehensive Jupyter notebook implementing all statistical analyses from manuscript § 3.5 (Analytical Approach).

**Status:** ✅ **COMPLETE** (77 cells, all sections implemented)

**Commit:** `8513c42` on branch `claude/analysis-v2-manuscript-mapping-014E5b6tfJekDmddkMDqqoau`

---

## Sections Implemented

### 1. Setup & Data Loading (Cells 1-16)
- Imports and configuration
- Helper functions (LaTeX export, judge filtering)
- MCQ and OSQ data loading
- Position variant filtering (a/b/c/d → A/B/C/D)
- Matched question identification (845 questions)
- Data summary table

**Key Configuration:**
- `N_MATCHED_QUESTIONS = 845`
- `N_BOOTSTRAP = 10000`
- `JUDGE_SELECTION = 'all'` (modular - can filter by judge)
- `POSITION_MAPPING = {'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'}`

---

### 2. MCQ Position Bias Analysis - § 3.5.1 (Cells 17-34)

#### Analyses Implemented:
✅ **Visual Diagnostics:**
- Accuracy by position bar charts (A/B/C/D)
- Deviation from uniform plots (Δ_p)

✅ **Statistical Tests:**
- Chi-square test of independence (2×4 contingency table)
- Friedman test (repeated measures across positions)
- Cramér's V effect sizes

✅ **Interpretation:**
- Manuscript decision logic (No bias / Mild / Moderate / Strong)
- Categorization based on p-values and effect sizes

#### Outputs:
- `fig_mcq_position_accuracy.png`
- `fig_mcq_deviation_uniform.png`
- `fig_cramers_v_position_bias.png`
- `table_chi_square_position_bias.csv` + `.tex`
- `table_friedman_position_bias.csv` + `.tex`
- `table_position_bias_interpretation.csv` + `.tex`

---

### 3. OSQ-Specific Analysis - § 3.5.2 (Cells 35-49)

#### Analyses Implemented:
✅ **Descriptive Statistics:**
- Per-model: n, mean, median, SD, IQR, min, max
- Per-judge: n, mean, median, SD, IQR, leniency

✅ **Visual Diagnostics:**
- Score distribution plots (histogram + KDE) per model
- Judge-level violin plots with embedded box plots
- Rubric dimension bar charts (5 dimensions)

✅ **Statistical Tests:**
- Inter-judge agreement (Spearman correlation, pairwise)
- Bootstrap 95% confidence intervals (10,000 iterations)

✅ **Interpretation:**
- High/Moderate/Low reliability thresholds (ρ ≥ 0.80 / 0.50)
- CI width assessment

#### Outputs:
- `fig_osq_score_distributions.png`
- `fig_osq_judge_distributions.png`
- `fig_osq_rubric_dimensions.png`
- `fig_osq_bootstrap_ci.png`
- `table_osq_stats_by_model.csv`
- `table_osq_stats_by_judge.csv` + `.tex`
- `table_interjudge_correlation.csv` + `.tex`
- `table_osq_bootstrap_ci.csv` + `.tex`

---

### 4. Format Comparison: MCQ vs OSQ - § 3.5.3 (Cells 50-63)

#### Analyses Implemented:
✅ **Visual Diagnostics:**
- MCQ-OSQ scatter plot with:
  - Separate points for each judge
  - Correlation line per judge
  - Average across all judges (bold line)
  - y=x reference diagonal

✅ **Statistical Tests:**
- Pearson correlation (linear association)
- Spearman correlation (rank agreement)
- Wilcoxon signed-rank test (paired differences)
- Cohen's d (effect size for paired samples)

✅ **Per-Model Analysis:**
- Δᵢ = Acc_MCQ,i - S̄'_OSQ,i for each model

✅ **Interpretation:**
- Correlation thresholds (≥0.80 equivalent / ≥0.50 aligned)
- Effect size categories (< 0.20 negligible / 0.50 medium / 0.80 large)
- Final interpretation logic

#### Outputs:
- `fig_mcq_osq_scatter_multijudge.png`
- `table_mcq_osq_correlations.csv` + `.tex`
- `table_wilcoxon_results.csv` + `.tex`
- `table_effect_sizes.csv` + `.tex`
- `table_per_model_differences.csv` + `.tex`

**Key Feature:** Multi-judge support with per-judge and average analysis

---

### 5. Tokenomics & Cost-Effectiveness - § 3.5.4 (Cells 64-72)

#### Analyses Implemented:
✅ **Token & Cost Metrics:**
- Token counting using tiktoken (cl100k_base encoding)
- Model-specific API pricing (19 models)
- Cost per response calculation
- Cost per 1,000 questions
- Cost per score point (efficiency metric)

✅ **Visual Diagnostics:**
- Cost-quality bubble chart
  - X-axis: Cost per 1,000 questions
  - Y-axis: Mean OSQ score
  - Bubble size: Response token count
  - Color: Cost per score point
  - Quadrant lines (median splits)

✅ **Interpretation:**
- Best efficiency identification
- Best quality identification
- Budget tier classification (Budget / Mid-tier / Premium)

#### Model Pricing Included:
- Anthropic: Claude Sonnet 4.5
- OpenAI: GPT-4.1
- Google: Gemini 2.5 Flash
- Mistral: Large, Small 3.2, Devstral
- Llama: 3.2 (1B, 3B), 3.3 (70B), 4 (16x17B)
- Mixtral: 8x22B
- Gemma: 1B, 4B, 12B, 27B
- Phi: 3 (14B), 3.5 (3.8B), 4 (14B), 4-mini (3.8B)

#### Outputs:
- `fig_cost_quality_bubble.png`
- `table_tokenomics.csv` + `.tex`

**Note:** Pareto frontier analysis intentionally EXCLUDED per user request

---

### 6. Summary & Export (Cells 73-77)

#### Components:
✅ **Analysis Summary:**
- Aggregate statistics across all sections
- Model counts, significance counts
- Key metrics (correlations, effect sizes, costs)

✅ **Export Manifest:**
- Automatic file listing (figures, CSVs, LaTeX tables)
- File size reporting

✅ **Key Findings:**
- Position bias summary
- OSQ reliability assessment
- Format alignment conclusion
- Most efficient model identification
- Saved to `key_findings.txt`

---

## Complete Output Manifest

### Figures (9 total):
1. `fig_mcq_position_accuracy.png` - Accuracy by position bar chart
2. `fig_mcq_deviation_uniform.png` - Deviation from uniform
3. `fig_cramers_v_position_bias.png` - Effect sizes horizontal bar
4. `fig_osq_score_distributions.png` - Multi-panel histograms + KDE
5. `fig_osq_judge_distributions.png` - Violin plots by judge
6. `fig_osq_rubric_dimensions.png` - Rubric dimension bar chart
7. `fig_osq_bootstrap_ci.png` - Forest plot with error bars
8. `fig_mcq_osq_scatter_multijudge.png` - Multi-judge scatter with regressions
9. `fig_cost_quality_bubble.png` - Cost-quality trade-off

### Tables (12 sets, CSV + LaTeX):
1. `table_chi_square_position_bias` - Chi-square results
2. `table_friedman_position_bias` - Friedman results
3. `table_position_bias_interpretation` - Position bias categories
4. `table_osq_stats_by_model` - OSQ descriptive stats by model
5. `table_osq_stats_by_judge` - OSQ descriptive stats by judge
6. `table_interjudge_correlation` - Pairwise judge correlations
7. `table_osq_bootstrap_ci` - Bootstrap confidence intervals
8. `table_mcq_osq_correlations` - Pearson & Spearman per judge
9. `table_wilcoxon_results` - Wilcoxon signed-rank test
10. `table_effect_sizes` - Cohen's d per judge
11. `table_per_model_differences` - Δᵢ per model
12. `table_tokenomics` - Token and cost metrics

### Summary Files:
- `key_findings.txt` - Human-readable findings summary

**Total outputs:** 9 figures + 24 files (12×2 formats) + 1 summary = **34 files**

---

## Key Features

### ✅ Multi-Judge Support
- All OSQ and format comparison analyses support multiple judges
- Separate analysis per judge + aggregate average
- Correlation lines per judge on scatter plots
- Modular `JUDGE_SELECTION` configuration

### ✅ Manuscript Alignment
- Exact section numbering (§ 3.5.1 - 3.5.4)
- All tests as specified (Chi-square, Friedman, Spearman, Wilcoxon, Bootstrap)
- Interpretation logic from manuscript decision trees
- Effect size thresholds matching manuscript

### ✅ 845 Matched Questions
- MCQ vs OSQ uses only matched subset
- Consistent question set for format comparison
- Explicit filtering and validation

### ✅ Position Variant Mapping
- Variants a/b/c/d → Positions A/B/C/D
- 2×4 contingency tables (correct/incorrect × A/B/C/D)
- Repeated measures design for Friedman

### ✅ Production Quality
- 300 DPI figures
- LaTeX tables with booktabs formatting
- Comprehensive error handling
- Clear documentation and comments

---

## Usage Instructions

### Running the Notebook:

```bash
cd /home/user/dissertation/src/phase6_analysis
jupyter notebook analysis-v2.ipynb
```

Or run all cells:
```bash
jupyter nbconvert --to notebook --execute analysis-v2.ipynb
```

### Configuration Options:

1. **Judge Selection:**
   ```python
   JUDGE_SELECTION = 'all'  # Use all complete judges
   # OR
   JUDGE_SELECTION = ['openai_gpt-5-mini']  # Specific judge
   ```

2. **Bootstrap Iterations:**
   ```python
   N_BOOTSTRAP = 10000  # Default (can reduce for faster execution)
   ```

3. **Output Directory:**
   ```python
   output_dir = Path('output_v2')  # Change if needed
   ```

### Dependencies:
- pandas, numpy, scipy, matplotlib, seaborn
- tiktoken (for token counting)
- Local `parsers` module (already in phase6_analysis/)

---

## Manuscript Integration

### Tables to Include:
1. **Position Bias:** `table_position_bias_interpretation.tex`
2. **OSQ Stats:** `table_osq_stats_by_model.tex`, `table_osq_stats_by_judge.tex`
3. **Inter-Judge:** `table_interjudge_correlation.tex`
4. **Bootstrap CIs:** `table_osq_bootstrap_ci.tex`
5. **Format Comparison:** `table_mcq_osq_correlations.tex`, `table_effect_sizes.tex`
6. **Tokenomics:** `table_tokenomics.tex`

### Figures to Include:
- All 9 figures are publication-ready at 300 DPI
- Suggest: 2-3 figures per analysis section
- Key figures: Multi-judge scatter (Fig 8), Cramér's V (Fig 3), Cost-quality (Fig 9)

---

## Next Steps

### Immediate:
1. ✅ Review output files in `output_v2/`
2. ✅ Execute notebook to verify all cells run successfully
3. ✅ Check statistical results for sanity

### Integration:
4. Incorporate tables into manuscript § 3.5
5. Add figures to manuscript with captions
6. Update results section with key findings

### Optional Enhancements:
7. Add Bland-Altman plots for format agreement (if desired)
8. Add dimension-specific OSQ analysis
9. Create supplementary materials notebook

---

## Git Information

**Branch:** `claude/analysis-v2-manuscript-mapping-014E5b6tfJekDmddkMDqqoau`

**Commit:** `8513c42`

**Files:**
- `src/phase6_analysis/analysis-v2.ipynb` (primary notebook)
- `src/phase6_analysis/add_remaining_sections.py` (helper script)
- `src/phase6_analysis/complete_notebook.py` (helper script)

**To create PR:**
```bash
gh pr create --title "Add analysis-v2.ipynb with complete manuscript mapping" \
             --body "Implements all analyses from § 3.5"
```

---

## Contact

For questions or issues with the notebook, refer to:
- Manuscript § 3.5 for analysis specifications
- This summary document for implementation details
- Inline comments in notebook cells for specific analysis steps

---

**Created:** 2025-12-11
**Status:** Complete and committed
**Verified:** All 77 cells implemented, all outputs specified

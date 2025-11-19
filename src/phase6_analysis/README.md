# TODO: Update


# Phase 6: Results Processing & Analysis

This directory contains comprehensive statistical analysis tools for Phase 6 of the dissertation pipeline.

## Overview

Phase 6 aggregates results from all previous phases and performs:

1. **Position Bias Analysis** - Detect and quantify position bias in MCQ responses
2. **MCQ vs OSQ Comparison** - Compare performance across question formats
3. **Tokenomics & Cost Analysis** - Analyze token efficiency and cost-effectiveness
4. **Statistical Testing** - Normality tests, effect sizes, confidence intervals
5. **Visualizations** - Publication-ready plots and charts

## Main Script

### `comprehensive_analysis.py`

Comprehensive statistical analysis covering all Phase 6 requirements.

#### Quick Start

```bash
# Run complete analysis with defaults
python src/phase6_analysis/comprehensive_analysis.py

# Custom paths
python src/phase6_analysis/comprehensive_analysis.py \
    --results-dir src/phase4_inference/downloaded_output \
    --osq-judged-dir src/phase5_llm_as_a_judge/judged_outputs \
    --output-dir src/phase6_analysis/results
```

#### Arguments

- `--results-dir`: Directory containing Phase 4 MCQ and OSQ results (default: `src/phase4_inference/downloaded_output`)
- `--osq-judged-dir`: Directory containing Phase 5 judged OSQ outputs (default: `src/phase5_llm_as_a_judge/judged_outputs`)
- `--output-dir`: Output directory for analysis results (default: `src/phase6_analysis/results`)
- `--model-pricing`: Path to model pricing CSV (optional, for tokenomics analysis)

## Analysis Modules

### 1. Position Bias Analysis

Detects if models have a systematic preference for certain answer positions (A, B, C, D).

**Statistical Tests:**
- **Chi-Square Test**: Tests independence between position and correctness
- **Kruskal-Wallis H Test**: Non-parametric ANOVA across positions
- **Friedman Test**: Repeated measures test (same questions, different positions)
- **Pairwise McNemar Tests**: Paired comparisons between positions
- **Cramér's V**: Effect size measurement (0-1 scale)

**Outputs:**
- `csv/position_bias_analysis.csv` - Statistical test results per model
- `figures/position_bias_heatmap.png` - Heatmap of accuracy by position
- `figures/position_bias_deviation.png` - Deviation from expected uniform distribution (25% per position)

**Interpretation:**
- **p-value < 0.05**: Statistically significant position bias
- **Cramér's V > 0.3**: Strong effect
- **Cramér's V 0.1-0.3**: Moderate effect
- **Cramér's V < 0.1**: Weak effect

### 2. MCQ vs OSQ Comparison

Compares model performance across question formats.

**Analyses:**
- Overall accuracy comparison
- Pearson correlation between formats
- Paired t-tests (MCQ vs OSQ for same models)
- Question-level consistency analysis

**Outputs:**
- `csv/mcq_vs_osq_comparison.csv` - Comparative statistics
- `figures/mcq_vs_osq_scatter.png` - Scatter plot (MCQ vs OSQ accuracy)
- `figures/mcq_vs_osq_bars.png` - Side-by-side bar comparison

**Key Metrics:**
- Correlation coefficient (r)
- Mean difference (OSQ - MCQ)
- Statistical significance (p-value)

### 3. Tokenomics & Cost Analysis

Analyzes the cost-effectiveness of different models (especially "thinking" models).

**Metrics:**
- Average tokens per sample
- Cost per sample (based on model pricing)
- Accuracy per dollar (efficiency metric)
- ROI for thinking vs. standard models
- Break-even analysis

**Example Output:**

```
TOKENOMICS SUMMARY
===========================================================
Model                Accuracy  Avg_Tokens  Cost/Sample  Acc/$
deepseek-r1:7b       0.78      3,245       $0.00097     803
qwq:32b              0.82      4,512       $0.00271     302
llama3.2:3b          0.61      187         $0.00002     30,500
mistral:7b           0.65      234         $0.00003     21,667

BREAK-EVEN ANALYSIS
===========================================================
At 10,000 samples:
- Extra cost: $24.50
- Extra correct: 1,700
- Cost per extra correct: $0.0144
```

**Outputs:**
- `csv/tokenomics_analysis.csv` - Full cost/efficiency data
- `figures/tokenomics_cost_vs_accuracy.png` - Cost-effectiveness scatter
- `figures/tokenomics_efficiency_frontier.png` - Pareto frontier
- `figures/tokenomics_roi_curves.png` - ROI by sample size

### 4. Statistical Testing

Rigorous statistical validation of results.

**Normality Tests:**
- **Shapiro-Wilk Test**: Standard normality test (best for n < 50)
- **Jarque-Bera Test**: Tests skewness and kurtosis
- **D'Agostino's K² Test**: Combines skew and kurtosis

**Effect Sizes:**
- **Cohen's d**: Standardized mean difference
- **Glass's Δ**: Variant of Cohen's d using control group SD
- **Hedges' g**: Corrected for small sample sizes

**Confidence Intervals:**
- **Bootstrap Method**: 10,000 resamples
- **95% Confidence**: Default level (configurable)

**Outputs:**
- `reports/statistical_tests.json` - Test results in JSON format
- `csv/bootstrap_confidence_intervals.csv` - Bootstrap CIs per model
- `figures/qq_plot_*.png` - Q-Q plots for normality assessment
- `figures/effect_sizes.png` - Effect size visualizations

## Output Directory Structure

```
results/
├── csv/                                    # Data tables
│   ├── position_bias_analysis.csv
│   ├── mcq_vs_osq_comparison.csv
│   ├── tokenomics_analysis.csv
│   ├── bootstrap_confidence_intervals.csv
│   └── model_detailed_*.csv
├── figures/                                # Visualizations
│   ├── position_bias_heatmap.png
│   ├── position_bias_deviation.png
│   ├── mcq_vs_osq_scatter.png
│   ├── mcq_vs_osq_bars.png
│   ├── tokenomics_cost_vs_accuracy.png
│   ├── tokenomics_efficiency_frontier.png
│   ├── qq_plot_mcq_accuracies.png
│   └── ...
└── reports/                                # Summary reports
    ├── comprehensive_analysis_summary.md   # Main summary
    ├── statistical_tests.json              # Test results
    └── ...
```

## Statistical Test Decision Table

Based on `mcq_notional_statistics_tests.md`:

| Data Type | 2 Models (Paired) | 3+ Models (Repeated Measures) |
|-----------|-------------------|-------------------------------|
| Binary Outcomes | McNemar's Test | Cochran's Q Test |
| Log Probabilities | Paired t-Test / Wilcoxon | Repeated-Measures ANOVA / Friedman |
| Confidence Scores | Paired t-Test / Wilcoxon | Repeated-Measures ANOVA / Friedman |
| Ordinal Data | Wilcoxon Signed-Rank | Friedman Test |

**Assumptions:**
- **Normality**: Check with Shapiro-Wilk or Q-Q plots
- **Sphericity** (for ANOVA): Check with Mauchly's test
- **Effect Size**: Cohen's d for t-tests, Kendall's W for Friedman
- **Multiple Comparisons**: Use Bonferroni or Holm correction

## Visualization Guidelines

All plots are:
- **High-resolution**: 300 DPI for publication
- **Accessible**: Color-blind friendly palettes where possible
- **Annotated**: Clear labels, titles, and legends
- **Consistent**: Uniform styling across all figures

## Decision Framework

Based on `analysis.md`, the results support:

### For High-Volume Applications (>100K queries)
- Thinking models often worth it due to accumulated accuracy gains

### For Cost-Sensitive Applications
- Use standard models with position rotation to minimize bias cost

### For Critical Applications
- Thinking models justified despite higher cost
- OSQ format may provide better accuracy than MCQ

### For Research/Development
- Test on subset first to calculate specific ROI
- Use break-even analysis to justify budget

## Key Insights

The analysis quantifies the "thinking model trade-off":
- **When**: Extra accuracy justifies extra cost
- **How much**: Cost per additional correct answer
- **At what scale**: Break-even points

## References

**Position Bias:**
- Cramér's V effect size interpretation (Cohen, 1988)
- McNemar test for paired nominal data (McNemar, 1947)

**Statistical Tests:**
- Shapiro-Wilk normality test (Shapiro & Wilk, 1965)
- Friedman test for repeated measures (Friedman, 1937)
- Bootstrap confidence intervals (Efron, 1979)

**Effect Sizes:**
- Cohen's d interpretation (Cohen, 1988)
- Hedges' g correction (Hedges, 1981)

## Advanced Usage

### Running Individual Analyses

```python
from comprehensive_analysis import ComprehensiveAnalyzer

# Initialize
analyzer = ComprehensiveAnalyzer(
    results_dir="path/to/results",
    output_dir="path/to/output"
)

# Load data
analyzer.load_all_data()

# Run specific analyses
position_bias_df = analyzer.analyze_position_bias()
comparison_df = analyzer.analyze_mcq_vs_osq()
statistical_tests = analyzer.perform_statistical_tests()

# Generate report
analyzer.generate_summary_report()
```

### Custom Visualizations

The `ComprehensiveAnalyzer` class provides methods for creating custom visualizations:

```python
# Create Q-Q plot
analyzer.create_qq_plot(data, "Custom Title")

# Bootstrap CIs with custom parameters
analyzer.bootstrap_confidence_intervals(
    n_iterations=20000,
    confidence=0.99
)
```

## Troubleshooting

**Missing Data:**
- Ensure Phase 4 results are in the expected directory structure
- Check that Phase 5 judging has been completed for OSQ data
- Verify file naming conventions match expected patterns

**Statistical Warnings:**
- Small sample sizes may cause normality test failures
- Use non-parametric alternatives when assumptions are violated
- Bootstrap CIs are robust to normality violations

**Performance:**
- Bootstrap with 10,000 iterations may take several minutes
- Consider reducing iterations for initial exploration
- Use `--model` flag to process specific models for testing

## Next Steps

After analysis:

1. Review summary report in `reports/comprehensive_analysis_summary.md`
2. Examine CSV files for detailed numerical results
3. Use figures for dissertation writing
4. Interpret statistical tests in context of research questions
5. Document findings in dissertation methods and results sections

For architectural overview, see `src/ARCHITECTURE_DIAGRAMS.md`.

For statistical test details, see `mcq_notional_statistics_tests.md`.

For analysis guidance, see `analysis.md`.

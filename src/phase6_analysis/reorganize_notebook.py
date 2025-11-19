#!/usr/bin/env python3
"""
Reorganize Phase 6 Analysis Notebook
This script reorganizes analysis.ipynb according to the detailed reorganization plan.
"""

import json
import copy

def create_markdown_cell(text):
    """Create a new markdown cell with the given text."""
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [text + "\n"]
    }

def create_code_cell(code):
    """Create a new code cell with the given code."""
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [code]
    }

# Read the original notebook
with open('analysis.ipynb', 'r') as f:
    nb = json.load(f)

old_cells = nb['cells']
new_cells = []

print(f"Original notebook has {len(old_cells)} cells")

# ============================================================================
# SECTION 1: Setup and Imports (Cells 0-4) - KEEP AS IS
# ============================================================================
new_cells.append(old_cells[0])  # 0: Title/Intro
new_cells.append(old_cells[1])  # 1: ## 1. Setup and Imports
new_cells.append(old_cells[2])  # 2: ### 1.1 Data Structure Reference
new_cells.append(old_cells[3])  # 3: CODE: Imports
new_cells.append(old_cells[4])  # 4: CODE: Utility functions

# ============================================================================
# SECTION 2: Data Loading (Cells 5-7) - KEEP AS IS
# ============================================================================
new_cells.append(old_cells[5])  # 5: ## 2. Data Loading
new_cells.append(old_cells[6])  # 6: CODE: Define paths
new_cells.append(old_cells[7])  # 7: CODE: Parse MCQ samples

# ============================================================================
# SECTION 3: MCQ Analysis (Cells 8-41)
# ============================================================================

# 8: Rename header from "## 3. Data Exploration" to "## 3. MCQ Analysis"
mcq_header = copy.deepcopy(old_cells[8])
mcq_header['source'] = ["## 3. MCQ Analysis\n"]
new_cells.append(mcq_header)

# 3.1 Data Exploration
new_cells.append(create_markdown_cell("### 3.1 Data Exploration"))  # 9: NEW
new_cells.append(old_cells[9])   # 10: CODE: PyGWalker install
new_cells.append(old_cells[10])  # 11: CODE: PyGWalker usage
new_cells.append(old_cells[11])  # 12: CODE: DataFrame preview

# 3.2 Overall MCQ Performance (NEW SECTION)
new_cells.append(create_markdown_cell("### 3.2 Overall MCQ Performance"))  # 13: NEW
new_cells.append(old_cells[18])  # 14: CODE: Table 3 - Model Performance Summary

# 3.3 Position Bias Analysis
# Rename from "## 4. Position Bias Analysis" to "### 3.3 Position Bias Analysis"
pos_bias_header = copy.deepcopy(old_cells[12])
pos_bias_header['source'] = ["### 3.3 Position Bias Analysis\n"]
new_cells.append(pos_bias_header)  # 15
new_cells.append(old_cells[13])  # 16: CODE: Filter fixed-position variants

# Statistical Test Justification
new_cells.append(create_markdown_cell("#### Statistical Test Justification"))  # 17: NEW
new_cells.append(old_cells[16])  # 18: MD: Justification content (from old cell 16)

# Chi-Square Test
new_cells.append(create_markdown_cell("#### Chi-Square Test"))  # 19: NEW
new_cells.append(old_cells[15])  # 20: CODE: Chi-square test

# Kruskal-Wallis H Test (NEW)
new_cells.append(create_markdown_cell("#### Kruskal-Wallis H Test"))  # 21: NEW
kruskal_code = """# Kruskal-Wallis H Test for Position Bias
# Non-parametric alternative to one-way ANOVA
# Tests whether samples originate from the same distribution

from scipy import stats

print("\\n" + "="*80)
print("KRUSKAL-WALLIS H TEST FOR POSITION BIAS")
print("="*80)
print("\\nNull Hypothesis: All position groups have the same distribution")
print("Alternative: At least one position group differs\\n")

# Group accuracy by position
position_groups = []
position_labels = []
for pos in sorted(df_fixed['position'].unique()):
    group = df_fixed[df_fixed['position'] == pos]['accuracy']
    position_groups.append(group)
    position_labels.append(pos)
    print(f"Position {pos}: n={len(group)}, median={group.median():.4f}")

# Perform Kruskal-Wallis test
h_stat, p_value = stats.kruskal(*position_groups)

print(f"\\nKruskal-Wallis H statistic: {h_stat:.4f}")
print(f"p-value: {p_value:.6f}")

if p_value < 0.001:
    print(f"Result: HIGHLY SIGNIFICANT (p < 0.001) ✓✓✓")
elif p_value < 0.01:
    print(f"Result: VERY SIGNIFICANT (p < 0.01) ✓✓")
elif p_value < 0.05:
    print(f"Result: SIGNIFICANT (p < 0.05) ✓")
else:
    print(f"Result: NOT SIGNIFICANT (p ≥ 0.05)")

# Effect size: Epsilon-squared (ε²)
# ε² = H / (n² - 1) / (n + 1) where n is total sample size
n_total = sum(len(g) for g in position_groups)
k_groups = len(position_groups)
epsilon_squared = (h_stat - k_groups + 1) / (n_total - k_groups)
print(f"\\nEffect size (ε²): {epsilon_squared:.4f}")

# Interpretation
if epsilon_squared < 0.01:
    effect_interp = "negligible"
elif epsilon_squared < 0.06:
    effect_interp = "small"
elif epsilon_squared < 0.14:
    effect_interp = "medium"
else:
    effect_interp = "large"
print(f"Effect size interpretation: {effect_interp}")

# Export results
kruskal_results = {
    'test': 'Kruskal-Wallis H Test',
    'h_statistic': float(h_stat),
    'p_value': float(p_value),
    'epsilon_squared': float(epsilon_squared),
    'effect_interpretation': effect_interp,
    'n_groups': k_groups,
    'n_total': n_total,
    'group_medians': {pos: float(df_fixed[df_fixed['position'] == pos]['accuracy'].median())
                      for pos in position_labels}
}

output_dir = Path('../output/phase6_analysis')
with open(output_dir / 'kruskal_wallis_results.json', 'w') as f:
    json.dump(kruskal_results, f, indent=2)

print(f"\\n✓ Results exported to: {output_dir / 'kruskal_wallis_results.json'}")
print("="*80)
"""
new_cells.append(create_code_cell(kruskal_code))  # 22: CODE: Kruskal-Wallis

# Friedman Test (NEW)
new_cells.append(create_markdown_cell("#### Friedman Test"))  # 23: NEW
friedman_code = """# Friedman Test for Position Bias (Repeated Measures)
# Non-parametric alternative to repeated measures ANOVA
# Treats each question as a "subject" with repeated measures across positions

from scipy import stats
import pandas as pd

print("\\n" + "="*80)
print("FRIEDMAN TEST FOR POSITION BIAS (REPEATED MEASURES)")
print("="*80)
print("\\nNull Hypothesis: Position has no effect on accuracy (repeated measures)")
print("Alternative: Position affects accuracy\\n")

# Create pivot table: questions × positions
# Each row is a question, each column is a position
pivot_data = df_fixed.pivot_table(
    values='accuracy',
    index='question_id',
    columns='position',
    aggfunc='mean'
)

print(f"Data structure for Friedman test:")
print(f"  Questions (subjects): {len(pivot_data)}")
print(f"  Positions (conditions): {len(pivot_data.columns)}")
print(f"  Complete cases: {pivot_data.dropna().shape[0]}\\n")

# Remove questions that don't have all positions tested
pivot_complete = pivot_data.dropna()

if len(pivot_complete) < 10:
    print(f"WARNING: Only {len(pivot_complete)} questions have all positions.")
    print("Friedman test may have low power. Consider this when interpreting results.\\n")

# Prepare data for Friedman test (each column is a condition)
position_arrays = [pivot_complete[col].values for col in sorted(pivot_complete.columns)]

# Perform Friedman test
if len(position_arrays) >= 3:  # Need at least 3 conditions
    friedman_stat, p_value = stats.friedmanchisquare(*position_arrays)

    print(f"Friedman χ² statistic: {friedman_stat:.4f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Degrees of freedom: {len(position_arrays) - 1}")

    if p_value < 0.001:
        print(f"Result: HIGHLY SIGNIFICANT (p < 0.001) ✓✓✓")
    elif p_value < 0.01:
        print(f"Result: VERY SIGNIFICANT (p < 0.01) ✓✓")
    elif p_value < 0.05:
        print(f"Result: SIGNIFICANT (p < 0.05) ✓")
    else:
        print(f"Result: NOT SIGNIFICANT (p ≥ 0.05)")

    # Kendall's W (effect size for Friedman test)
    # W = χ² / (n * (k - 1)) where n = subjects, k = conditions
    n_subjects = len(pivot_complete)
    k_conditions = len(position_arrays)
    kendalls_w = friedman_stat / (n_subjects * (k_conditions - 1))

    print(f"\\nKendall's W (effect size): {kendalls_w:.4f}")

    # Interpretation
    if kendalls_w < 0.1:
        w_interp = "negligible"
    elif kendalls_w < 0.3:
        w_interp = "small"
    elif kendalls_w < 0.5:
        w_interp = "medium"
    else:
        w_interp = "large"
    print(f"Effect size interpretation: {w_interp}")

    # Mean ranks for each position
    print(f"\\nMean accuracy by position (in complete cases):")
    for col in sorted(pivot_complete.columns):
        mean_acc = pivot_complete[col].mean()
        print(f"  Position {col}: {mean_acc:.4f}")

    # Export results
    friedman_results = {
        'test': 'Friedman Test',
        'chi_square': float(friedman_stat),
        'p_value': float(p_value),
        'df': k_conditions - 1,
        'kendalls_w': float(kendalls_w),
        'effect_interpretation': w_interp,
        'n_subjects': n_subjects,
        'n_conditions': k_conditions,
        'position_means': {str(col): float(pivot_complete[col].mean())
                          for col in sorted(pivot_complete.columns)}
    }

    output_dir = Path('../output/phase6_analysis')
    with open(output_dir / 'friedman_test_results.json', 'w') as f:
        json.dump(friedman_results, f, indent=2)

    print(f"\\n✓ Results exported to: {output_dir / 'friedman_test_results.json'}")
else:
    print(f"ERROR: Need at least 3 positions for Friedman test, found {len(position_arrays)}")

print("="*80)
"""
new_cells.append(create_code_cell(friedman_code))  # 24: CODE: Friedman

# Pairwise McNemar Tests
new_cells.append(create_markdown_cell("#### Pairwise McNemar Tests"))  # 25: NEW
new_cells.append(old_cells[22])  # 26: CODE: McNemar tests

# Cramér's V Effect Sizes
new_cells.append(create_markdown_cell("#### Cramér's V Effect Sizes"))  # 27: NEW
new_cells.append(old_cells[20])  # 28: CODE: Cramér's V

# Visualizations
new_cells.append(create_markdown_cell("#### Visualizations"))  # 29: NEW
new_cells.append(old_cells[33])  # 30: CODE: Heatmap
new_cells.append(old_cells[34])  # 31: CODE: Bar chart
new_cells.append(old_cells[35])  # 32: CODE: Per-position heatmap
new_cells.append(old_cells[36])  # 33: CODE: Deviation bar
new_cells.append(old_cells[37])  # 34: CODE: Heatmap alternate

# 3.4 MCQ Normality & Distributional Tests
new_cells.append(create_markdown_cell("### 3.4 MCQ Normality & Distributional Tests"))  # 35: NEW
new_cells.append(old_cells[24])  # 36: CODE: Normality tests
new_cells.append(old_cells[26])  # 37: CODE: Q-Q plot
new_cells.append(old_cells[41])  # 38: CODE: Q-Q plots comprehensive

# 3.5 MCQ Bootstrap Confidence Intervals
new_cells.append(create_markdown_cell("### 3.5 MCQ Bootstrap Confidence Intervals"))  # 39: NEW
new_cells.append(old_cells[28])  # 40: CODE: Bootstrap calculation
new_cells.append(old_cells[42])  # 41: CODE: Bootstrap visualization

# ============================================================================
# SECTION 4: OSQ Analysis (Cells 42-58)
# ============================================================================

new_cells.append(create_markdown_cell("## 4. OSQ Analysis"))  # 42: NEW

# 4.1 OSQ Data Exploration
new_cells.append(create_markdown_cell("### 4.1 OSQ Data Exploration"))  # 43: NEW
new_cells.append(old_cells[44])  # 44: CODE: Load OSQ data
new_cells.append(old_cells[45])  # 45: CODE: Filter OSQ data
new_cells.append(old_cells[46])  # 46: CODE: Judge/Prompt analysis

# 4.2 OSQ Score Distribution
new_cells.append(create_markdown_cell("### 4.2 OSQ Score Distribution"))  # 47: NEW
new_cells.append(old_cells[47])  # 48: CODE: By judge model
new_cells.append(old_cells[48])  # 49: CODE: By prompt
new_cells.append(old_cells[49])  # 50: CODE: Model performance across judges
new_cells.append(old_cells[62])  # 51: CODE: Histogram with KDE
new_cells.append(old_cells[63])  # 52: CODE: Violin plot
new_cells.append(old_cells[56])  # 53: CODE: Bloom's level
new_cells.append(old_cells[66])  # 54: CODE: By dataset/variant

# 4.3 OSQ Normality & Distributional Tests
new_cells.append(create_markdown_cell("### 4.3 OSQ Normality & Distributional Tests"))  # 55: NEW
new_cells.append(old_cells[52])  # 56: CODE: OSQ normality tests

# 4.4 OSQ Bootstrap Confidence Intervals (NEW)
new_cells.append(create_markdown_cell("### 4.4 OSQ Bootstrap Confidence Intervals"))  # 57: NEW
osq_bootstrap_code = """# Bootstrap Confidence Intervals for OSQ Scores
# Calculate 95% confidence intervals for mean OSQ scores by model

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

print("\\n" + "="*80)
print("BOOTSTRAP CONFIDENCE INTERVALS FOR OSQ SCORES")
print("="*80)

# Bootstrap parameters
n_bootstrap = 10000
ci_level = 0.95
alpha = 1 - ci_level

print(f"\\nBootstrap parameters:")
print(f"  Iterations: {n_bootstrap:,}")
print(f"  Confidence level: {ci_level*100}%")
print(f"  Alpha: {alpha}\\n")

# Perform bootstrap for each model
bootstrap_results = {}

for model in sorted(df_osq_aligned['model'].unique()):
    model_data = df_osq_aligned[df_osq_aligned['model'] == model]['osq_mean_score'].dropna()

    if len(model_data) < 10:
        print(f"Skipping {model}: insufficient data (n={len(model_data)})")
        continue

    # Bootstrap resampling
    bootstrap_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(model_data, size=len(model_data), replace=True)
        bootstrap_means.append(np.mean(sample))

    bootstrap_means = np.array(bootstrap_means)

    # Calculate confidence intervals
    ci_lower = np.percentile(bootstrap_means, alpha/2 * 100)
    ci_upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
    observed_mean = model_data.mean()

    # Standard error
    se = bootstrap_means.std()

    bootstrap_results[model] = {
        'observed_mean': float(observed_mean),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper),
        'se': float(se),
        'ci_width': float(ci_upper - ci_lower),
        'n': len(model_data),
        'bootstrap_means': bootstrap_means
    }

    print(f"{model}:")
    print(f"  Observed mean: {observed_mean:.4f}")
    print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
    print(f"  CI width: {ci_upper - ci_lower:.4f}")
    print(f"  SE: {se:.4f}")
    print(f"  n: {len(model_data)}\\n")

# Visualize bootstrap distributions
n_models = len(bootstrap_results)
fig, axes = plt.subplots(n_models, 1, figsize=(10, 3*n_models))
if n_models == 1:
    axes = [axes]

for idx, (model, results) in enumerate(sorted(bootstrap_results.items())):
    ax = axes[idx]

    # Plot bootstrap distribution
    ax.hist(results['bootstrap_means'], bins=50, alpha=0.7, edgecolor='black', density=True)

    # Add observed mean
    ax.axvline(results['observed_mean'], color='red', linestyle='--', linewidth=2,
               label=f"Observed: {results['observed_mean']:.4f}")

    # Add confidence intervals
    ax.axvline(results['ci_lower'], color='green', linestyle=':', linewidth=2,
               label=f"95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")
    ax.axvline(results['ci_upper'], color='green', linestyle=':', linewidth=2)

    ax.set_title(f"Bootstrap Distribution: {model}", fontsize=12, fontweight='bold')
    ax.set_xlabel('Mean OSQ Score')
    ax.set_ylabel('Density')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.tight_layout()
output_dir = Path('../output/phase6_analysis')
plt.savefig(output_dir / 'plot_osq_bootstrap_ci.png', dpi=300, bbox_inches='tight')
print(f"\\n✓ Visualization saved to: {output_dir / 'plot_osq_bootstrap_ci.png'}")
plt.show()

# Export results
export_results = {
    model: {k: v for k, v in results.items() if k != 'bootstrap_means'}
    for model, results in bootstrap_results.items()
}

with open(output_dir / 'osq_bootstrap_results.json', 'w') as f:
    json.dump(export_results, f, indent=2)

print(f"✓ Results exported to: {output_dir / 'osq_bootstrap_results.json'}")
print("="*80)
"""
new_cells.append(create_code_cell(osq_bootstrap_code))  # 58: CODE: OSQ bootstrap

# ============================================================================
# SECTION 5: MCQ vs OSQ Comparative Analysis (Cells 59-74)
# ============================================================================

new_cells.append(create_markdown_cell("## 5. MCQ vs OSQ Comparative Analysis"))  # 59: NEW

# 5.1 Comparative Analysis Rationale
new_cells.append(create_markdown_cell("### 5.1 Comparative Analysis Rationale"))  # 60: NEW
new_cells.append(old_cells[57])  # 61: MD: Statistical rationale content

# 5.2 Correlation Analysis
new_cells.append(create_markdown_cell("### 5.2 Correlation Analysis"))  # 62: NEW
new_cells.append(old_cells[54])  # 63: CODE: MCQ-OSQ correlation

# 5.3 Paired Statistical Tests
new_cells.append(create_markdown_cell("### 5.3 Paired Statistical Tests"))  # 64: NEW
new_cells.append(old_cells[59])  # 65: CODE: Wilcoxon test

# 5.4 Effect Size Calculations
new_cells.append(create_markdown_cell("### 5.4 Effect Size Calculations"))  # 66: NEW
new_cells.append(old_cells[61])  # 67: CODE: Effect sizes

# 5.5 Visualizations
new_cells.append(create_markdown_cell("### 5.5 Visualizations"))  # 68: NEW
new_cells.append(old_cells[50])  # 69: CODE: Side-by-side bar chart
new_cells.append(old_cells[53])  # 70: CODE: Scatter plot MCQ vs OSQ
new_cells.append(old_cells[69])  # 71: CODE: MCQ vs OSQ scatter alternate
new_cells.append(old_cells[67])  # 72: CODE: Confusion matrix multiples
new_cells.append(old_cells[68])  # 73: CODE: Wrong-answer distribution
new_cells.append(old_cells[70])  # 74: CODE: Confusion matrix all

# ============================================================================
# SECTION 6: Summary Tables & Export (Cells 75-80)
# ============================================================================

new_cells.append(create_markdown_cell("## 6. Summary Tables & Export"))  # 75: NEW
new_cells.append(old_cells[29])  # 76: CODE: Table 2 - Position accuracy
new_cells.append(old_cells[30])  # 77: CODE: Table 1 - Statistical tests
new_cells.append(old_cells[32])  # 78: CODE: ANOVA test

new_cells.append(create_markdown_cell("### Output Summary and Manifest"))  # 79: NEW
new_cells.append(old_cells[39])  # 80: CODE: Final summary

# ============================================================================
# Write the reorganized notebook
# ============================================================================

nb['cells'] = new_cells
print(f"\nReorganized notebook has {len(new_cells)} cells")
print(f"Added {len(new_cells) - len(old_cells)} new cells")

with open('analysis.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("\n✓ Notebook reorganization complete!")
print("✓ Output written to: analysis.ipynb")
print("✓ Backup available at: analysis.ipynb.backup")

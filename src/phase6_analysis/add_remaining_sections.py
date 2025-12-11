#!/usr/bin/env python3
"""
Script to add remaining sections (3-6) to analysis-v2.ipynb
"""

import json
from pathlib import Path

# Read the current notebook
notebook_path = Path('analysis-v2.ipynb')
with open(notebook_path, 'r') as f:
    nb = json.load(f)

print(f"Current notebook has {len(nb['cells'])} cells")

# Define all remaining cells for sections 3-6
remaining_cells = [
    # ========================================================================
    # SECTION 3: OSQ-SPECIFIC ANALYSIS
    # ========================================================================
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n## 3. OSQ-SPECIFIC ANALYSIS (§ 3.5.2)\n\n"
            "OSQ analysis characterizes model performance on open short-answer questions and assesses "
            "consistency of LLM-based judge scoring.\n\n"
            "### Analyses:\n"
            "1. **Visual Diagnostics:** Score distributions, judge-level plots, rubric dimensions\n"
            "2. **Descriptive Statistics:** Mean, median, SD, IQR per model and judge\n"
            "3. **Inter-judge Agreement:** Spearman correlation\n"
            "4. **Bootstrap CIs:** Uncertainty quantification\n"
            "5. **Interpretation:** Apply manuscript decision logic"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": "### 3.1 OSQ Descriptive Statistics by Model"
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (
            "print('\\n📊 OSQ Descriptive Statistics by Model\\n')\n\n"
            "osq_stats_model = osq_filtered.groupby('model')['total_score'].agg([\n"
            "    ('n', 'count'),\n"
            "    ('mean', 'mean'),\n"
            "    ('median', 'median'),\n"
            "    ('std', 'std'),\n"
            "    ('iqr', lambda x: x.quantile(0.75) - x.quantile(0.25)),\n"
            "    ('min', 'min'),\n"
            "    ('max', 'max')\n"
            "]).round(2)\n\n"
            "print('OSQ Statistics by Model (first 10):')\n"
            "print(osq_stats_model.head(10))\n\n"
            "# Export\n"
            "osq_stats_model.to_csv(output_dir / 'table_osq_stats_by_model.csv')\n"
            "print(f'\\n✅ Saved: {output_dir}/table_osq_stats_by_model.csv')"
        )
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": "### 3.2 OSQ Descriptive Statistics by Judge"
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (
            "print('\\n📊 OSQ Descriptive Statistics by Judge\\n')\n\n"
            "osq_stats_judge = osq_filtered.groupby('judge_model')['total_score'].agg([\n"
            "    ('n', 'count'),\n"
            "    ('mean', 'mean'),\n"
            "    ('median', 'median'),\n"
            "    ('std', 'std'),\n"
            "    ('iqr', lambda x: x.quantile(0.75) - x.quantile(0.25))\n"
            "]).round(2)\n\n"
            "# Add leniency (deviation from cross-judge mean)\n"
            "overall_mean = osq_filtered['total_score'].mean()\n"
            "osq_stats_judge['leniency'] = (osq_stats_judge['mean'] - overall_mean).round(2)\n\n"
            "print('OSQ Statistics by Judge:')\n"
            "print(osq_stats_judge)\n\n"
            "# Export\n"
            "osq_stats_judge.to_csv(output_dir / 'table_osq_stats_by_judge.csv')\n"
            "export_latex_table(\n"
            "    osq_stats_judge,\n"
            "    'table_osq_stats_by_judge.tex',\n"
            "    'OSQ Descriptive Statistics by Judge',\n"
            "    'tab:osq_stats_judge'\n"
            ")"
        )
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": "### 3.3 Visual Diagnostic: Score Distributions per Model"
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (
            "print('\\n📊 PLOT 4: OSQ Score Distributions per Model\\n')\n\n"
            "models = sorted(osq_filtered['model'].unique())\n"
            "n_models = len(models)\n"
            "n_cols = 4\n"
            "n_rows = int(np.ceil(n_models / n_cols))\n\n"
            "fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 3))\n"
            "axes = axes.flatten()\n\n"
            "for i, model in enumerate(models):\n"
            "    ax = axes[i]\n"
            "    model_scores = osq_filtered[osq_filtered['model'] == model]['total_score']\n"
            "    \n"
            "    # Histogram\n"
            "    ax.hist(model_scores, bins=20, alpha=0.6, edgecolor='black', density=True)\n"
            "    \n"
            "    # KDE overlay\n"
            "    if len(model_scores) > 1:\n"
            "        kde = gaussian_kde(model_scores)\n"
            "        x_range = np.linspace(0, 100, 200)\n"
            "        ax.plot(x_range, kde(x_range), 'r-', linewidth=2)\n"
            "    \n"
            "    # Stats\n"
            "    ax.axvline(model_scores.mean(), color='blue', linestyle='--', linewidth=1.5, \n"
            "               label=f'Mean={model_scores.mean():.1f}')\n"
            "    ax.axvline(model_scores.median(), color='green', linestyle='--', linewidth=1.5,\n"
            "               label=f'Median={model_scores.median():.1f}')\n"
            "    \n"
            "    ax.set_title(model, fontsize=9, fontweight='bold')\n"
            "    ax.set_xlabel('OSQ Score', fontsize=8)\n"
            "    ax.set_ylabel('Density', fontsize=8)\n"
            "    ax.legend(fontsize=7)\n"
            "    ax.set_xlim(0, 100)\n\n"
            "# Hide unused subplots\n"
            "for j in range(i+1, len(axes)):\n"
            "    axes[j].axis('off')\n\n"
            "plt.tight_layout()\n"
            "plt.savefig(output_dir / 'fig_osq_score_distributions.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()\n\n"
            "print(f'✅ Saved: {output_dir}/fig_osq_score_distributions.png')"
        )
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": "### 3.4 Visual Diagnostic: Judge-Level Distributions"
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (
            "print('\\n📊 PLOT 5: OSQ Score Distribution by Judge\\n')\n\n"
            "fig, ax = plt.subplots(figsize=(12, 8))\n\n"
            "sns.violinplot(\n"
            "    data=osq_filtered,\n"
            "    x='judge_model',\n"
            "    y='total_score',\n"
            "    ax=ax,\n"
            "    inner='box',\n"
            "    palette='Set2'\n"
            ")\n\n"
            "ax.set_xlabel('Judge Model', fontsize=12)\n"
            "ax.set_ylabel('OSQ Total Score (0-100)', fontsize=12)\n"
            "ax.set_title('OSQ Score Distribution by Judge Model', \n"
            "             fontsize=14, fontweight='bold')\n"
            "ax.grid(axis='y', alpha=0.3)\n"
            "plt.xticks(rotation=45, ha='right')\n\n"
            "plt.tight_layout()\n"
            "plt.savefig(output_dir / 'fig_osq_judge_distributions.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()\n\n"
            "print(f'✅ Saved: {output_dir}/fig_osq_judge_distributions.png')"
        )
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": "### 3.5 Visual Diagnostic: Rubric Dimensions"
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": (
            "print('\\n📊 PLOT 6: OSQ Performance by Rubric Dimension\\n')\n\n"
            "# Rubric dimensions\n"
            "rubric_dimensions = [\n"
            "    'technical_accuracy',\n"
            "    'conceptual_understanding',\n"
            "    'completeness',\n"
            "    'clarity_organization',\n"
            "    'professional_relevance'\n"
            "]\n\n"
            "# Calculate mean score per dimension per model\n"
            "rubric_means = osq_filtered.groupby('model')[rubric_dimensions].mean()\n\n"
            "fig, ax = plt.subplots(figsize=(14, 10))\n\n"
            "rubric_means.plot(\n"
            "    kind='bar',\n"
            "    ax=ax,\n"
            "    width=0.8,\n"
            "    edgecolor='black',\n"
            "    linewidth=0.5\n"
            ")\n\n"
            "ax.set_xlabel('Model', fontsize=12)\n"
            "ax.set_ylabel('Mean Score (0-20)', fontsize=12)\n"
            "ax.set_title('OSQ Performance by Rubric Dimension', \n"
            "             fontsize=14, fontweight='bold')\n"
            "ax.legend(title='Rubric Dimension', bbox_to_anchor=(1.05, 1), loc='upper left')\n"
            "ax.grid(axis='y', alpha=0.3)\n"
            "plt.xticks(rotation=45, ha='right')\n\n"
            "plt.tight_layout()\n"
            "plt.savefig(output_dir / 'fig_osq_rubric_dimensions.png', dpi=300, bbox_inches='tight')\n"
            "plt.show()\n\n"
            "print(f'✅ Saved: {output_dir}/fig_osq_rubric_dimensions.png')"
        )
    },
]

# Add cells to notebook
nb['cells'].extend(remaining_cells)

# Write back
with open(notebook_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"\n✅ Added {len(remaining_cells)} cells")
print(f"Notebook now has {len(nb['cells'])} cells total")
print("Sections added: 3.1-3.5 (OSQ Analysis partial)")

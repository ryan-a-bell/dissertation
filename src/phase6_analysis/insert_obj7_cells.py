"""
Insert new notebook cells for MCQ vs OSQ scatter plots and marginal delta tables
into analysis-v2.ipynb. Inserts after cell 128 (6.7 delta code), before cell 129
(6.8 interpretation).

Also updates the 6.8 interpretation markdown to reference the new artifacts.
"""

import json
from pathlib import Path

nb_path = Path(__file__).parent / 'analysis-v2.ipynb'

with open(nb_path, 'r') as f:
    nb = json.load(f)

cells = nb['cells']
print(f"Total cells before insertion: {len(cells)}")

# Verify cell 129 is the interpretation cell
assert '6.8' in ''.join(cells[129]['source']), \
    f"Expected cell 129 to be 6.8 interpretation, got: {''.join(cells[129]['source'][:50])}"

# Define new cells to insert after cell 128 (index 129 = before interpretation)
new_cells = []

# ---- 6.8 MCQ vs OSQ Scatter Plot by Category (Full) ----
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.8 MCQ vs OSQ Scatter Plot by INCOSE Category (Leaf-Level)\n",
        "\n",
        "Each point represents one INCOSE leaf-level category, with model-averaged MCQ accuracy on the x-axis\n",
        "and model-averaged OSQ score on the y-axis. Points below the diagonal indicate categories where\n",
        "MCQ accuracy exceeds OSQ scores."
    ]
})

new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "from scipy.stats import linregress\n",
        "\n",
        "def make_category_scatter(cat_col, title_suffix, filename, ax=None):\n",
        "    \"\"\"Create MCQ vs OSQ scatter plot where each point is one category.\"\"\"\n",
        "    # Aggregate: per-category mean across all models\n",
        "    mcq_by_cat = mcq_cat.groupby(cat_col)['is_correct'].mean()\n",
        "    osq_by_cat = osq_cat.groupby(cat_col)['osq_accuracy'].mean()\n",
        "\n",
        "    scatter_df = pd.DataFrame({\n",
        "        'mcq_accuracy': mcq_by_cat,\n",
        "        'osq_score': osq_by_cat\n",
        "    }).dropna()\n",
        "\n",
        "    x = scatter_df['mcq_accuracy'].values\n",
        "    y = scatter_df['osq_score'].values\n",
        "\n",
        "    # Regression\n",
        "    slope, intercept, r_val, p_val, _ = linregress(x, y)\n",
        "\n",
        "    # Plot\n",
        "    fig, ax = plt.subplots(figsize=(12, 9))\n",
        "    palette = sns.color_palette('tab20', len(scatter_df))\n",
        "\n",
        "    for (cat, row), color in zip(scatter_df.iterrows(), palette):\n",
        "        ax.scatter(\n",
        "            row['mcq_accuracy'], row['osq_score'],\n",
        "            s=180, color=color, edgecolors='black', linewidths=0.6, alpha=0.85, zorder=5\n",
        "        )\n",
        "        ax.annotate(\n",
        "            cat, (row['mcq_accuracy'], row['osq_score']),\n",
        "            xytext=(6, 6), textcoords='offset points', fontsize=9,\n",
        "            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='gray', alpha=0.6)\n",
        "        )\n",
        "\n",
        "    # Reference lines\n",
        "    x_line = np.linspace(0, 1, 400)\n",
        "    tolerance = 0.02\n",
        "    ax.plot(x_line, x_line, color='red', linestyle=':', linewidth=2, label='Perfect Agreement')\n",
        "    ax.fill_between(x_line, x_line - tolerance, x_line + tolerance,\n",
        "                    color='gray', alpha=0.15, label=f'+/-{tolerance:.02f} Agreement Band')\n",
        "    ax.plot(x_line, slope * x_line + intercept, linestyle='--', color='gray',\n",
        "            linewidth=2, label=f'R$^2$={r_val**2:.3f}, p={p_val:.4f}')\n",
        "\n",
        "    # Axis limits - zoom to data range with padding\n",
        "    x_min, x_max = x.min() - 0.03, x.max() + 0.03\n",
        "    y_min, y_max = y.min() - 0.03, y.max() + 0.03\n",
        "    lo = min(x_min, y_min)\n",
        "    hi = max(x_max, y_max)\n",
        "    ax.set_xlim(lo, hi)\n",
        "    ax.set_ylim(lo, hi)\n",
        "\n",
        "    # Region labels\n",
        "    x_lo, x_hi = ax.get_xlim()\n",
        "    y_lo, y_hi = ax.get_ylim()\n",
        "    x_range = x_hi - x_lo\n",
        "    y_range = y_hi - y_lo\n",
        "\n",
        "    ax.text(x_lo + 0.03 * x_range, y_hi - 0.05 * y_range,\n",
        "            'OSQ > MCQ\\n(Category performs better on OSQ)',\n",
        "            ha='left', va='top', fontsize=10,\n",
        "            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.45))\n",
        "    ax.text(x_hi - 0.03 * x_range, y_lo + 0.05 * y_range,\n",
        "            'OSQ < MCQ\\n(Category performs better on MCQ)',\n",
        "            ha='right', va='bottom', fontsize=10,\n",
        "            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.45))\n",
        "\n",
        "    ax.set_xlabel('MCQ Accuracy (model-averaged)', fontsize=12)\n",
        "    ax.set_ylabel('OSQ Mean Score (model-averaged, 0-1)', fontsize=12)\n",
        "    ax.set_title(f'MCQ Accuracy vs OSQ Score by INCOSE Category\\n{title_suffix}',\n",
        "                 fontsize=14, fontweight='bold')\n",
        "    ax.grid(True, alpha=0.3)\n",
        "    ax.legend(fontsize=10)\n",
        "\n",
        "    plt.tight_layout()\n",
        "    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')\n",
        "    plt.show()\n",
        "    plt.close(fig)\n",
        "    print(f'Saved: {filename}')\n",
        "\n",
        "make_category_scatter('category_short', '(Leaf-Level Categories)',\n",
        "                      'fig_mcq_vs_osq_scatter_by_category.png')"
    ],
    "outputs": [],
    "execution_count": None
})

# ---- 6.9 MCQ vs OSQ Scatter Plot by Top-Level Group ----
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.9 MCQ vs OSQ Scatter Plot by INCOSE Top-Level Group\n",
        "\n",
        "Same scatter analysis but aggregated at the top-level INCOSE process group."
    ]
})

new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "make_category_scatter('category_toplevel', '(Top-Level Groups)',\n",
        "                      'fig_mcq_vs_osq_scatter_by_toplevel.png')"
    ],
    "outputs": [],
    "execution_count": None
})

# ---- 6.10 Delta Table with Marginal Statistics (Leaf-Level) ----
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.10 MCQ-OSQ Delta Table with Marginal Statistics (Leaf-Level)\n",
        "\n",
        "Each cell shows the mean MCQ-OSQ delta for a given (model, category) pair.\n",
        "The last two columns show per-model mean and median delta.\n",
        "The last two rows show per-category mean and median delta across models."
    ]
})

new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "def make_delta_table_with_marginals(cat_col, filename_csv, filename_tex):\n",
        "    \"\"\"Create delta table (model x category) with mean/median marginals.\"\"\"\n",
        "    delta_data = aligned_cat.groupby(['model', cat_col])['delta'].mean().reset_index()\n",
        "    delta_pivot = delta_data.pivot(index='model', columns=cat_col, values='delta')\n",
        "\n",
        "    # Sort models and categories consistently\n",
        "    models_sorted = [m for m in model_order if m in delta_pivot.index]\n",
        "    if cat_col == 'category_short':\n",
        "        cats_sorted = [c for c in cat_order if c in delta_pivot.columns]\n",
        "    else:\n",
        "        cats_sorted = [c for c in top_order if c in delta_pivot.columns]\n",
        "    delta_pivot = delta_pivot.reindex(index=models_sorted, columns=cats_sorted)\n",
        "\n",
        "    # Add per-model marginals (rightmost columns)\n",
        "    delta_pivot['Mean Delta'] = delta_pivot.mean(axis=1)\n",
        "    delta_pivot['Median Delta'] = delta_pivot.median(axis=1)\n",
        "\n",
        "    # Add per-category marginals (bottom rows)\n",
        "    cat_cols = cats_sorted\n",
        "    mean_row = delta_pivot[cat_cols].mean(axis=0)\n",
        "    median_row = delta_pivot[cat_cols].median(axis=0)\n",
        "\n",
        "    mean_row['Mean Delta'] = delta_pivot['Mean Delta'].mean()\n",
        "    mean_row['Median Delta'] = delta_pivot['Median Delta'].mean()\n",
        "    median_row['Mean Delta'] = delta_pivot['Mean Delta'].median()\n",
        "    median_row['Median Delta'] = delta_pivot['Median Delta'].median()\n",
        "\n",
        "    mean_row.name = 'Mean (across models)'\n",
        "    median_row.name = 'Median (across models)'\n",
        "\n",
        "    delta_with_marginals = pd.concat([delta_pivot, mean_row.to_frame().T, median_row.to_frame().T])\n",
        "\n",
        "    # Save CSV\n",
        "    delta_with_marginals.to_csv(output_dir / filename_csv)\n",
        "    print(f'Saved: {filename_csv}')\n",
        "\n",
        "    # Format for LaTeX\n",
        "    formatted = delta_with_marginals.copy()\n",
        "    for col in formatted.columns:\n",
        "        formatted[col] = formatted[col].apply(\n",
        "            lambda v: f'{v:+.3f}' if pd.notna(v) else '--'\n",
        "        )\n",
        "\n",
        "    col_fmt = 'l' + 'r' * len(formatted.columns)\n",
        "    short_cols = [c[:18] + '..' if len(c) > 20 else c for c in formatted.columns]\n",
        "    formatted.columns = short_cols\n",
        "\n",
        "    latex_str = formatted.to_latex(column_format=col_fmt, escape=True, float_format='%.3f')\n",
        "    with open(output_dir / filename_tex, 'w') as f:\n",
        "        f.write(latex_str)\n",
        "    print(f'Saved: {filename_tex}')\n",
        "\n",
        "    return delta_with_marginals\n",
        "\n",
        "delta_full = make_delta_table_with_marginals(\n",
        "    'category_short',\n",
        "    'table_delta_marginals_category.csv',\n",
        "    'table_delta_marginals_category.tex'\n",
        ")\n",
        "\n",
        "# Display styled\n",
        "display(delta_full.style.format('{:+.3f}', na_rep='--')\n",
        "        .background_gradient(cmap='RdYlGn_r', axis=None)\n",
        "        .set_caption('MCQ-OSQ Delta by INCOSE Category (Leaf-Level) with Marginal Statistics'))"
    ],
    "outputs": [],
    "execution_count": None
})

# ---- 6.11 Delta Table with Marginal Statistics (Top-Level) ----
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.11 MCQ-OSQ Delta Table with Marginal Statistics (Top-Level)\n",
        "\n",
        "Same as 6.10 but aggregated at the top-level INCOSE process group."
    ]
})

new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "delta_top = make_delta_table_with_marginals(\n",
        "    'category_toplevel',\n",
        "    'table_delta_marginals_toplevel.csv',\n",
        "    'table_delta_marginals_toplevel.tex'\n",
        ")\n",
        "\n",
        "# Display styled\n",
        "display(delta_top.style.format('{:+.3f}', na_rep='--')\n",
        "        .background_gradient(cmap='RdYlGn_r', axis=None)\n",
        "        .set_caption('MCQ-OSQ Delta by INCOSE Top-Level Group with Marginal Statistics'))"
    ],
    "outputs": [],
    "execution_count": None
})

# ---- 6.12 Qualification Classification Table ----
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.12 Qualification Modality Classification\n",
        "\n",
        "Classifies each INCOSE category into a recommended evaluation modality based on\n",
        "the MCQ-OSQ delta and MCQ accuracy:\n",
        "- **MCQ-sufficient**: High MCQ accuracy and large MCQ advantage (delta >= 0.15, MCQ >= 0.85)\n",
        "- **Dual-modality recommended**: Moderate MCQ advantage (0.05 <= delta < 0.15)\n",
        "- **OSQ-preferred**: Small or negative MCQ advantage (delta < 0.05)\n",
        "- **Insufficient coverage**: Fewer than 30 aligned samples"
    ]
})

new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "# Compute per-category stats\n",
        "cat_stats = aligned_cat.groupby('category_short').agg(\n",
        "    mean_delta=('delta', 'mean'),\n",
        "    median_delta=('delta', 'median'),\n",
        "    mean_mcq=('mcq_score', 'mean'),\n",
        "    mean_osq=('osq_score', 'mean'),\n",
        "    n_samples=('delta', 'count')\n",
        ").reset_index()\n",
        "\n",
        "def classify_modality(row):\n",
        "    if row['n_samples'] < 30:\n",
        "        return 'Insufficient coverage'\n",
        "    if row['mean_delta'] >= 0.15 and row['mean_mcq'] >= 0.85:\n",
        "        return 'MCQ-sufficient'\n",
        "    if row['mean_delta'] >= 0.05:\n",
        "        return 'Dual-modality recommended'\n",
        "    return 'OSQ-preferred'\n",
        "\n",
        "cat_stats['classification'] = cat_stats.apply(classify_modality, axis=1)\n",
        "cat_stats = cat_stats.sort_values('mean_delta', ascending=False)\n",
        "\n",
        "class_table = cat_stats[['category_short', 'mean_mcq', 'mean_osq',\n",
        "                          'mean_delta', 'median_delta', 'n_samples', 'classification']].copy()\n",
        "class_table.columns = ['Category', 'Mean MCQ Acc.', 'Mean OSQ Score',\n",
        "                        'Mean Delta', 'Median Delta', 'N', 'Classification']\n",
        "\n",
        "# Save\n",
        "class_table.to_csv(output_dir / 'table_qualification_classification.csv', index=False)\n",
        "latex_str = class_table.to_latex(index=False, column_format='lrrrrrl', escape=True, float_format='%.3f')\n",
        "with open(output_dir / 'table_qualification_classification.tex', 'w') as f:\n",
        "    f.write(latex_str)\n",
        "\n",
        "print('Classification results:')\n",
        "for _, row in class_table.iterrows():\n",
        "    print(f'  {row[\"Category\"]:55s} -> {row[\"Classification\"]}  '\n",
        "          f'(delta={row[\"Mean Delta\"]:+.3f}, MCQ={row[\"Mean MCQ Acc.\"]:.3f}, n={row[\"N\"]})')\n",
        "\n",
        "# Display styled\n",
        "def color_classification(val):\n",
        "    colors = {\n",
        "        'MCQ-sufficient': 'background-color: #d4edda',\n",
        "        'Dual-modality recommended': 'background-color: #fff3cd',\n",
        "        'OSQ-preferred': 'background-color: #f8d7da',\n",
        "        'Insufficient coverage': 'background-color: #e2e3e5'\n",
        "    }\n",
        "    return colors.get(val, '')\n",
        "\n",
        "display(class_table.style\n",
        "        .format({'Mean MCQ Acc.': '{:.3f}', 'Mean OSQ Score': '{:.3f}',\n",
        "                 'Mean Delta': '{:+.3f}', 'Median Delta': '{:+.3f}', 'N': '{:.0f}'})\n",
        "        .map(color_classification, subset=['Classification'])\n",
        "        .set_caption('Qualification Modality Classification by INCOSE Category'))"
    ],
    "outputs": [],
    "execution_count": None
})

# Now renumber the old 6.8 interpretation to 6.13
old_interp = cells[129]
old_source = ''.join(old_interp['source'])
old_interp['source'] = [old_source.replace('### 6.8', '### 6.13')]

# Insert new cells before the (now renumbered) interpretation cell
for i, cell in enumerate(new_cells):
    cells.insert(129 + i, cell)

print(f"Inserted {len(new_cells)} new cells at position 129")
print(f"Total cells after insertion: {len(cells)}")

# Save
nb['cells'] = cells
with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Done! Updated analysis-v2.ipynb")

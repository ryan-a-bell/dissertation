"""
Insert a consolidated MCQ Position Bias Robustness Statistics table
into analysis-v2.ipynb. This merges the chi-square, Friedman, and
classification results into a single table matching the user's LaTeX template.

Inserts after the position bias interpretation export cell, before Section 3.
"""

import json
from pathlib import Path

nb_path = Path(__file__).parent / 'analysis-v2.ipynb'

with open(nb_path, 'r') as f:
    nb = json.load(f)

cells = nb['cells']
print(f"Total cells before insertion: {len(cells)}")

# Find the cell that exports table_position_bias_interpretation
target_idx = None
for i, cell in enumerate(cells):
    src = ''.join(cell.get('source', []))
    if 'table_position_bias_interpretation.csv' in src and cell['cell_type'] == 'code':
        target_idx = i
        break

assert target_idx is not None, "Could not find interpretation export cell"
print(f"Found interpretation export cell at index {target_idx}")

# Verify next section is "## 3. OSQ"
for j in range(target_idx + 1, min(target_idx + 5, len(cells))):
    src = ''.join(cells[j].get('source', []))
    if '## 3.' in src:
        print(f"Section 3 starts at index {j}")
        break

# Insert after the export cell
insert_at = target_idx + 1

new_cells = []

# Markdown header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 2.8 Consolidated MCQ Position Bias Robustness Table\n",
        "\n",
        "Merge all per-model position bias statistics into a single table:\n",
        "chi-square statistic and p-value, Cramer's V, Friedman statistic and p-value,\n",
        "Kendall's W, and the overall classification."
    ]
})

# Code cell
new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "# ── Consolidated MCQ Position Bias Robustness Table ──────────────────\n",
        "# Load the three source tables (already computed earlier in this section)\n",
        "chi_sq = pd.read_csv(output_dir / 'table_chi_square_position_bias.csv')\n",
        "fried  = pd.read_csv(output_dir / 'table_friedman_position_bias.csv')\n",
        "interp = pd.read_csv(output_dir / 'table_position_bias_interpretation.csv')\n",
        "\n",
        "# Merge into one DataFrame\n",
        "consolidated = chi_sq[['model', 'chi2_stat', 'p_value', 'cramers_v']].merge(\n",
        "    fried[['model', 'friedman_stat', 'p_value', 'kendalls_w']],\n",
        "    on='model', suffixes=('_chi2', '_friedman')\n",
        ").merge(\n",
        "    interp[['model', 'category']],\n",
        "    on='model'\n",
        ")\n",
        "\n",
        "consolidated.columns = [\n",
        "    'Model', 'Chi-Square', 'p (Chi-Square)', \"Cramer's V\",\n",
        "    'Friedman', 'p (Friedman)', \"Kendall's W\", 'Classification'\n",
        "]\n",
        "\n",
        "# Sort by Cramer's V descending (strongest bias first)\n",
        "consolidated = consolidated.sort_values(\"Cramer's V\", ascending=False).reset_index(drop=True)\n",
        "\n",
        "# ── Save CSV ─────────────────────────────────────────────────────────\n",
        "consolidated.to_csv(output_dir / 'table_position_bias_consolidated.csv', index=False)\n",
        "print(f'Saved: table_position_bias_consolidated.csv')\n",
        "\n",
        "# ── Save LaTeX ───────────────────────────────────────────────────────\n",
        "fmt = consolidated.copy()\n",
        "fmt['Chi-Square']      = fmt['Chi-Square'].map(lambda v: f'{v:.2f}')\n",
        "fmt['p (Chi-Square)']  = fmt['p (Chi-Square)'].map(\n",
        "    lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}')\n",
        "fmt[\"Cramer's V\"]      = fmt[\"Cramer's V\"].map(lambda v: f'{v:.4f}')\n",
        "fmt['Friedman']        = fmt['Friedman'].map(lambda v: f'{v:.2f}')\n",
        "fmt['p (Friedman)']    = fmt['p (Friedman)'].map(\n",
        "    lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}')\n",
        "fmt[\"Kendall's W\"]     = fmt[\"Kendall's W\"].map(lambda v: f'{v:.4f}')\n",
        "\n",
        "# Escape underscores in model names for LaTeX\n",
        "fmt['Model'] = fmt['Model'].str.replace('_', r'\\_', regex=False)\n",
        "\n",
        "latex_lines = []\n",
        "latex_lines.append(r'\\begin{tabular}{l r r r r r r l}')\n",
        "latex_lines.append(r'\\toprule')\n",
        "latex_lines.append(\n",
        "    r\"\\textbf{Model} & \\textbf{$\\chi^2$} & \\textbf{$p_{\\chi^2}$} & \"\n",
        "    r\"\\textbf{Cram\\'er's $V$} & \\textbf{Friedman} & \"\n",
        "    r\"\\textbf{$p_{\\text{Friedman}}$} & \\textbf{Kendall's $W$} & \"\n",
        "    r\"\\textbf{Classification} \\\\\")\n",
        "latex_lines.append(r'\\midrule')\n",
        "\n",
        "for _, row in fmt.iterrows():\n",
        "    line = ' & '.join(str(row[c]) for c in fmt.columns) + r' \\\\'\n",
        "    latex_lines.append(line)\n",
        "\n",
        "latex_lines.append(r'\\bottomrule')\n",
        "latex_lines.append(r'\\end{tabular}')\n",
        "\n",
        "tex_str = '\\n'.join(latex_lines)\n",
        "with open(output_dir / 'table_position_bias_consolidated.tex', 'w') as f:\n",
        "    f.write(tex_str)\n",
        "print(f'Saved: table_position_bias_consolidated.tex')\n",
        "\n",
        "# ── Display ──────────────────────────────────────────────────────────\n",
        "def color_classification(val):\n",
        "    colors = {\n",
        "        'No bias': 'background-color: #d4edda',\n",
        "        'Mixed evidence': 'background-color: #fff3cd',\n",
        "        'Moderate bias': 'background-color: #f8d7da',\n",
        "        'Strong bias': 'background-color: #f5c6cb',\n",
        "    }\n",
        "    return colors.get(val, '')\n",
        "\n",
        "display(consolidated.style\n",
        "    .format({\n",
        "        'Chi-Square': '{:.2f}',\n",
        "        'p (Chi-Square)': lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}',\n",
        "        \"Cramer's V\": '{:.4f}',\n",
        "        'Friedman': '{:.2f}',\n",
        "        'p (Friedman)': lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}',\n",
        "        \"Kendall's W\": '{:.4f}',\n",
        "    })\n",
        "    .map(color_classification, subset=['Classification'])\n",
        "    .set_caption('MCQ Answer-Position Robustness Statistical Results by Model')\n",
        ")"
    ],
    "outputs": [],
    "execution_count": None
})

for i, cell in enumerate(new_cells):
    cells.insert(insert_at + i, cell)

print(f"Inserted {len(new_cells)} cells at position {insert_at}")
print(f"Total cells after insertion: {len(cells)}")

nb['cells'] = cells
with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Done!")

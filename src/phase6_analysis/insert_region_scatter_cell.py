"""
Insert notebook cell for the region-annotated scatter plot after the
existing scatter plots (Section 6.9) in analysis-v2.ipynb.
"""

import json
from pathlib import Path

nb_path = Path(__file__).parent / 'analysis-v2.ipynb'

with open(nb_path, 'r') as f:
    nb = json.load(f)

cells = nb['cells']
print(f"Total cells before insertion: {len(cells)}")

# Find cell 6.9 (MCQ vs OSQ Scatter Plot by INCOSE Top-Level Group)
target_idx = None
for i, cell in enumerate(cells):
    src = ''.join(cell.get('source', []))
    if '### 6.9 MCQ vs OSQ Scatter Plot by INCOSE Top-Level Group' in src:
        target_idx = i
        break

assert target_idx is not None, "Could not find cell 6.9"
print(f"Found cell 6.9 at index {target_idx}")

# The code cell for 6.9 is the next cell
code_cell_idx = target_idx + 1
print(f"Code cell for 6.9 at index {code_cell_idx}")

# Insert new cells after cell 6.9 code (at code_cell_idx + 1)
insert_at = code_cell_idx + 1

new_cells = []

# Markdown header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6.9a MCQ vs OSQ Scatter with Classification Regions\n",
        "\n",
        "Overlay the predefined classification regions on the category scatter plot:\n",
        "- **Green**: MCQ-sufficient (|delta| < 5%, MCQ Acc >= 85%)\n",
        "- **Amber**: Dual-modality recommended (5% <= |delta| < 15%)\n",
        "- **Red**: Dual-modality required (|delta| >= 15%)"
    ]
})

# Code cell
new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "import matplotlib.patheffects as pe\n",
        "from matplotlib.patches import Polygon as MplPolygon, Patch as MplPatch\n",
        "\n",
        "def make_region_scatter(cat_col, title_suffix, filename):\n",
        "    \"\"\"Scatter plot with classification region overlay.\"\"\"\n",
        "    mcq_by_cat = mcq_cat.groupby(cat_col)['is_correct'].mean()\n",
        "    osq_by_cat = osq_cat.groupby(cat_col)['osq_accuracy'].mean()\n",
        "    sdf = pd.DataFrame({'mcq_accuracy': mcq_by_cat, 'osq_score': osq_by_cat}).dropna()\n",
        "    sdf['mcq_pct'] = sdf['mcq_accuracy'] * 100\n",
        "    sdf['osq_pct'] = sdf['osq_score'] * 100\n",
        "    x = sdf['mcq_pct'].values\n",
        "    y = sdf['osq_pct'].values\n",
        "    from scipy.stats import linregress as lr\n",
        "    sl, ic, rv, pv, _ = lr(x, y)\n",
        "\n",
        "    # Style\n",
        "    plt.rcParams.update({'font.family': 'serif', 'font.size': 11,\n",
        "        'axes.linewidth': 0.8, 'axes.edgecolor': '#333333',\n",
        "        'grid.alpha': 0.25, 'grid.linewidth': 0.5, 'figure.dpi': 200})\n",
        "    C_GREEN, C_AMBER, C_RED = '#2d936c', '#c4820e', '#c0392b'\n",
        "    C_DIAG, C_BOUND = '#555555', '#2d936c'\n",
        "\n",
        "    fig, ax = plt.subplots(figsize=(14, 11))\n",
        "    ax.set_xlim(0, 100); ax.set_ylim(0, 100)\n",
        "    ax.set_xlabel('MCQ Accuracy (%)', fontsize=13, labelpad=10)\n",
        "    ax.set_ylabel('OSQ Accuracy (%)', fontsize=13, labelpad=10)\n",
        "    ax.set_aspect('equal')\n",
        "    ax.set_xticks(np.arange(0, 101, 20))\n",
        "    ax.set_yticks(np.arange(0, 101, 20))\n",
        "\n",
        "    def add_p(pts, fc, alpha):\n",
        "        ax.add_patch(MplPolygon(pts, closed=True, fc=fc, ec='none', alpha=alpha))\n",
        "\n",
        "    # Regions\n",
        "    add_p([(0,15),(0,100),(85,100)], fc=C_RED, alpha=0.18)\n",
        "    add_p([(15,0),(100,0),(100,85)], fc=C_RED, alpha=0.18)\n",
        "    add_p([(0,5),(0,15),(85,100),(95,100)], fc=C_AMBER, alpha=0.20)\n",
        "    add_p([(5,0),(15,0),(100,85),(100,95)], fc=C_AMBER, alpha=0.20)\n",
        "    add_p([(85,80),(85,90),(95,100),(100,100),(100,95)], fc=C_GREEN, alpha=0.30)\n",
        "\n",
        "    # Boundary lines\n",
        "    lkw = dict(linewidth=0.9, linestyle='--', zorder=3)\n",
        "    ax.plot([0,100],[0,100], color=C_DIAG, linewidth=1.1, linestyle='-', zorder=3, alpha=0.6)\n",
        "    ax.plot([0,100],[5,105], color=C_GREEN, **lkw, alpha=0.55)\n",
        "    ax.plot([0,100],[-5,95], color=C_GREEN, **lkw, alpha=0.55)\n",
        "    ax.plot([0,100],[15,115], color=C_RED, **lkw, alpha=0.55)\n",
        "    ax.plot([0,100],[-15,85], color=C_RED, **lkw, alpha=0.55)\n",
        "    ax.axvline(85, color=C_BOUND, linewidth=1.0, linestyle=':', zorder=3, alpha=0.7)\n",
        "\n",
        "    # Regression line\n",
        "    xr = np.linspace(0, 100, 400)\n",
        "    ax.plot(xr, sl*xr+ic, ls='--', color='gray', lw=1.5, zorder=4,\n",
        "            label=f'Linear fit (R$^2$={rv**2:.3f}, p={pv:.4f})')\n",
        "\n",
        "    # Data points\n",
        "    pal = sns.color_palette('tab20', len(sdf))\n",
        "    for (cat, row), col in zip(sdf.iterrows(), pal):\n",
        "        ax.scatter(row['mcq_pct'], row['osq_pct'], s=200, color=col,\n",
        "                   edgecolors='black', linewidths=0.7, alpha=0.90, zorder=6)\n",
        "        ax.annotate(cat, (row['mcq_pct'], row['osq_pct']),\n",
        "                    xytext=(7,7), textcoords='offset points', fontsize=8.5,\n",
        "                    bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='gray', alpha=0.7),\n",
        "                    zorder=7)\n",
        "\n",
        "    # Region labels\n",
        "    lbl = dict(fontsize=9, ha='center', va='center', style='italic',\n",
        "               path_effects=[pe.withStroke(linewidth=3, foreground='white')])\n",
        "    ax.text(92.5,93,'MCQ-sufficient\\n($x$ >= 85%, |d| < 5)',\n",
        "            fontsize=8.5, ha='center', va='center', style='italic',\n",
        "            path_effects=[pe.withStroke(linewidth=3, foreground='white')], color='#1a6b4a', zorder=8)\n",
        "    ax.text(30,78,'Dual-modality\\nrequired (|d| >= 15)', **lbl, color=C_RED, zorder=8)\n",
        "    ax.text(78,22,'Dual-modality\\nrequired (|d| >= 15)', **lbl, color=C_RED, zorder=8)\n",
        "    ax.text(30,28,'Dual-modality\\nrecommended (5-15%)', **lbl, color='#8a5e00', zorder=8)\n",
        "    ax.text(68,70,'Dual-modality\\nrecommended (5-15%)', **lbl, color='#8a5e00', zorder=8)\n",
        "\n",
        "    # Legend\n",
        "    handles = [\n",
        "        MplPatch(fc=C_GREEN, alpha=0.30, ec='#1a6b4a', lw=0.6,\n",
        "                 label='MCQ-sufficient (|d| < 5%, Acc >= 85%)'),\n",
        "        MplPatch(fc=C_AMBER, alpha=0.20, ec='#8a5e00', lw=0.6,\n",
        "                 label='Dual-modality recommended (5% <= |d| < 15%)'),\n",
        "        MplPatch(fc=C_RED, alpha=0.18, ec=C_RED, lw=0.6,\n",
        "                 label='Dual-modality required (|d| >= 15%)'),\n",
        "        plt.Line2D([0],[0], color='gray', lw=1.5, ls='--',\n",
        "                   label=f'Linear fit (R$^2$={rv**2:.3f})'),\n",
        "        plt.Line2D([0],[0], color=C_DIAG, lw=1.1, ls='-',\n",
        "                   label='Perfect agreement'),\n",
        "    ]\n",
        "    leg = ax.legend(handles=handles, loc='lower right', frameon=True,\n",
        "                    fontsize=9, framealpha=0.92, edgecolor='#cccccc',\n",
        "                    borderpad=0.8, handlelength=1.5)\n",
        "    leg.get_frame().set_linewidth(0.6)\n",
        "\n",
        "    ax.set_title(f'MCQ vs OSQ Accuracy by INCOSE Category\\nwith Qualification Classification Regions {title_suffix}',\n",
        "                 fontsize=14, fontweight='bold', pad=12)\n",
        "    ax.grid(True, which='major', color='#cccccc')\n",
        "    fig.tight_layout(pad=1.5)\n",
        "    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight', facecolor='white')\n",
        "    plt.show()\n",
        "    plt.close(fig)\n",
        "    print(f'Saved: {filename}')\n",
        "\n",
        "make_region_scatter('category_short', '(Leaf-Level Categories)',\n",
        "                    'fig_mcq_vs_osq_scatter_regions.png')"
    ],
    "outputs": [],
    "execution_count": None
})

for i, cell in enumerate(new_cells):
    cells.insert(insert_at + i, cell)

print(f"Inserted {len(new_cells)} cells at position {insert_at}")

# Renumber subsequent sections: 6.10 -> 6.11, 6.11 -> 6.12, 6.12 -> 6.13, 6.13 -> 6.14
for i in range(insert_at + len(new_cells), len(cells)):
    src = ''.join(cells[i].get('source', []))
    if '## 7.' in src:
        break
    for old_num, new_num in [('### 6.13', '### 6.15'), ('### 6.12', '### 6.14'),
                              ('### 6.11', '### 6.13'), ('### 6.10', '### 6.12')]:
        if old_num in src:
            cells[i]['source'] = [src.replace(old_num, new_num)]
            break

print(f"Total cells after insertion: {len(cells)}")

nb['cells'] = cells
with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Done!")

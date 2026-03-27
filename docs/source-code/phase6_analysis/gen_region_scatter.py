"""
Generate the region-annotated MCQ vs OSQ scatter plot and updated classification table.

- New figure: fig_mcq_vs_osq_scatter_regions.png
  Overlay classification regions (MCQ-sufficient, dual-modality recommended,
  dual-modality required) behind the actual INCOSE category data points.

- Updated table: table_qualification_classification.csv/.tex
  Classification based on region boundaries: |delta| < 5 and MCQ >= 85 => MCQ-sufficient,
  5 <= |delta| < 15 => dual-modality recommended, |delta| >= 15 => dual-modality required.

Region logic matches user-provided Python code (percentage scale), adapted to 0-1 data.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Polygon, Patch
from pathlib import Path
from scipy.stats import linregress

sys.path.insert(0, str(Path(__file__).parent))
from parsers import parse_mcq_samples, parse_osq_judged_samples, align_mcq_osq_results


# ---- Config ----
phase4_dir = Path(__file__).parent.parent / 'phase4_inference' / 'output'
phase5_dir = Path(__file__).parent.parent / 'phase5_llm_as_a_judge'
output_dir = Path(__file__).parent / 'output_v2'
output_dir.mkdir(exist_ok=True)
manuscript_dir = Path(__file__).parent.parent.parent / 'manuscript' / 'overleaf' / 'figs' / 'ch4' / '4.6'
manuscript_dir.mkdir(parents=True, exist_ok=True)


def explode_categories(df, category_col='category'):
    """Split multi-category assignments and add short/toplevel labels."""
    df = df.copy()
    df = df.dropna(subset=[category_col])
    df = df[df[category_col].str.strip() != '']
    df[category_col] = df[category_col].str.split('\n')
    df = df.explode(category_col).reset_index(drop=True)
    df[category_col] = df[category_col].str.strip()
    df = df[df[category_col] != '']
    df['category_short'] = df[category_col].str.split('/').str[-1].str.strip()
    parts = df[category_col].str.split('/')
    df['category_toplevel'] = parts.apply(
        lambda p: p[1].strip() if len(p) > 1 else p[0].strip()
    )
    return df


def save_to_both(fig, filename):
    """Save figure to both output_v2 and manuscript directories."""
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(manuscript_dir / filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  Saved: {filename}')


# ---- Load Data ----
print('=' * 80)
print('REGION-ANNOTATED SCATTER PLOT + UPDATED CLASSIFICATION')
print('=' * 80)

print('\nLoading MCQ data...')
mcq_data = parse_mcq_samples(phase4_dir, use_latest=True)
mcq_df = pd.DataFrame(mcq_data)
print(f'  {len(mcq_df):,} MCQ samples, {mcq_df["model"].nunique()} models')

print('Loading OSQ data...')
osq_data = parse_osq_judged_samples(phase5_dir)
osq_df = pd.DataFrame(osq_data)
osq_filtered = osq_df.copy()
print(f'  {len(osq_filtered):,} OSQ samples, {osq_filtered["model"].nunique()} models')

print('Aligning...')
aligned_data = align_mcq_osq_results(mcq_df, osq_filtered.to_dict('records'))
aligned_df = pd.DataFrame(aligned_data)
print(f'  {len(aligned_df):,} aligned records')

# ---- Prepare category data ----
print('\nPreparing category data...')
mcq_cat = explode_categories(mcq_df, 'category')
osq_success = osq_filtered[osq_filtered['parse_status'] == 'success'].copy()
osq_cat = explode_categories(osq_success, 'category')
osq_cat['osq_accuracy'] = osq_cat['percentage'] / 100.0

aligned_complete = aligned_df[
    (aligned_df['mcq_avg_correct'].notna()) &
    (aligned_df['osq_percentage'].notna())
].copy()
aligned_cat = explode_categories(aligned_complete, 'category')
aligned_cat['mcq_score'] = aligned_cat['mcq_avg_correct']
aligned_cat['osq_score'] = aligned_cat['osq_percentage'] / 100.0
aligned_cat['delta'] = aligned_cat['mcq_score'] - aligned_cat['osq_score']


# ==================================================================
# 1. REGION-ANNOTATED SCATTER PLOT
# ==================================================================
print('\n--- Generating region-annotated scatter plot ---')

# Aggregate: per-category mean across all models
mcq_by_cat = mcq_cat.groupby('category_short')['is_correct'].mean()
osq_by_cat = osq_cat.groupby('category_short')['osq_accuracy'].mean()

scatter_df = pd.DataFrame({
    'mcq_accuracy': mcq_by_cat,
    'osq_score': osq_by_cat
}).dropna()

# Convert to percentage for the region plot
scatter_df['mcq_pct'] = scatter_df['mcq_accuracy'] * 100
scatter_df['osq_pct'] = scatter_df['osq_score'] * 100

x_pct = scatter_df['mcq_pct'].values
y_pct = scatter_df['osq_pct'].values

# Regression (on percentage scale)
slope, intercept, r_val, p_val, _ = linregress(x_pct, y_pct)

# ── Style setup ──────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#333333",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "figure.dpi": 200,
})

# ── Color palette ────────────────────────────────────────────────────────
C_GREEN = "#2d936c"   # MCQ-sufficient
C_AMBER = "#c4820e"   # Dual-modality recommended
C_RED   = "#c0392b"   # Dual-modality required
C_DIAG  = "#555555"   # Diagonal reference
C_BOUND = "#2d936c"   # x=85 boundary

# ── Figure ───────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 11))

# Use full 0-100 range so region polygons render with clean geometry
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("MCQ Accuracy (%)", fontsize=13, labelpad=10)
ax.set_ylabel("OSQ Accuracy (%)", fontsize=13, labelpad=10)
ax.set_aspect("equal")
ax.set_xticks(np.arange(0, 101, 20))
ax.set_yticks(np.arange(0, 101, 20))

# ── Thresholds (percentage scale) ────────────────────────────────────────
D_SMALL, D_MOD, X_MIN = 5, 15, 85

# ── Helper ───────────────────────────────────────────────────────────────
def add_poly(pts, fc, alpha):
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec="none", alpha=alpha))

# ── Classification regions (exact geometry from user specification) ───────

# Dual-modality REQUIRED (|delta| >= 15) — drawn first (background)
add_poly([(0, 15), (0, 100), (85, 100)],       fc=C_RED, alpha=0.18)
add_poly([(15, 0), (100, 0),  (100, 85)],      fc=C_RED, alpha=0.18)

# Dual-modality RECOMMENDED (5 <= |delta| < 15)
add_poly([(0, 5), (0, 15), (85, 100), (95, 100)],     fc=C_AMBER, alpha=0.20)
add_poly([(5, 0), (15, 0), (100, 85), (100, 95)],     fc=C_AMBER, alpha=0.20)

# MCQ-sufficient (|delta| < 5 AND x >= 85)
add_poly(
    [(85, 80), (85, 90), (95, 100), (100, 100), (100, 95)],
    fc=C_GREEN, alpha=0.30
)

# ── Boundary lines ───────────────────────────────────────────────────────
line_kw = dict(linewidth=0.9, linestyle="--", zorder=3)
x_line = np.linspace(0, 100, 400)

# Main diagonal (perfect agreement)
ax.plot([0, 100], [0, 100], color=C_DIAG, linewidth=1.1, linestyle="-", zorder=3, alpha=0.6)

# |delta| = 5 boundaries
ax.plot([0, 100], [5, 105],  color=C_GREEN, **line_kw, alpha=0.55)
ax.plot([0, 100], [-5, 95],  color=C_GREEN, **line_kw, alpha=0.55)

# |delta| = 15 boundaries
ax.plot([0, 100], [15, 115], color=C_RED, **line_kw, alpha=0.55)
ax.plot([0, 100], [-15, 85], color=C_RED, **line_kw, alpha=0.55)

# x = 85 vertical boundary
ax.axvline(X_MIN, color=C_BOUND, linewidth=1.0, linestyle=":", zorder=3, alpha=0.7)

# ── Regression line ──────────────────────────────────────────────────────
ax.plot(x_line, slope * x_line + intercept, linestyle='--', color='gray',
        linewidth=1.5, zorder=4,
        label=f'Linear fit (R$^2$={r_val**2:.3f}, p={p_val:.4f})')

# ── Data points ──────────────────────────────────────────────────────────
import seaborn as sns
palette = sns.color_palette("tab20", len(scatter_df))

for (cat, row), color in zip(scatter_df.iterrows(), palette):
    ax.scatter(
        row['mcq_pct'], row['osq_pct'],
        s=200, color=color, edgecolors='black', linewidths=0.7, alpha=0.90, zorder=6
    )
    ax.annotate(
        cat, (row['mcq_pct'], row['osq_pct']),
        xytext=(7, 7), textcoords='offset points', fontsize=8.5,
        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='gray', alpha=0.7),
        zorder=7
    )

# ── Region labels ────────────────────────────────────────────────────────
label_kw = dict(
    fontsize=9, ha="center", va="center", style="italic",
    path_effects=[pe.withStroke(linewidth=3, foreground="white")]
)

# MCQ-sufficient label
ax.text(92.5, 93, "MCQ-sufficient\n($x$ \u2265 85%,  |\u0394| < 5)",
        fontsize=8.5, ha="center", va="center", style="italic",
        path_effects=[pe.withStroke(linewidth=3, foreground="white")],
        color="#1a6b4a", zorder=8)

# Dual-modality required labels
ax.text(30, 78, "Dual-modality\nrequired  (|\u0394| \u2265 15)",
        **label_kw, color=C_RED, zorder=8)
ax.text(78, 22, "Dual-modality\nrequired  (|\u0394| \u2265 15)",
        **label_kw, color=C_RED, zorder=8)

# Dual-modality recommended labels
ax.text(30, 28, "Dual-modality\nrecommended  (5\u201315%)",
        **label_kw, color="#8a5e00", zorder=8)
ax.text(68, 70, "Dual-modality\nrecommended  (5\u201315%)",
        **label_kw, color="#8a5e00", zorder=8)

# ── Delta annotation arrows ─────────────────────────────────────────────
arr_kw = dict(arrowstyle="<->", color="#666666", lw=0.8)
ax.annotate("", xy=(50, 55), xytext=(50, 50),
            arrowprops=arr_kw, zorder=8)
ax.text(52, 52.5, "|\u0394| = 5", fontsize=7.5, color="#666666", va="center",
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")], zorder=8)

ax.annotate("", xy=(40, 55), xytext=(40, 40),
            arrowprops=arr_kw, zorder=8)
ax.text(37.5, 47.5, "|\u0394| = 15", fontsize=7.5, color="#666666", va="center", ha="right",
        path_effects=[pe.withStroke(linewidth=2.5, foreground="white")], zorder=8)

# ── Legend ────────────────────────────────────────────────────────────────
handles = [
    Patch(fc=C_GREEN, alpha=0.30, ec="#1a6b4a", lw=0.6,
          label="MCQ-sufficient  (|\u0394| < 5%, Acc \u2265 85%)"),
    Patch(fc=C_AMBER, alpha=0.20, ec="#8a5e00", lw=0.6,
          label="Dual-modality recommended  (5% \u2264 |\u0394| < 15%)"),
    Patch(fc=C_RED, alpha=0.18, ec=C_RED, lw=0.6,
          label="Dual-modality required  (|\u0394| \u2265 15%)"),
    plt.Line2D([0], [0], color='gray', linewidth=1.5, linestyle='--',
               label=f'Linear fit (R$^2$={r_val**2:.3f})'),
    plt.Line2D([0], [0], color=C_DIAG, linewidth=1.1, linestyle='-',
               label='Perfect agreement'),
]
leg = ax.legend(
    handles=handles, loc="lower right", frameon=True,
    fontsize=9, framealpha=0.92, edgecolor="#cccccc",
    borderpad=0.8, handlelength=1.5
)
leg.get_frame().set_linewidth(0.6)

# ── Title & grid ─────────────────────────────────────────────────────────
ax.set_title('MCQ vs OSQ Accuracy by INCOSE Category\nwith Qualification Classification Regions',
             fontsize=14, fontweight='bold', pad=12)
ax.grid(True, which="major", color="#cccccc")
fig.tight_layout(pad=1.5)
save_to_both(fig, 'fig_mcq_vs_osq_scatter_regions.png')


# ==================================================================
# 2. UPDATED CLASSIFICATION TABLE (region-based)
# ==================================================================
print('\n--- Generating updated classification table ---')

# Per-category stats
cat_stats = aligned_cat.groupby('category_short').agg(
    mean_delta=('delta', 'mean'),
    median_delta=('delta', 'median'),
    mean_mcq=('mcq_score', 'mean'),
    mean_osq=('osq_score', 'mean'),
    n_samples=('delta', 'count')
).reset_index()

# Convert to percentage for classification
cat_stats['mean_mcq_pct'] = cat_stats['mean_mcq'] * 100
cat_stats['abs_delta_pct'] = cat_stats['mean_delta'].abs() * 100


def classify_modality_regions(row):
    """Classify based on the region boundaries in the scatter plot."""
    abs_delta = row['abs_delta_pct']
    mcq_acc = row['mean_mcq_pct']

    if row['n_samples'] < 30:
        return 'Insufficient coverage'
    if abs_delta < 5 and mcq_acc >= 85:
        return 'MCQ-sufficient'
    if abs_delta < 15:
        return 'Dual-modality recommended'
    return 'Dual-modality required'


cat_stats['classification'] = cat_stats.apply(classify_modality_regions, axis=1)
cat_stats = cat_stats.sort_values('mean_delta', ascending=False)

# Format table
class_table = cat_stats[['category_short', 'mean_mcq', 'mean_osq',
                          'mean_delta', 'median_delta', 'abs_delta_pct',
                          'n_samples', 'classification']].copy()
class_table.columns = ['Category', 'Mean MCQ Acc.', 'Mean OSQ Score',
                        'Mean Delta', 'Median Delta', '|Delta| (%)',
                        'N', 'Classification']

# Save CSV
class_table.to_csv(output_dir / 'table_qualification_classification.csv', index=False)
class_table.to_csv(manuscript_dir / 'table_qualification_classification.csv', index=False)

# Save LaTeX
latex_str = class_table.to_latex(
    index=False,
    column_format='lrrrrrrl',
    escape=True,
    float_format='%.3f'
)
for tex_dir in [manuscript_dir, output_dir]:
    with open(tex_dir / 'table_qualification_classification.tex', 'w') as f:
        f.write(latex_str)

print(f'  Saved: table_qualification_classification.csv/.tex')
print(f'\n--- Classification Results ---')
for _, row in class_table.iterrows():
    print(f'  {row["Category"]:55s} -> {row["Classification"]:30s}  '
          f'(|delta|={row["|Delta| (%)"]:.1f}%, MCQ={row["Mean MCQ Acc."]:.3f}, n={row["N"]})')

# Summary counts
print(f'\nClassification summary:')
for cls, count in class_table['Classification'].value_counts().items():
    print(f'  {cls}: {count}')

print('\n' + '=' * 80)
print('COMPLETE')
print('=' * 80)

for f in sorted(list(output_dir.glob('*scatter_regions*')) + list(output_dir.glob('*qualification*'))):
    size_kb = f.stat().st_size / 1024
    print(f'  {f.name:55s} ({size_kb:8.1f} KB)')

"""
Generate new INCOSE category analysis artifacts:
- MCQ vs OSQ scatter plots by category (20 subcategories + 6 top-level)
- Delta tables with marginal statistics (mean + median per model and per category)
- Qualification classification table

Outputs go to both output_v2/ (for notebook) and manuscript figs/ch4/4.6/ (for LaTeX).
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.patches import Patch
from scipy.stats import linregress

sys.path.insert(0, str(Path(__file__).parent))
from parsers import parse_mcq_samples, parse_osq_judged_samples, align_mcq_osq_results

# ---- Config ----
phase4_dir = Path(__file__).parent.parent / 'phase4_inference' / 'output'
phase5_dir = Path(__file__).parent.parent / 'phase5_llm_as_a_judge'
output_dir = Path(__file__).parent / 'output_v2'
output_dir.mkdir(exist_ok=True)

# Also output to manuscript figures directory
manuscript_dir = Path(__file__).parent.parent.parent / 'manuscript' / 'overleaf' / 'figs' / 'ch4' / '4.6'
manuscript_dir.mkdir(parents=True, exist_ok=True)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')


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


# ---- Load Data ----
print('=' * 80)
print('INCOSE CATEGORY ANALYSIS - NEW ARTIFACTS')
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

# Sort orders
model_order = mcq_cat.groupby('model')['is_correct'].mean().sort_values(ascending=False).index.tolist()
cat_order = sorted(mcq_cat['category_short'].unique())
top_order = sorted(mcq_cat['category_toplevel'].unique())


def save_to_both(fig, filename):
    """Save figure to both output_v2 and manuscript directories."""
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
    fig.savefig(manuscript_dir / filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {filename}')


# ==================================================================
# 1. MCQ vs OSQ SCATTER PLOTS BY CATEGORY
# ==================================================================

def make_category_scatter(cat_col, title_suffix, filename):
    """Create MCQ vs OSQ scatter plot where each point is one category."""
    # Aggregate: per-category mean across all models
    mcq_by_cat = mcq_cat.groupby(cat_col)['is_correct'].mean()
    osq_by_cat = osq_cat.groupby(cat_col)['osq_accuracy'].mean()

    scatter_df = pd.DataFrame({
        'mcq_accuracy': mcq_by_cat,
        'osq_score': osq_by_cat
    }).dropna()

    x = scatter_df['mcq_accuracy'].values
    y = scatter_df['osq_score'].values

    # Regression
    slope, intercept, r_val, p_val, _ = linregress(x, y)

    # Plot
    fig, ax = plt.subplots(figsize=(12, 9))
    palette = sns.color_palette("tab20", len(scatter_df))

    for (cat, row), color in zip(scatter_df.iterrows(), palette):
        ax.scatter(
            row['mcq_accuracy'], row['osq_score'],
            s=180, color=color, edgecolors='black', linewidths=0.6, alpha=0.85, zorder=5
        )
        ax.annotate(
            cat, (row['mcq_accuracy'], row['osq_score']),
            xytext=(6, 6), textcoords='offset points', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='gray', alpha=0.6)
        )

    # Reference lines
    x_line = np.linspace(0, 1, 400)
    tolerance = 0.02
    ax.plot(x_line, x_line, color='red', linestyle=':', linewidth=2, label='Perfect Agreement')
    ax.fill_between(x_line, x_line - tolerance, x_line + tolerance,
                    color='gray', alpha=0.15, label=f'+/-{tolerance:.02f} Agreement Band')
    ax.plot(x_line, slope * x_line + intercept, linestyle='--', color='gray',
            linewidth=2, label=f'R^2={r_val**2:.3f}, p={p_val:.4f}')

    # Axis limits - zoom to data range with padding
    x_min, x_max = x.min() - 0.03, x.max() + 0.03
    y_min, y_max = y.min() - 0.03, y.max() + 0.03
    lo = min(x_min, y_min)
    hi = max(x_max, y_max)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)

    # Region labels
    x_lo, x_hi = ax.get_xlim()
    y_lo, y_hi = ax.get_ylim()
    x_range = x_hi - x_lo
    y_range = y_hi - y_lo

    ax.text(x_lo + 0.03 * x_range, y_hi - 0.05 * y_range,
            "OSQ > MCQ\n(Category performs better on OSQ)",
            ha='left', va='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.45))
    ax.text(x_hi - 0.03 * x_range, y_lo + 0.05 * y_range,
            "OSQ < MCQ\n(Category performs better on MCQ)",
            ha='right', va='bottom', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', alpha=0.45))

    ax.set_xlabel('MCQ Accuracy (model-averaged)', fontsize=12)
    ax.set_ylabel('OSQ Mean Score (model-averaged, 0-1)', fontsize=12)
    ax.set_title(f'MCQ Accuracy vs OSQ Score by INCOSE Category\n{title_suffix}',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    save_to_both(fig, filename)


print('\n--- Generating MCQ vs OSQ scatter plots ---')
make_category_scatter('category_short', '(Leaf-Level Categories)',
                      'fig_mcq_vs_osq_scatter_by_category.png')
make_category_scatter('category_toplevel', '(Top-Level Groups)',
                      'fig_mcq_vs_osq_scatter_by_toplevel.png')


# ==================================================================
# 2. DELTA TABLES WITH MARGINAL STATISTICS
# ==================================================================

def make_delta_table_with_marginals(cat_col, filename_csv, filename_tex, caption, label):
    """Create delta table (model x category) with mean/median marginals."""
    # Compute per-model, per-category delta
    delta_data = aligned_cat.groupby(['model', cat_col])['delta'].mean().reset_index()
    delta_pivot = delta_data.pivot(index='model', columns=cat_col, values='delta')

    # Sort models and categories consistently
    models_sorted = [m for m in model_order if m in delta_pivot.index]
    if cat_col == 'category_short':
        cats_sorted = [c for c in cat_order if c in delta_pivot.columns]
    else:
        cats_sorted = [c for c in top_order if c in delta_pivot.columns]
    delta_pivot = delta_pivot.reindex(index=models_sorted, columns=cats_sorted)

    # Add per-model marginals (rightmost columns)
    delta_pivot['Mean Delta'] = delta_pivot.mean(axis=1)
    delta_pivot['Median Delta'] = delta_pivot.median(axis=1)

    # Add per-category marginals (bottom rows)
    cat_cols = cats_sorted  # original category columns only
    mean_row = delta_pivot[cat_cols].mean(axis=0)
    median_row = delta_pivot[cat_cols].median(axis=0)

    # Also compute marginals for the marginal columns
    mean_row['Mean Delta'] = delta_pivot['Mean Delta'].mean()
    mean_row['Median Delta'] = delta_pivot['Median Delta'].mean()
    median_row['Mean Delta'] = delta_pivot['Mean Delta'].median()
    median_row['Median Delta'] = delta_pivot['Median Delta'].median()

    mean_row.name = 'Mean (across models)'
    median_row.name = 'Median (across models)'

    # Append marginal rows
    delta_with_marginals = pd.concat([delta_pivot, mean_row.to_frame().T, median_row.to_frame().T])

    # Save CSV
    delta_with_marginals.to_csv(output_dir / filename_csv)
    delta_with_marginals.to_csv(manuscript_dir / filename_csv)
    print(f'  Saved: {filename_csv}')

    # Format for LaTeX
    formatted = delta_with_marginals.copy()
    for col in formatted.columns:
        formatted[col] = formatted[col].apply(
            lambda v: f'{v:+.3f}' if pd.notna(v) else '--'
        )

    # Write raw LaTeX table (no \begin{table} wrapper - chapter4.tex uses \input with \resizebox)
    col_fmt = 'l' + 'r' * len(formatted.columns)

    # Truncate long column names for readability
    short_cols = []
    for c in formatted.columns:
        if len(c) > 20:
            short_cols.append(c[:18] + '..')
        else:
            short_cols.append(c)
    formatted.columns = short_cols

    latex_str = formatted.to_latex(
        column_format=col_fmt,
        escape=True,
        float_format='%.3f'
    )

    tex_path = manuscript_dir / filename_tex
    with open(tex_path, 'w') as f:
        f.write(latex_str)
    # Also save to output_v2
    with open(output_dir / filename_tex, 'w') as f:
        f.write(latex_str)
    print(f'  Saved: {filename_tex}')

    return delta_with_marginals


print('\n--- Generating delta tables with marginals ---')
delta_full = make_delta_table_with_marginals(
    'category_short',
    'table_delta_marginals_category.csv',
    'table_delta_marginals_category.tex',
    'MCQ--OSQ Delta by INCOSE Category with Marginal Statistics',
    'tab:delta_full_marginals'
)

delta_top = make_delta_table_with_marginals(
    'category_toplevel',
    'table_delta_marginals_toplevel.csv',
    'table_delta_marginals_toplevel.tex',
    'MCQ--OSQ Delta by INCOSE Top-Level Group with Marginal Statistics',
    'tab:delta_toplevel_marginals'
)


# ==================================================================
# 3. QUALIFICATION CLASSIFICATION TABLE
# ==================================================================

print('\n--- Generating qualification classification table ---')

# Compute per-category stats
cat_stats = aligned_cat.groupby('category_short').agg(
    mean_delta=('delta', 'mean'),
    median_delta=('delta', 'median'),
    mean_mcq=('mcq_score', 'mean'),
    mean_osq=('osq_score', 'mean'),
    n_samples=('delta', 'count')
).reset_index()

# Apply classification
def classify_modality(row):
    if row['n_samples'] < 30:
        return 'Insufficient coverage'
    if row['mean_delta'] >= 0.15 and row['mean_mcq'] >= 0.85:
        return 'MCQ-sufficient'
    if row['mean_delta'] >= 0.05:
        return 'Dual-modality recommended'
    return 'OSQ-preferred'

cat_stats['classification'] = cat_stats.apply(classify_modality, axis=1)
cat_stats = cat_stats.sort_values('mean_delta', ascending=False)

# Format for display
class_table = cat_stats[['category_short', 'mean_mcq', 'mean_osq',
                          'mean_delta', 'median_delta', 'n_samples', 'classification']].copy()
class_table.columns = ['Category', 'Mean MCQ Acc.', 'Mean OSQ Score',
                        'Mean Delta', 'Median Delta', 'N', 'Classification']

# Save CSV
class_table.to_csv(output_dir / 'table_qualification_classification.csv', index=False)
class_table.to_csv(manuscript_dir / 'table_qualification_classification.csv', index=False)

# Save LaTeX
latex_str = class_table.to_latex(
    index=False,
    column_format='lrrrrrl',
    escape=True,
    float_format='%.3f'
)
for tex_dir in [manuscript_dir, output_dir]:
    with open(tex_dir / 'table_qualification_classification.tex', 'w') as f:
        f.write(latex_str)

print(f'  Saved: table_qualification_classification.csv/.tex')
print(f'\n--- Classification Results ---')
for _, row in class_table.iterrows():
    print(f'  {row["Category"]:55s} -> {row["Classification"]}  '
          f'(delta={row["Mean Delta"]:+.3f}, MCQ={row["Mean MCQ Acc."]:.3f}, n={row["N"]})')


# ==================================================================
# SUMMARY
# ==================================================================
print('\n' + '=' * 80)
print('COMPLETE')
print('=' * 80)
print('\nNew artifacts:')
for f in sorted(list(output_dir.glob('*scatter*')) + list(output_dir.glob('*marginals*')) + list(output_dir.glob('*qualification*'))):
    size_kb = f.stat().st_size / 1024
    print(f'  {f.name:55s} ({size_kb:8.1f} KB)')

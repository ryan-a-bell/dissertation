"""
Standalone script to run the INCOSE Category Accuracy Analysis (Section 6).
Loads data using parsers.py and generates all 6 plots + 2 tables.
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.patches import Patch

# Add parent to path for parsers
sys.path.insert(0, str(Path(__file__).parent))
from parsers import parse_mcq_samples, parse_osq_judged_samples, align_mcq_osq_results

# ─── Configuration ────────────────────────────────────────────────────────────
phase4_dir = Path(__file__).parent.parent / 'phase4_inference' / 'output'
phase5_dir = Path(__file__).parent.parent / 'phase5_llm_as_a_judge'
output_dir = Path(__file__).parent / 'output_v2'
output_dir.mkdir(exist_ok=True)

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

MODEL_DISPLAY = {
    'claude-3.5-sonnet': 'Claude 3.5 Sonnet',
    'claude-sonnet-4-20250514': 'Claude Sonnet 4',
    'deepseek-r1:7b': 'DeepSeek R1 7B',
    'gemma3:12b': 'Gemma 3 12B',
    'gemma3:27b': 'Gemma 3 27B',
    'gemma3:4b': 'Gemma 3 4B',
    'gpt-4.1': 'GPT-4.1',
    'gpt-4.1-mini': 'GPT-4.1 Mini',
    'gpt-4.1-nano': 'GPT-4.1 Nano',
    'llama3.1:70b': 'Llama 3.1 70B',
    'llama3.1:8b': 'Llama 3.1 8B',
    'llama3.2:1b': 'Llama 3.2 1B',
    'llama3.2:3b': 'Llama 3.2 3B',
    'mistral-small3.1:24b': 'Mistral Small 3.1 24B',
    'phi4-mini': 'Phi-4 Mini',
    'phi4:14b': 'Phi-4 14B',
    'qwen3:8b': 'Qwen 3 8B',
    'qwq:32b': 'QwQ 32B',
}


def export_latex_table(df, filename, caption, label, column_format=None):
    """Export DataFrame to LaTeX table with booktabs formatting."""
    if column_format is None:
        column_format = 'l' + 'r' * (len(df.columns) - 1)

    output_path = output_dir / filename
    latex_str = df.to_latex(
        index=False,
        caption=caption,
        label=label,
        column_format=column_format,
        escape=True,
        float_format='%.3f'
    )
    # Add booktabs
    latex_str = latex_str.replace('\\hline', '')
    latex_str = latex_str.replace('\\toprule', '\\toprule')

    with open(output_path, 'w') as f:
        f.write(latex_str)
    print(f'   \u2713 Exported: {filename}')


def explode_categories(df, category_col='category'):
    """
    Handle multi-category assignments by exploding rows.
    Splits multi-category entries on '\n', explodes, and adds
    'category_short' (leaf) and 'category_toplevel' (second level).
    """
    df = df.copy()
    df = df.dropna(subset=[category_col])
    df = df[df[category_col].str.strip() != '']

    df[category_col] = df[category_col].str.split('\n')
    df = df.explode(category_col).reset_index(drop=True)
    df[category_col] = df[category_col].str.strip()
    df = df[df[category_col] != '']

    # Leaf level
    df['category_short'] = df[category_col].str.split('/').str[-1].str.strip()

    # Top-level group (second level)
    parts = df[category_col].str.split('/')
    df['category_toplevel'] = parts.apply(
        lambda p: p[1].strip() if len(p) > 1 else p[0].strip()
    )

    return df


# ─── Load Data ────────────────────────────────────────────────────────────────
print('=' * 80)
print('INCOSE CATEGORY ACCURACY ANALYSIS')
print('=' * 80)

print('\n--- Loading MCQ data ---')
mcq_data = parse_mcq_samples(phase4_dir, use_latest=True)
mcq_df = pd.DataFrame(mcq_data)
print(f'   Loaded {len(mcq_df):,} MCQ samples, {mcq_df["model"].nunique()} models')

print('\n--- Loading OSQ data ---')
osq_data = parse_osq_judged_samples(phase5_dir)
osq_df = pd.DataFrame(osq_data)
osq_filtered = osq_df.copy()  # No judge filter for now
print(f'   Loaded {len(osq_filtered):,} OSQ samples, {osq_filtered["model"].nunique()} models')

print('\n--- Aligning MCQ + OSQ ---')
aligned_data = align_mcq_osq_results(mcq_df, osq_filtered.to_dict('records'))
aligned_df = pd.DataFrame(aligned_data)
print(f'   Aligned {len(aligned_df):,} records')


# ─── 6.1 Prepare Category Data ───────────────────────────────────────────────
print('\n--- Preparing category data ---')

mcq_cat = explode_categories(mcq_df, 'category')
print(f'MCQ: {len(mcq_df):,} rows -> {len(mcq_cat):,} after category explosion')

osq_success = osq_filtered[osq_filtered['parse_status'] == 'success'].copy()
osq_cat = explode_categories(osq_success, 'category')
print(f'OSQ: {len(osq_success):,} rows -> {len(osq_cat):,} after category explosion')

aligned_complete = aligned_df[
    (aligned_df['mcq_avg_correct'].notna()) &
    (aligned_df['osq_percentage'].notna())
].copy()
aligned_cat = explode_categories(aligned_complete, 'category')
print(f'Aligned: {len(aligned_complete):,} rows -> {len(aligned_cat):,} after category explosion')

# Category summaries
print(f'\n--- Full Categories (leaf level) ---')
cat_counts = mcq_cat['category_short'].value_counts()
print(f'Unique categories: {len(cat_counts)}')
for cat, count in cat_counts.items():
    print(f'  {cat}: {count:,} samples')

print(f'\n--- Top-Level Groupings ---')
top_counts = mcq_cat['category_toplevel'].value_counts()
print(f'Unique top-level groups: {len(top_counts)}')
for grp, count in top_counts.items():
    print(f'  {grp}: {count:,} samples')


# ─── Sort orders (consistent across all plots) ───────────────────────────────
# Models sorted by overall MCQ accuracy (best at top)
model_order = mcq_cat.groupby('model')['is_correct'].mean().sort_values(ascending=False).index.tolist()
# Categories sorted alphabetically
cat_order = sorted(mcq_cat['category_short'].unique())
top_order = sorted(mcq_cat['category_toplevel'].unique())


# ─── 6.2 MCQ Accuracy Heatmap (Full Categories) ─────────────────────────────
print('\n--- 6.2 MCQ Accuracy Heatmap (Full Categories) ---')

mcq_accuracy = mcq_cat.groupby(['model', 'category_short'])['is_correct'].mean().reset_index()
mcq_pivot = mcq_accuracy.pivot(index='model', columns='category_short', values='is_correct')
mcq_pivot = mcq_pivot.reindex(index=model_order, columns=cat_order)

fig, ax = plt.subplots(figsize=(22, 12))
sns.heatmap(
    mcq_pivot,
    annot=True, fmt='.0%',
    cmap='RdYlGn', vmin=0.5, vmax=1.0,
    linewidths=0.5, linecolor='white',
    cbar_kws={'label': 'MCQ Accuracy', 'shrink': 0.8},
    ax=ax
)
ax.set_title('MCQ Accuracy by Model and INCOSE Category', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('INCOSE Category', fontsize=12)
ax.set_ylabel('Model', fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / 'fig_mcq_accuracy_by_incose_category.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_mcq_accuracy_by_incose_category.png')


# ─── 6.3 OSQ Accuracy Heatmap (Full Categories) ─────────────────────────────
print('\n--- 6.3 OSQ Accuracy Heatmap (Full Categories) ---')

osq_cat['osq_accuracy'] = osq_cat['percentage'] / 100.0
osq_accuracy = osq_cat.groupby(['model', 'category_short'])['osq_accuracy'].mean().reset_index()
osq_pivot = osq_accuracy.pivot(index='model', columns='category_short', values='osq_accuracy')

osq_models = [m for m in model_order if m in osq_pivot.index]
osq_cats = [c for c in cat_order if c in osq_pivot.columns]
osq_pivot = osq_pivot.reindex(index=osq_models, columns=osq_cats)

fig, ax = plt.subplots(figsize=(22, 12))
sns.heatmap(
    osq_pivot,
    annot=True, fmt='.0%',
    cmap='RdYlGn', vmin=0.5, vmax=1.0,
    linewidths=0.5, linecolor='white',
    cbar_kws={'label': 'OSQ Mean Score', 'shrink': 0.8},
    ax=ax
)
ax.set_title('OSQ Mean Score by Model and INCOSE Category', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('INCOSE Category', fontsize=12)
ax.set_ylabel('Model', fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / 'fig_osq_accuracy_by_incose_category.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_osq_accuracy_by_incose_category.png')


# ─── 6.4 MCQ-OSQ Delta (Full Categories) ─────────────────────────────────────
print('\n--- 6.4 MCQ-OSQ Delta (Full Categories) ---')

aligned_cat['mcq_score'] = aligned_cat['mcq_avg_correct']
aligned_cat['osq_score'] = aligned_cat['osq_percentage'] / 100.0
aligned_cat['delta'] = aligned_cat['mcq_score'] - aligned_cat['osq_score']

# Per-model delta table
delta_by_model_cat = aligned_cat.groupby(['model', 'category_short'])['delta'].mean().reset_index()
delta_pivot_full = delta_by_model_cat.pivot(index='model', columns='category_short', values='delta')
delta_models = [m for m in model_order if m in delta_pivot_full.index]
delta_cats = [c for c in cat_order if c in delta_pivot_full.columns]
delta_pivot_full = delta_pivot_full.reindex(index=delta_models, columns=delta_cats)

# Export CSV
delta_pivot_full.to_csv(output_dir / 'table_mcq_osq_delta_by_incose_category.csv')
print(f'\u2705 Saved: table_mcq_osq_delta_by_incose_category.csv')

# Export LaTeX
delta_latex = delta_pivot_full.copy()
delta_latex.columns = [c[:25] + '...' if len(c) > 28 else c for c in delta_latex.columns]
export_latex_table(
    delta_latex.reset_index(),
    'table_mcq_osq_delta_by_incose_category.tex',
    'MCQ--OSQ Accuracy Delta by INCOSE Category (All Models)',
    'tab:mcq_osq_delta_category'
)

# Diverging bar chart (averaged across models)
cat_delta = aligned_cat.groupby('category_short')['delta'].agg(['mean', 'std', 'count']).reset_index()
cat_delta.columns = ['category', 'mean_delta', 'std_delta', 'n']
cat_delta = cat_delta.sort_values('mean_delta', ascending=True)

colors = ['#2196F3' if d >= 0 else '#FF9800' for d in cat_delta['mean_delta']]

fig, ax = plt.subplots(figsize=(14, max(8, len(cat_delta) * 0.5)))
bars = ax.barh(cat_delta['category'], cat_delta['mean_delta'], color=colors, edgecolor='white', height=0.7)
ax.axvline(x=0, color='black', linewidth=0.8, linestyle='-')

for bar, val in zip(bars, cat_delta['mean_delta']):
    x_pos = bar.get_width()
    ha = 'left' if val >= 0 else 'right'
    offset = 0.005 if val >= 0 else -0.005
    ax.text(x_pos + offset, bar.get_y() + bar.get_height()/2,
            f'{val:+.1%}', va='center', ha=ha, fontsize=9, fontweight='bold')

ax.set_xlabel('Mean MCQ \u2212 OSQ Delta (across models)', fontsize=12)
ax.set_ylabel('')
ax.set_title('MCQ vs. OSQ Accuracy Gap by INCOSE Category\n(Positive = MCQ stronger, Negative = OSQ stronger)',
             fontsize=14, fontweight='bold')
ax.tick_params(axis='y', labelsize=10)
legend_elements = [
    Patch(facecolor='#2196F3', label='MCQ advantage'),
    Patch(facecolor='#FF9800', label='OSQ advantage')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / 'fig_mcq_osq_delta_by_incose_category.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_mcq_osq_delta_by_incose_category.png')

print(f'\n--- MCQ-OSQ Delta Summary (Full Categories) ---')
display_df = cat_delta.sort_values('mean_delta', ascending=False).copy()
display_df['mean_delta'] = display_df['mean_delta'].map('{:+.1%}'.format)
display_df['std_delta'] = display_df['std_delta'].map('{:.1%}'.format)
print(display_df.to_string(index=False))


# ─── 6.5 MCQ Accuracy Heatmap (Top-Level) ────────────────────────────────────
print('\n--- 6.5 MCQ Accuracy Heatmap (Top-Level) ---')

mcq_top_accuracy = mcq_cat.groupby(['model', 'category_toplevel'])['is_correct'].mean().reset_index()
mcq_top_pivot = mcq_top_accuracy.pivot(index='model', columns='category_toplevel', values='is_correct')
mcq_top_pivot = mcq_top_pivot.reindex(index=model_order, columns=top_order)

fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(
    mcq_top_pivot,
    annot=True, fmt='.0%',
    cmap='RdYlGn', vmin=0.5, vmax=1.0,
    linewidths=0.5, linecolor='white',
    cbar_kws={'label': 'MCQ Accuracy', 'shrink': 0.8},
    annot_kws={'fontsize': 12},
    ax=ax
)
ax.set_title('MCQ Accuracy by Model and INCOSE Top-Level Group', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('INCOSE Top-Level Group', fontsize=12)
ax.set_ylabel('Model', fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right', fontsize=11)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / 'fig_mcq_accuracy_by_incose_toplevel.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_mcq_accuracy_by_incose_toplevel.png')


# ─── 6.6 OSQ Accuracy Heatmap (Top-Level) ────────────────────────────────────
print('\n--- 6.6 OSQ Accuracy Heatmap (Top-Level) ---')

osq_top_accuracy = osq_cat.groupby(['model', 'category_toplevel'])['osq_accuracy'].mean().reset_index()
osq_top_pivot = osq_top_accuracy.pivot(index='model', columns='category_toplevel', values='osq_accuracy')
osq_top_models = [m for m in model_order if m in osq_top_pivot.index]
osq_top_cats = [c for c in top_order if c in osq_top_pivot.columns]
osq_top_pivot = osq_top_pivot.reindex(index=osq_top_models, columns=osq_top_cats)

fig, ax = plt.subplots(figsize=(14, 12))
sns.heatmap(
    osq_top_pivot,
    annot=True, fmt='.0%',
    cmap='RdYlGn', vmin=0.5, vmax=1.0,
    linewidths=0.5, linecolor='white',
    cbar_kws={'label': 'OSQ Mean Score', 'shrink': 0.8},
    annot_kws={'fontsize': 12},
    ax=ax
)
ax.set_title('OSQ Mean Score by Model and INCOSE Top-Level Group', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('INCOSE Top-Level Group', fontsize=12)
ax.set_ylabel('Model', fontsize=12)
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right', fontsize=11)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=10)

plt.tight_layout()
plt.savefig(output_dir / 'fig_osq_accuracy_by_incose_toplevel.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_osq_accuracy_by_incose_toplevel.png')


# ─── 6.7 MCQ-OSQ Delta (Top-Level) ───────────────────────────────────────────
print('\n--- 6.7 MCQ-OSQ Delta (Top-Level) ---')

delta_top_by_model = aligned_cat.groupby(['model', 'category_toplevel'])['delta'].mean().reset_index()
delta_top_pivot = delta_top_by_model.pivot(index='model', columns='category_toplevel', values='delta')
delta_top_models = [m for m in model_order if m in delta_top_pivot.index]
delta_top_cats = [c for c in top_order if c in delta_top_pivot.columns]
delta_top_pivot = delta_top_pivot.reindex(index=delta_top_models, columns=delta_top_cats)

# Export CSV
delta_top_pivot.to_csv(output_dir / 'table_mcq_osq_delta_by_incose_toplevel.csv')
print(f'\u2705 Saved: table_mcq_osq_delta_by_incose_toplevel.csv')

# Export LaTeX
export_latex_table(
    delta_top_pivot.reset_index(),
    'table_mcq_osq_delta_by_incose_toplevel.tex',
    'MCQ--OSQ Accuracy Delta by INCOSE Top-Level Group (All Models)',
    'tab:mcq_osq_delta_toplevel'
)

# Diverging bar chart
top_delta = aligned_cat.groupby('category_toplevel')['delta'].agg(['mean', 'std', 'count']).reset_index()
top_delta.columns = ['category', 'mean_delta', 'std_delta', 'n']
top_delta = top_delta.sort_values('mean_delta', ascending=True)

colors = ['#2196F3' if d >= 0 else '#FF9800' for d in top_delta['mean_delta']]

fig, ax = plt.subplots(figsize=(12, max(6, len(top_delta) * 0.8)))
bars = ax.barh(top_delta['category'], top_delta['mean_delta'], color=colors, edgecolor='white', height=0.6)
ax.axvline(x=0, color='black', linewidth=0.8, linestyle='-')

for bar, val in zip(bars, top_delta['mean_delta']):
    x_pos = bar.get_width()
    ha = 'left' if val >= 0 else 'right'
    offset = 0.005 if val >= 0 else -0.005
    ax.text(x_pos + offset, bar.get_y() + bar.get_height()/2,
            f'{val:+.1%}', va='center', ha=ha, fontsize=11, fontweight='bold')

ax.set_xlabel('Mean MCQ \u2212 OSQ Delta (across models)', fontsize=12)
ax.set_ylabel('')
ax.set_title('MCQ vs. OSQ Accuracy Gap by INCOSE Top-Level Group\n(Positive = MCQ stronger, Negative = OSQ stronger)',
             fontsize=14, fontweight='bold')
ax.tick_params(axis='y', labelsize=11)
legend_elements = [
    Patch(facecolor='#2196F3', label='MCQ advantage'),
    Patch(facecolor='#FF9800', label='OSQ advantage')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

plt.tight_layout()
plt.savefig(output_dir / 'fig_mcq_osq_delta_by_incose_toplevel.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'\u2705 Saved: fig_mcq_osq_delta_by_incose_toplevel.png')

print(f'\n--- MCQ-OSQ Delta Summary (Top-Level Groups) ---')
display_top = top_delta.sort_values('mean_delta', ascending=False).copy()
display_top['mean_delta'] = display_top['mean_delta'].map('{:+.1%}'.format)
display_top['std_delta'] = display_top['std_delta'].map('{:.1%}'.format)
print(display_top.to_string(index=False))


# ─── Summary ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 80)
print('ANALYSIS COMPLETE')
print('=' * 80)
print('\nGenerated files:')
for f in sorted(output_dir.glob('*incose*')):
    size_kb = f.stat().st_size / 1024
    print(f'  {f.name:55s} ({size_kb:8.1f} KB)')

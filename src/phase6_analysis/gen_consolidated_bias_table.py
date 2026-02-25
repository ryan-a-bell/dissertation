"""
Generate the consolidated MCQ position bias robustness table
by merging chi-square, Friedman, and interpretation CSVs.

Outputs: table_position_bias_consolidated.csv and .tex
"""

import pandas as pd
from pathlib import Path

output_dir = Path(__file__).parent / 'output_v2'
manuscript_dir = Path(__file__).parent.parent.parent / 'manuscript' / 'overleaf' / 'figs' / 'ch4' / '4.6'
manuscript_dir.mkdir(parents=True, exist_ok=True)

# Load source tables
chi_sq = pd.read_csv(output_dir / 'table_chi_square_position_bias.csv')
fried  = pd.read_csv(output_dir / 'table_friedman_position_bias.csv')
interp = pd.read_csv(output_dir / 'table_position_bias_interpretation.csv')

# Merge
consolidated = chi_sq[['model', 'chi2_stat', 'p_value', 'cramers_v']].merge(
    fried[['model', 'friedman_stat', 'p_value', 'kendalls_w']],
    on='model', suffixes=('_chi2', '_friedman')
).merge(
    interp[['model', 'category']],
    on='model'
)

consolidated.columns = [
    'Model', 'Chi-Square', 'p (Chi-Square)', "Cramer's V",
    'Friedman', 'p (Friedman)', "Kendall's W", 'Classification'
]

# Sort by Cramer's V descending
consolidated = consolidated.sort_values("Cramer's V", ascending=False).reset_index(drop=True)

# Save CSV
consolidated.to_csv(output_dir / 'table_position_bias_consolidated.csv', index=False)
consolidated.to_csv(manuscript_dir / 'table_position_bias_consolidated.csv', index=False)
print('Saved: table_position_bias_consolidated.csv')

# Format for LaTeX
fmt = consolidated.copy()
fmt['Chi-Square']      = fmt['Chi-Square'].map(lambda v: f'{v:.2f}')
fmt['p (Chi-Square)']  = fmt['p (Chi-Square)'].map(
    lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}')
fmt["Cramer's V"]      = fmt["Cramer's V"].map(lambda v: f'{v:.4f}')
fmt['Friedman']        = fmt['Friedman'].map(lambda v: f'{v:.2f}')
fmt['p (Friedman)']    = fmt['p (Friedman)'].map(
    lambda v: f'{v:.4f}' if v >= 0.0001 else f'{v:.2e}')
fmt["Kendall's W"]     = fmt["Kendall's W"].map(lambda v: f'{v:.4f}')

# Escape underscores in model names for LaTeX
fmt['Model'] = fmt['Model'].str.replace('_', r'\_', regex=False)

latex_lines = []
latex_lines.append(r'\begin{tabular}{l r r r r r r l}')
latex_lines.append(r'\toprule')
latex_lines.append(
    r"\textbf{Model} & \textbf{$\chi^2$} & \textbf{$p_{\chi^2}$} & "
    r"\textbf{Cram\'er's $V$} & \textbf{Friedman} & "
    r"\textbf{$p_{\text{Friedman}}$} & \textbf{Kendall's $W$} & "
    r"\textbf{Classification} \\")
latex_lines.append(r'\midrule')

for _, row in fmt.iterrows():
    line = ' & '.join(str(row[c]) for c in fmt.columns) + r' \\'
    latex_lines.append(line)

latex_lines.append(r'\bottomrule')
latex_lines.append(r'\end{tabular}')

tex_str = '\n'.join(latex_lines)
for d in [output_dir, manuscript_dir]:
    with open(d / 'table_position_bias_consolidated.tex', 'w') as f:
        f.write(tex_str)
print('Saved: table_position_bias_consolidated.tex')

# Print summary
print(f'\nConsolidated table ({len(consolidated)} models):')
print(consolidated.to_string(index=False))
print(f'\nClassification breakdown:')
for cls, cnt in consolidated['Classification'].value_counts().items():
    print(f'  {cls}: {cnt}')

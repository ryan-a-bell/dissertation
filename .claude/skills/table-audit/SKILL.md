---
name: table-audit
description: Audit all tables in the dissertation manuscript. Checks for labels, captions, consistent formatting, and cross-references. Flags tables missing from text references, unreferenced tables, and caption style inconsistencies.
allowed-tools: Read, Grep, Glob
---

# Table Audit

Catalog and audit every table environment in the dissertation LaTeX source.

## File Locations

- **TeX source**: `manuscript/overleaf/*.tex` (chapters, appendices, front matter)
- **External table files**: `manuscript/overleaf/figs/**/*.tex` (generated LaTeX tables)
- **External table data**: `manuscript/overleaf/figs/**/*.csv`

## Procedure

### Step 1: Find all table environments

Scan all `.tex` files for table environments:
- `\begin{table}` ... `\end{table}`
- `\begin{table*}` ... `\end{table*}` (two-column)
- `\begin{longtable}` ... `\end{longtable}`
- `\begin{tabular}` ... `\end{tabular}` (may appear outside a table float)
- `\begin{sidewaystable}` ... `\end{sidewaystable}`

For each table environment, extract:
- **File** and **line number** (of `\begin`)
- **Label**: the `\label{...}` key (if present)
- **Caption**: the `\caption{...}` text (if present)
- **Position specifier**: `[h]`, `[t]`, `[b]`, `[H]`, `[htbp]`, etc.
- **Column spec**: the `{|l|c|r|}` argument to `\begin{tabular}`
- **Row count**: approximate number of `\\` within the tabular
- **External inputs**: any `\input{...}` or `\csvreader{...}` within the table

### Step 2: Find all table references

Scan all `.tex` files for references to tables:
- `\ref{tab:...}`, `\autoref{tab:...}`, `\cref{tab:...}`, `\Cref{tab:...}`
- `Table~\ref{...}` patterns (where the label may not have a `tab:` prefix)

### Step 3: Cross-reference

Match table labels to their references. Classify:

| Status | Meaning |
|--------|---------|
| Complete | Has label, caption, and at least one `\ref` in text |
| Unreferenced | Has label but no `\ref` found in any `.tex` file |
| Unlabeled | Table environment with `\caption` but no `\label` |
| Uncaptioned | Table environment with `\label` but no `\caption` |
| Bare | `\begin{tabular}` outside a `\begin{table}` float (no label or caption possible) |
| Undefined ref | `\ref{tab:...}` with no corresponding `\label` |

### Step 4: Style consistency checks

1. **Caption placement**: Are captions consistently above or below tables? (LaTeX convention: above for tables) Flag inconsistencies.
2. **Label prefix**: Do all table labels use the `tab:` prefix? Flag any that don't.
3. **Position specifiers**: Are they consistent across tables? Flag unusual ones.
4. **Column alignment**: Flag tables mixing `|` bordered and borderless styles (inconsistent visual style).
5. **Caption style**: Check for consistent capitalization (sentence case vs. title case). Flag mixed styles.
6. **Caption punctuation**: Do captions end with periods consistently?

### Step 5: External table files

Check `manuscript/overleaf/figs/` for `.tex` files containing `tabular` environments. These are often generated tables. Verify they are `\input{}`'d somewhere in the chapters.

## Output Format

```
## Table Audit Report

### Summary
- Total table environments: N
- Complete (label + caption + referenced): N
- Unreferenced: N
- Unlabeled: N
- Uncaptioned: N
- Bare tabular (no float): N
- Undefined references: N

### Per-Chapter Breakdown
| Chapter | Tables | Complete | Issues |
|---------|--------|----------|--------|
| chapter1.tex | N | N | N |
| ... | | | |

### Issues

#### Unreferenced Tables
- <file>:<line> `\label{<key>}` -- "<caption>" -- never referenced in text

#### Unlabeled Tables
- <file>:<line> -- caption: "<caption>" -- no \label{}

#### Uncaptioned Tables
- <file>:<line> `\label{<key>}` -- no \caption{}

#### Undefined References
- <file>:<line> `\ref{<key>}` -- no table with this label

#### Style Inconsistencies
- Caption placement: N above, N below (convention: above for tables)
- Label prefixes: N use `tab:`, N use other prefixes
- Caption capitalization: N sentence case, N title case
- Caption punctuation: N end with period, N do not

### External Table Files
| File | Input By | Has Label | Status |
|------|----------|-----------|--------|
| figs/ch4/results.tex | chapter4.tex:200 | tab:results | OK |
| figs/ch4/unused.tex | -- | -- | Orphaned |

### Full Inventory
| # | File:Line | Label | Caption (truncated) | Ref Count | Status |
|---|-----------|-------|---------------------|-----------|--------|
| 1 | chapter1.tex:89 | tab:overview | Overview of... | 3 | Complete |
| ... | | | | | |
```

Omit sections with zero results. Truncate captions to 50 characters in the inventory table.

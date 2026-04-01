---
name: figure-audit
description: Audit all figure environments in the dissertation manuscript. Checks for labels, captions, consistent formatting, cross-references, and image file existence. Companion to /table-audit and /figure-inventory.
allowed-tools: Read, Grep, Glob
---

# Figure Audit

Catalog and audit every figure environment in the dissertation LaTeX source, focusing on structural correctness, style consistency, and cross-references.

## File Locations

- **TeX source**: `manuscript/overleaf/*.tex` (chapters, appendices, front matter)
- **Image files**: `manuscript/overleaf/figs/` (recursive)

## Procedure

### Step 1: Find all figure environments

Scan all `.tex` files for figure environments:
- `\begin{figure}` ... `\end{figure}`
- `\begin{figure*}` ... `\end{figure*}` (two-column)
- `\begin{subfigure}` ... `\end{subfigure}`
- `\begin{sidewaysfigure}` ... `\end{sidewaysfigure}`
- `\begin{wrapfigure}` ... `\end{wrapfigure}`

For each figure environment, extract:
- **File** and **line number** (of `\begin`)
- **Label**: the `\label{...}` key (if present)
- **Caption**: the `\caption{...}` text (if present)
- **Position specifier**: `[h]`, `[t]`, `[b]`, `[H]`, `[htbp]`, etc.
- **Image path(s)**: all `\includegraphics{...}` paths within the environment
- **Width/scale**: the `[width=...]` or `[scale=...]` option on `\includegraphics`
- **Subfigure count**: number of `\begin{subfigure}` blocks (if any)

### Step 2: Find all figure references

Scan all `.tex` files for references to figures:
- `\ref{fig:...}`, `\autoref{fig:...}`, `\cref{fig:...}`, `\Cref{fig:...}`
- `Figure~\ref{...}` patterns (where the label may not have a `fig:` prefix)

### Step 3: Verify image files exist

For each `\includegraphics{<path>}`:
- Resolve the path relative to `manuscript/overleaf/`
- If no extension is given, check for `.png`, `.jpg`, `.jpeg`, `.pdf`, `.eps` variants
- Flag missing files

### Step 4: Cross-reference

Match figure labels to their references. Classify:

| Status | Meaning |
|--------|---------|
| Complete | Has label, caption, image exists, and at least one `\ref` in text |
| Unreferenced | Has label but no `\ref` found in any `.tex` file |
| Unlabeled | Figure environment with `\caption` but no `\label` |
| Uncaptioned | Figure environment with `\label` but no `\caption` |
| Missing image | `\includegraphics` path does not resolve to a file on disk |
| Undefined ref | `\ref{fig:...}` with no corresponding `\label` |

### Step 5: Style consistency checks

1. **Caption placement**: Are captions consistently below figures? (LaTeX convention: below for figures) Flag inconsistencies.
2. **Label prefix**: Do all figure labels use the `fig:` prefix? Flag any that don't.
3. **Position specifiers**: Are they consistent? Flag unusual ones or missing specifiers.
4. **Image widths**: Flag figures without explicit width/scale options (may render at unexpected sizes). Note the distribution of widths used (e.g., `\textwidth`, `\linewidth`, `\columnwidth`).
5. **Caption style**: Check for consistent capitalization (sentence case vs. title case). Flag mixed styles.
6. **Caption punctuation**: Do captions end with periods consistently?
7. **Subfigure consistency**: Within multi-subfigure figures, check that all subfigures have captions and labels.

### Step 6: Image quality flags

- Flag image files over 5 MB (may slow compilation or PDF generation)
- Flag `.jpg`/`.jpeg` images (lossy compression -- `.png` or `.pdf` preferred for publications)
- Flag images with very small dimensions (under 100x100 pixels, likely placeholder)

## Output Format

```
## Figure Audit Report

### Summary
- Total figure environments: N
- Total subfigures: N
- Complete (label + caption + image + referenced): N
- Unreferenced: N
- Unlabeled: N
- Uncaptioned: N
- Missing images: N
- Undefined references: N

### Per-Chapter Breakdown
| Chapter | Figures | Subfigures | Complete | Issues |
|---------|---------|------------|----------|--------|
| chapter1.tex | N | N | N | N |
| ... | | | | |

### Issues

#### Missing Images
- <file>:<line> `\includegraphics{<path>}` -- file not found

#### Unreferenced Figures
- <file>:<line> `\label{<key>}` -- "<caption>" -- never referenced in text

#### Unlabeled Figures
- <file>:<line> -- caption: "<caption>" -- no \label{}

#### Uncaptioned Figures
- <file>:<line> `\label{<key>}` -- no \caption{}

#### Undefined References
- <file>:<line> `\ref{<key>}` -- no figure with this label

#### Style Inconsistencies
- Caption placement: N above, N below (convention: below for figures)
- Label prefixes: N use `fig:`, N use other prefixes
- Caption capitalization: N sentence case, N title case
- Caption punctuation: N end with period, N do not
- Missing width spec: N figures have no explicit width/scale

#### Image Quality Flags
- Large files (>5 MB): <path> (<size>)
- JPEG images: <path> (consider .png or .pdf)

### Full Inventory
| # | File:Line | Label | Caption (truncated) | Image Path | Ref Count | Status |
|---|-----------|-------|---------------------|------------|-----------|--------|
| 1 | chapter1.tex:55 | fig:arch | Architecture of... | figs/ch1/arch.png | 4 | Complete |
| ... | | | | | | |
```

Omit sections with zero results. Truncate captions to 50 characters in the inventory table.

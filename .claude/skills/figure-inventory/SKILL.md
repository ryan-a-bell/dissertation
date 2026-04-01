---
name: figure-inventory
description: Catalog all dissertation figures. Cross-references image files on disk with includegraphics calls in the LaTeX source. Finds orphaned figures, missing files, and produces a full inventory table.
allowed-tools: Read, Grep, Glob, Bash(find *), Bash(wc *)
---

# Figure Inventory

Produce a complete inventory of all figures in the dissertation, cross-referencing files on disk with LaTeX references.

## File Locations

- **Figure files**: `manuscript/overleaf/figs/` (recursive, all subdirectories)
- **TeX source**: `manuscript/overleaf/*.tex`

## Procedure

### Step 1: Catalog files on disk

Recursively list all image files under `manuscript/overleaf/figs/` with extensions: `.png`, `.jpg`, `.jpeg`, `.pdf`, `.svg`, `.eps`, `.tex` (for standalone tikz/table figures).

Record the relative path from `manuscript/overleaf/` for each.

### Step 2: Extract LaTeX figure references

Scan all `.tex` files for:
- `\includegraphics[...]{<path>}` -- note that the path may omit the file extension
- `\input{<path>}` where the path points into `figs/`
- `\include{<path>}` where the path points into `figs/`

For each reference, extract:
- The file path referenced
- The `.tex` file and line number where it appears
- The enclosing `\begin{figure}` environment's `\label{...}` (if any)
- The enclosing `\caption{...}` text (if any)

### Step 3: Cross-reference

Match each `\includegraphics` path to a file on disk. Account for:
- Missing extensions (LaTeX often omits `.png`/`.pdf` -- check if any matching file exists)
- Relative paths from the document root (`manuscript/overleaf/`)

Classify each entry:

| Status | Meaning |
|--------|---------|
| Matched | File exists and is referenced in a `.tex` file |
| Orphaned | File exists on disk but is never referenced |
| Missing | Referenced in `.tex` but no file found on disk |
| Unlabeled | Referenced figure lacks a `\label{}` |
| Uncaptioned | Referenced figure lacks a `\caption{}` |

### Step 4: Generate chapter breakdown

Group referenced figures by chapter based on which `.tex` file contains the reference.

## Output Format

```
## Figure Inventory

### Summary
- Total image files on disk: N
- Total figure references in .tex: N
- Matched: N
- Orphaned (on disk, never referenced): N
- Missing (referenced, file not found): N
- Unlabeled figures: N
- Uncaptioned figures: N

### Per-Chapter Breakdown
| Chapter | Figures | Unlabeled | Uncaptioned |
|---------|---------|-----------|-------------|
| chapter1.tex | N | N | N |
| ... | | | |

### Missing Files (referenced but not found)
- <tex-file>:<line> -- `\includegraphics{<path>}` -- file not found

### Orphaned Files (on disk, never referenced)
- figs/<subdir>/<file>

### Full Inventory
| File | Chapter | Label | Caption (truncated) | Status |
|------|---------|-------|---------------------|--------|
| figs/ch1/overview.png | chapter1.tex:45 | fig:overview | System overview... | Matched |
| ... | | | | |
```

Omit sections with zero results. For the full inventory table, truncate captions to 50 characters.

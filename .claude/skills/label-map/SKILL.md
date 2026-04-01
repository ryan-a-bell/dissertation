---
name: label-map
description: Visualize the cross-reference graph across dissertation chapters. Maps all label definitions to their ref/autoref usage, showing inter-chapter dependencies and orphaned or undefined labels.
allowed-tools: Read, Grep, Glob
---

# Label Map

Parse all `\label{}` definitions and `\ref{}`/`\autoref{}` usage across the manuscript to produce a cross-reference dependency map.

## File Locations

- **TeX source**: `manuscript/overleaf/*.tex` (chapters, appendices, front matter)
- **Generated tables**: `manuscript/overleaf/figs/**/*.tex` (may contain labels)

## Procedure

### Step 1: Extract all label definitions

Scan all `.tex` files for `\label{<key>}`. Record:
- The label key
- The file and line number where it's defined
- The enclosing environment type (figure, table, equation, section, chapter, lstlisting, algorithm, or bare)
- The associated `\caption{...}` or `\section{...}` text (if applicable)

### Step 2: Extract all label references

Scan all `.tex` files for:
- `\ref{<key>}`
- `\autoref{<key>}`
- `\pageref{<key>}`
- `\nameref{<key>}`
- `\eqref{<key>}`
- `\cref{<key>}`, `\Cref{<key>}`

Record each: the key referenced, the file and line number, and the command used.

### Step 3: Build cross-reference map

For each label, determine:
- **Where defined**: which file
- **Where referenced**: which file(s) and how many times
- **Cross-chapter references**: references from a different file than the definition

### Step 4: Flag issues

1. **Undefined labels**: Keys referenced but never defined via `\label{}`
2. **Unreferenced labels**: Keys defined via `\label{}` but never referenced (excluding chapter/section labels, which may be intentionally unreferenced)
3. **Single-file labels**: Labels only referenced within the same file (informational)
4. **Heavily cross-referenced labels**: Labels referenced from 3+ different files (potential fragility)

### Step 5: Dependency summary

Produce a chapter-to-chapter dependency matrix showing how many cross-references flow between each pair.

## Output Format

```
## Label Cross-Reference Map

### Summary
- Total labels defined: N
- Total references: N
- Cross-chapter references: N
- Undefined labels: N
- Unreferenced labels: N

### Chapter Dependency Matrix
References FROM (row) TO (column):
|          | ch1 | ch2 | ch3 | ch4 | ch5 | ch6 | app1 | app2 | app3 |
|----------|-----|-----|-----|-----|-----|-----|------|------|------|
| ch1      | 5   | 0   | 1   | 0   | 0   | 0   | 0    | 0    | 0    |
| ch2      | 2   | 8   | 0   | 0   | 0   | 0   | 0    | 0    | 0    |
| ...      |     |     |     |     |     |     |      |      |      |

### Undefined Labels
- `\ref{<key>}` in <file>:<line> -- no `\label{<key>}` found

### Unreferenced Labels (non-section)
- `\label{<key>}` in <file>:<line> (<type>) -- never referenced

### Cross-Chapter References
| Label | Defined In | Type | Referenced From | Count |
|-------|-----------|------|-----------------|-------|
| fig:overview | chapter1.tex:45 | figure | chapter3.tex, chapter5.tex | 3 |
| ... | | | | |

### All Labels
| Label | File:Line | Type | Ref Count | Files Referencing |
|-------|-----------|------|-----------|-------------------|
| fig:overview | chapter1.tex:45 | figure | 5 | ch1, ch3, ch5 |
| ... | | | | |
```

Omit sections with zero results. Sort the full label table by file order.

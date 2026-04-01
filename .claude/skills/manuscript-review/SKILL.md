---
name: manuscript-review
description: Review LaTeX manuscript changes for the dissertation. Diffs chapter files, flags LaTeX issues (orphaned refs, missing labels, overfull hboxes), and summarizes changes in plain language. Use when reviewing or auditing manuscript edits.
argument-hint: "[ref-to-diff-against]"
allowed-tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *), Bash(git show *)
---

# Manuscript Review

Review changes to the dissertation LaTeX source in `manuscript/overleaf/` and produce a structured review summary.

## Arguments

- `$ARGUMENTS` (optional): A git ref to diff against (e.g., `HEAD~3`, `main`, a commit SHA). Defaults to `HEAD~1` if omitted.

## Manuscript Structure

| File | Content |
|------|---------|
| `manuscript/overleaf/main.tex` | Root document, front matter config, chapter includes |
| `manuscript/overleaf/front_matter.tex` | Title, abstract, acknowledgments |
| `manuscript/overleaf/chapter1.tex` - `chapter6.tex` | Dissertation chapters |
| `manuscript/overleaf/appendix1.tex` - `appendix3.tex` | Appendices |
| `manuscript/overleaf/references.bib` | Primary bibliography |
| `manuscript/overleaf/acronyms.tex` | Acronym definitions |
| `manuscript/sources/*.bib` | Topic-organized bibliography files |

## Review Procedure

### Step 1: Identify changes

Run a diff of `manuscript/overleaf/` against the provided ref (or `HEAD~1`):

```
git diff <ref> -- manuscript/overleaf/
```

If there are no changes, report that and stop.

### Step 2: Summarize changes in plain language

For each changed file, describe:
- **What** was added, removed, or modified
- **Why** it matters (e.g., new section, revised argument, added citation)
- Group related changes across files (e.g., a new figure added in `figs/` and referenced in a chapter)

### Step 3: LaTeX quality checks

Scan all modified `.tex` files for these issues:

1. **Orphaned references**: `\ref{...}` or `\autoref{...}` targets that have no corresponding `\label{...}` in any `.tex` file under `manuscript/overleaf/`
2. **Orphaned citations**: `\cite{...}` keys not found in any `.bib` file under `manuscript/overleaf/` or `manuscript/sources/`
3. **Missing labels**: Figures, tables, equations, or sections that lack `\label{}`
4. **Duplicate labels**: The same `\label{...}` key used in multiple places
5. **Empty sections**: `\section{...}` or `\subsection{...}` immediately followed by another section command with no content between them
6. **TODO/FIXME markers**: Any `TODO`, `FIXME`, `XXX`, or `PLACEHOLDER` strings left in the text
7. **Acronym consistency**: Acronyms used via `\ac{}` or `\gls{}` that aren't defined in `acronyms.tex` or `acronym-list.tex`

### Step 4: Cross-reference checks

- Verify that any new `\includegraphics{...}` paths point to files that exist in `manuscript/overleaf/figs/`
- Verify that any new `\input{...}` or `\include{...}` paths resolve to existing files
- Check that new bibliography entries in `.bib` files have all required fields for their entry type

### Step 5: Terminology and glossary alignment

Cross-reference key terms against `docs/glossary.md` for consistent usage across the dissertation and the documentation site.

## Output Format

Present the review as:

```
## Manuscript Review: <ref-range>

### Summary of Changes
- <plain-language summary per file, grouped logically>

### Issues Found
#### Critical (will cause compilation errors)
- <orphaned refs, missing files, etc.>

#### Warnings (should be addressed)
- <duplicate labels, missing labels, empty sections, etc.>

#### Notes (informational)
- <TODOs found, terminology suggestions, etc.>

### Statistics
- Files changed: N
- Lines added: N
- Lines removed: N
- New citations: N
- New figures: N
```

If no issues are found in a category, omit that category.

---
name: slide-outline
description: Generate a defense presentation outline from dissertation chapters. Extracts section hierarchy, key findings, and figure references to produce slide-ready bullet points.
argument-hint: "[chapter-numbers...]"
allowed-tools: Read, Grep, Glob
---

# Slide Outline Generator

Generate a structured presentation outline from dissertation chapter content, suitable for building defense slides.

## Arguments

- `$ARGUMENTS` (optional): Chapter numbers to include, space-separated (e.g., `1 3 4`). Defaults to all chapters (1-6) if omitted.

## File Locations

- **Chapters**: `manuscript/overleaf/chapter1.tex` through `chapter6.tex`
- **Figures**: `manuscript/overleaf/figs/`
- **Existing slides**: `manuscript/presentation/` (reference for style/format if present)
- **Key findings**: `docs/key-findings.md` (supplement with documented findings)

## Procedure

### Step 1: Parse chapter structure

For each requested chapter, extract the full section hierarchy:
- `\chapter{...}` -- slide group header
- `\section{...}` -- individual slide candidate
- `\subsection{...}` -- bullet points within a slide

### Step 2: Extract key content

For each section, identify:
- **Thesis statements**: Opening sentences of sections (first 1-2 sentences after `\section`)
- **Key findings**: Sentences containing signal phrases like "results show", "we find", "demonstrates", "significant", "outperforms", "suggests that"
- **Statistics**: Numbers, percentages, p-values, and quantitative claims
- **Figures and tables**: All `\ref{fig:...}` and `\ref{tab:...}` references, mapped to their captions and file paths -- these become visual slide candidates

### Step 3: Cross-reference key-findings.md

Read `docs/key-findings.md` and match documented findings to chapter sections. Include any findings that aren't already captured in the section extraction.

### Step 4: Build outline

Structure the outline for a defense presentation:

```
## Chapter N: <Title>

### Slide: <Section Title>
- <Key point 1>
- <Key point 2>
- Figure: <fig-label> -- <caption> (figs/<path>)
- Data: <statistic or quantitative claim>

### Slide: <Section Title>
- ...
```

### Step 5: Suggest presentation flow

After the per-chapter outline, add:
- **Recommended slide count**: Based on ~2 minutes per slide for a 45-60 minute defense
- **Suggested emphasis**: Which sections warrant multiple slides vs. which can be compressed
- **Visual opportunities**: Figures/tables that would make strong standalone slides
- **Transition suggestions**: How to connect chapters narratively

## Output Format

```
## Defense Presentation Outline

### Overview
- Chapters covered: N
- Total sections: N
- Figures available: N
- Recommended slide count: N (for ~50 min presentation)

---

## Chapter 1: <Title>

### Slide: <Section Title>
- <bullet>
- <bullet>
- [Figure: <label> -- <caption>]

...

---

## Presentation Flow Recommendations
- <emphasis suggestions>
- <transition notes>
- <visual slide candidates>
```

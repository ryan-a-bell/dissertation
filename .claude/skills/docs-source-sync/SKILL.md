---
name: docs-source-sync
description: Check documentation site content against the dissertation manuscript for consistency. Flags discrepancies in findings, terminology, statistics, and glossary definitions between docs/ and manuscript/overleaf/.
allowed-tools: Read, Grep, Glob
---

# Documentation-Source Sync

Compare content between the MkDocs documentation site and the dissertation LaTeX manuscript to find discrepancies.

## File Locations

### Documentation Site
- `docs/key-findings.md` -- documented research findings
- `docs/glossary.md` -- term definitions
- `docs/index.md` -- landing page (may contain summary claims)
- `docs/analysis-gallery.md` -- analysis descriptions and figure references
- `docs/metaeval.md` -- metaeval package documentation

### Manuscript Source
- `manuscript/overleaf/chapter1.tex` - `chapter6.tex` -- chapter content
- `manuscript/overleaf/front_matter.tex` -- abstract, executive summary
- `manuscript/overleaf/acronyms.tex` -- acronym definitions
- `manuscript/overleaf/references.bib` -- bibliography

## Sync Procedure

### Step 1: Key findings comparison

Read `docs/key-findings.md` and extract each documented finding (claims, statistics, conclusions).

For each finding, search the manuscript chapters for the corresponding claim. Flag:
- **Contradictions**: A finding in docs states X but the manuscript states Y
- **Missing from manuscript**: A finding documented on the site but not present in any chapter
- **Missing from docs**: A significant finding in the manuscript (near signal phrases like "key finding", "result", "conclude") not reflected on the docs site
- **Stale statistics**: Numeric values (percentages, counts, p-values) that differ between docs and manuscript

### Step 2: Glossary consistency

Read `docs/glossary.md` and extract all term definitions.

Compare against:
- `manuscript/overleaf/acronyms.tex` -- do acronym expansions match?
- Chapter text -- are terms defined consistently where they first appear?

Flag:
- Terms defined differently in glossary vs. manuscript
- Terms in glossary not appearing in the manuscript at all
- Key terms defined in the manuscript but missing from the glossary

### Step 3: Statistical consistency

Extract all numeric claims from both sources:
- Pattern: numbers followed by `%`, `p <`, `p =`, `n =`, counts like "1,144 questions"
- Compare identical metrics across sources for value mismatches

### Step 4: Structural consistency

Check that:
- Chapter titles in the docs navigation (`.pages.yml`, `index.md`) match actual `\chapter{}` titles in the manuscript
- The research phase descriptions on the docs site align with what the code in `src/` actually does
- The timeline in `docs/assets/timeline.puml` reflects the current chapter/phase structure

### Step 5: Freshness check

For each docs file, compare its last-modified date against the manuscript files it references. Flag docs pages that may be stale (manuscript updated significantly more recently).

## Output Format

```
## Documentation-Source Sync Report

### Summary
- Docs files checked: N
- Manuscript files checked: N
- Discrepancies found: N

### Contradictions
- <docs-file>: "<docs claim>"
  vs. <tex-file>:<line>: "<manuscript claim>"

### Stale Statistics
- <docs-file>: says "<value>" but <tex-file>:<line> says "<value>"

### Missing from Documentation
- <tex-file>:<line>: "<finding>" -- not in docs

### Missing from Manuscript
- <docs-file>: "<claim>" -- not found in any chapter

### Glossary Mismatches
- "<term>": docs says "<def1>", manuscript says "<def2>"

### Glossary Gaps
- In docs but not manuscript: <term>, <term>
- In manuscript but not docs: <term>, <term>

### Freshness
| Docs File | Last Modified | Related Manuscript File | Last Modified | Status |
|-----------|---------------|------------------------|---------------|--------|
| key-findings.md | <date> | chapter5.tex | <date> | Stale? |
```

Omit sections with zero results.

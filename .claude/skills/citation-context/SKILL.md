---
name: citation-context
description: Show how each bibliography source is cited in context. Extracts the surrounding sentence for each citation, helping review whether sources are used appropriately.
argument-hint: "[bib-key or 'all']"
allowed-tools: Read, Grep, Glob
---

# Citation Context

For a given bibliography key (or all keys), extract the surrounding text from the `.tex` source where it is cited.

## Arguments

- `$ARGUMENTS` (optional): A specific bib key to look up (e.g., `zheng2023judging`), or `all` to process every cited key. Defaults to `all` if omitted.

## File Locations

- **TeX source**: `manuscript/overleaf/*.tex`
- **Bibliography**: `manuscript/overleaf/references.bib`, `manuscript/sources/*.bib`

## Procedure

### Step 1: Identify target keys

If a specific key is provided, verify it exists in a `.bib` file. If `all`, collect every key cited in any `.tex` file.

Citation commands to match:
- `\cite{<key>}`, `\cite{key1,key2,...}`
- `\citep{<key>}`, `\citet{<key>}`
- `\citeauthor{<key>}`, `\citeyear{<key>}`
- `\parencite{<key>}`, `\textcite{<key>}`
- `\nocite{<key>}`

Split multi-key citations (e.g., `\cite{a,b,c}`) into individual keys.

### Step 2: Extract citation context

For each citation occurrence, extract:
- The **full sentence** containing the citation (from the previous period/newline to the next period/newline)
- The **file** and **line number**
- The **citation command** used (cite, citep, citet, etc.)
- The **chapter** the citation appears in

If the sentence spans multiple lines, join them.

### Step 3: Retrieve bibliography entry

For each key, read the corresponding `.bib` entry and extract:
- Author(s)
- Title
- Year
- Venue (journal, booktitle, or publisher)

### Step 4: Organize by key

Group all citation contexts under each bibliography key.

### Step 5: Analysis (for `all` mode)

When processing all keys, also compute:
- **Most cited**: Top 10 most-referenced sources by citation count
- **Single-use citations**: Sources cited exactly once
- **Citation clustering**: Sources that always appear together in multi-key citations
- **Chapter distribution**: Which chapters cite which sources most heavily
- **Uncited entries**: Bib entries with zero citations (cross-reference with `/bib-audit`)

## Output Format

### Single key mode

```
## Citation Context: <key>

### Source
**<Author> (<Year>)**. <Title>. *<Venue>*.

### Usage (N occurrences)

1. **chapter2.tex:145** (`\citep`)
   > "Previous work has shown that LLM-based evaluation can match human judgment in many scenarios \citep{<key>}."

2. **chapter4.tex:302** (`\citet`)
   > "\citet{<key>} demonstrated that position bias significantly affects MCQ accuracy."

...
```

### All keys mode

```
## Citation Context Report

### Summary
- Total unique sources cited: N
- Total citation occurrences: N
- Sources in .bib but never cited: N

### Most Cited Sources
| # | Key | Author (Year) | Citations | Chapters |
|---|-----|---------------|-----------|----------|
| 1 | <key> | <Author> (<Year>) | 15 | 1,2,3,4,5 |
| ... | | | | |

### Single-Use Citations
- <key> (<Author>, <Year>) -- cited once in <chapter>:<line>

### Citation Contexts by Key

#### <key1> -- <Author> (<Year>): <Title>
1. **chapter2.tex:145** (`\citep`): "<sentence>"
2. ...

#### <key2> -- ...
...
```

When in `all` mode, limit the per-key context listings to the first 5 occurrences for sources cited more than 5 times, with a note indicating the total count.

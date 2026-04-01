---
name: missing-refs
description: Find claims in the dissertation that lack supporting citations. Scans for assertion patterns like "studies show" or "research indicates" without a nearby cite command. Use to strengthen academic rigor before submission.
argument-hint: "[chapter-numbers...]"
allowed-tools: Read, Grep, Glob
---

# Missing References

Scan dissertation chapters for claims, assertions, and factual statements that appear to need a citation but lack one.

## Arguments

- `$ARGUMENTS` (optional): Chapter numbers to scan, space-separated (e.g., `1 3 4`). Defaults to all chapters (1-6) if omitted.

## File Locations

- **TeX source**: `manuscript/overleaf/chapter1.tex` through `chapter6.tex`
- **Front matter**: `manuscript/overleaf/front_matter.tex` (abstract, exec summary)

## Procedure

### Step 1: Load chapter text

For each target chapter, read the `.tex` file. Process line by line, tracking line numbers.

### Step 2: Identify assertion patterns

Search for sentences matching these categories of unsupported claims. A sentence is the text between two sentence-ending boundaries (period, start of paragraph, or `\\`).

#### Category A: Attribution to external work (high confidence)

Phrases that explicitly attribute a claim to outside research and almost always require a citation:

- "studies show", "studies have shown", "studies suggest", "studies indicate"
- "research shows", "research has shown", "research suggests", "research indicates", "research demonstrates"
- "literature suggests", "the literature shows", "in the literature"
- "has been shown", "has been demonstrated", "has been established", "has been proven", "has been observed", "has been reported", "has been noted", "has been found"
- "it is well known", "it is well established", "it is widely accepted", "it is commonly understood", "it is generally agreed"
- "according to", "as shown by", "as demonstrated by", "as noted by", "as reported by", "as described by", "as discussed by", "as proposed by", "as established by"
- "previous work", "prior work", "prior research", "previous research", "previous studies", "prior studies", "earlier work", "earlier studies"
- "existing approaches", "existing methods", "existing work", "existing research", "existing literature"
- "recently proposed", "recently introduced", "recently developed", "recently demonstrated"

#### Category B: Factual claims (medium confidence)

Statements presenting facts or statistics that likely need a source. Flag these only if no `\cite` appears within the same sentence or the immediately following/preceding sentence:

- Quantitative claims: "X% of", "N million", "N billion", numbers presented as established facts (not the author's own results)
- Comparative claims: "outperforms", "surpasses", "exceeds", "is superior to", "is inferior to", "lags behind"
- Temporal claims: "traditionally", "historically", "conventionally", "in recent years"
- Definitional claims: "is defined as", "refers to", "is known as", "is characterized by"

#### Category C: Hedged assertions (lower confidence)

Softer claims that may or may not need citations depending on context. Flag these with lower severity:

- "can be", "may be", "might be" followed by a claim about capability or behavior
- "tends to", "is likely to", "is expected to"
- "is considered", "is regarded as", "is seen as"
- "is important", "is critical", "is essential", "is necessary", "plays a key role", "plays a crucial role"

### Step 3: Check for nearby citations

For each flagged sentence, check whether a `\cite`, `\citep`, `\citet`, `\citeauthor`, `\parencite`, or `\textcite` command appears:
- Within the same sentence
- In the immediately preceding sentence (same paragraph)
- In the immediately following sentence (same paragraph)

If a citation is found nearby, do NOT flag the sentence. Only report sentences where no citation is within this window.

### Step 4: Exclude false positives

Do NOT flag sentences that:
- Are inside a `\caption{...}` (captions may summarize without re-citing)
- Are inside `\begin{abstract}` ... `\end{abstract}` (abstracts conventionally omit citations)
- Refer to the author's own work using first person ("we show", "we demonstrate", "our results show", "this dissertation")
- Are inside comments (`%` prefixed lines)
- Contain "in this chapter", "in this section", "in Chapter", "in Section" (self-references)

### Step 5: Severity classification

| Severity | Category | Meaning |
|----------|----------|---------|
| High | A | Explicitly attributes to external research -- almost certainly needs a cite |
| Medium | B | Factual/quantitative claim -- likely needs a source |
| Low | C | Hedged assertion -- may need a cite depending on context |

## Output Format

```
## Missing References Report

### Summary
- Chapters scanned: N
- Potential missing citations found: N
  - High severity: N
  - Medium severity: N
  - Low severity: N

### High Severity (attribution without citation)

#### chapter1.tex
- **Line 45**: "Previous research has shown that LLMs struggle with domain-specific reasoning."
  Pattern: "previous research has shown"

- **Line 112**: "It is well established that MCQ format introduces position bias."
  Pattern: "it is well established"

#### chapter2.tex
- ...

### Medium Severity (unsupported factual claims)

#### chapter1.tex
- **Line 78**: "Traditionally, systems engineering assessments relied on manual expert review."
  Pattern: "traditionally"

- ...

### Low Severity (hedged assertions)

#### chapter3.tex
- **Line 201**: "LLM-based evaluation is considered a cost-effective alternative."
  Pattern: "is considered"

- ...
```

Omit severity sections with zero results. Within each section, group by chapter file.

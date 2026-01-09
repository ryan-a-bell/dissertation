
# Dissertation Chapter Structural Review Prompt (Fixed)

You are reviewing a dissertation chapter draft provided as LaTeX (I will paste the full `.tex` contents).

---

## GOAL

Evaluate the **QUALITY of the chapter’s STRUCTURE** (sections / subsections / subsubsections) and how well the existing written content supports that structure. Then quantify coverage (**citations + words**). If the outline’s narrative quality is below threshold, propose a refactored outline using **only the content that already exists in the draft**.

---

## TASKS

### 1) EXTRACT OUTLINE

- Extract the hierarchy based on:
  - `\section{}`
  - `\subsection{}`
  - `\subsubsection{}`
- Preserve numbering and titles **exactly as written**.
- Note any **“stub” items** (empty or near-empty).

---

### 2) QUANTITATIVE COVERAGE

#### A) CITATION COUNTS PER SECTION

- Count **all citation commands that occur anywhere within the textual span of each section/subsection/subsubsection**, including when citations are:
  - Interleaved with figures, tables, or floats  
  - Separated by long quoted text or explanatory paragraphs  
  - Embedded after informal bullet-style prose (not using `itemize`)  
  - Placed before *or after* figures or figure captions  

- Citation commands to count:
  - `\cite{...}`, `\citet{...}`, `\citep{...}`, `\citeauthor{...}`, `\citeyear{...}`
  - `\autocite{...}`, `\parencite{...}`, `\textcite{...}`, and variants

- If multiple keys appear in one command (e.g., `\cite{a,b,c}`), count **each key as 1**.

- **IMPORTANT PARSING RULE**
  - The presence of `\begin{figure}`, `\end{figure}`, tables, or other environments  
  - **MUST NOT terminate citation counting** for the enclosing section/subsection/subsubsection.
  - Continue counting citations until the **next structural heading** of the same or higher level.

- Produce totals at:
  - Section level (2.0, 3.0, etc.)
  - Subsection level (2.1, 2.2, etc.)
  - Subsubsection level where present (2.5.1, etc.)

- If a part is a stub/empty, still list it with **0 citations**.

---

#### B) WORD COUNTS PER SECTION

- Estimate words per section/subsection/subsubsection by counting **readable prose words**.

- Exclude:
  - LaTeX commands
  - labels and refs
  - citation commands
  - figure/table environments
  - math
  - code listings
  - bibliography blocks

- Include:
  - Normal paragraphs
  - Explanatory prose
  - Bullet-style text even if not inside an `itemize` environment

- If exact counting is not possible, provide best-effort approximations and mark as **“approx.”**

---

### 3) OUTLINE NARRATIVE SCORE (STRUCTURE-LEVEL SCORING)

- Score the outline’s narrative effectiveness on a **0–10 scale**, based strictly on content that is actually present.

- Criteria (score each 0–2; total 0–10):
  1. Logical progression / funnel toward the chapter’s purpose
  2. Bridge quality between major sections (no abrupt jumps)
  3. Role clarity: each section has a distinct job (low redundancy)
  4. Balance: no single subsection dominates without structural justification
  5. Content support: headings match what’s written (few stubs/mismatches)

- Provide:
  - Overall score /10
  - Subscores for each criterion
  - 5–10 sentences justifying the score with references to **exact section numbers/titles**

---

### 4) NARRATIVE DIAGNOSIS

- In 5–10 sentences: *“What narrative does the current outline tell?”*
- Identify where the narrative is strongest and where it becomes muddled.

---

### 5) WEAKNESS DIAGNOSIS

- Where is the chapter weak and why:
  - structure
  - missing bridges
  - unsupported claims
  - imbalance of citations
  - overlong subsections
  - empty stubs

- Identify **big citation gaps**:
  - Only subsections with **0–1 citations after full parsing**
  - Do **not** flag sections as under-cited if citations are present but separated by figures or long prose

- Identify **coverage imbalance**:
  - Subsections with extremely high citation density or word count relative to their structural role

---

### 6) CONDITIONAL REFACTOR: PROPOSE A NEW OUTLINE IF SCORE < 7/10

If **overall narrative score < 7/10**:

- Propose a revised outline (sections/subsections/subsubsections) that improves the narrative and fixes redundancy.
- Constraints:
  - You may only reorganize and rename based on content that already exists in the draft.
  - **Do NOT invent new major topical content.**
  - You may add placeholder headings **only** to group existing paragraphs already present  
    (label them `[REFACTOR GROUPING]`).

- Provide:
  - A mapping from **old → new**
    - For each new subsection, list which old subsections or paragraph topics move into it
  - 5–10 bullet **refactor actions**

---

## OUTPUT FORMAT (MATCH EXACTLY)

A) High-level verdict (2–4 sentences)

B) Outline flow assessment  
- Flow strengths (bullets)  
- Flow breaks / missing bridges (bullets)  
- Overlap / redundancy hotspots (bullets)

C) Coverage table (hierarchical)  
- For each section/subsection/subsubsection:
  - Word count (approx ok)
  - Citation count
  - Coverage note

D) Outline narrative score  
- Overall score /10  
- Subscores  
- Justification (5–10 sentences)

E) Narrative: what story the outline tells (5–10 sentences)

F) Where it’s weak  
- Structural weaknesses  
- Evidence/citation weaknesses  
- What to fix first (top 5, ranked)

G) Big citation gaps list  
- Section number + title + reason citations are needed

H) (Conditional) Proposed refactored outline (ONLY if score < 7/10)  
- New outline  
- Old → new mapping  
- Refactor actions

---

## IMPORTANT CONSTRAINTS

- Do **NOT** rewrite the chapter.
- Do **NOT** invent citations.
- Be concrete: refer to exact section numbers/titles.
- Call out TODOs/placeholders as weaknesses.
- Prefer minimal disruption: improve flow while preserving intent.

---

## INPUT

[PASTE FULL LATEX CHAPTER HERE]

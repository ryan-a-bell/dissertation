You are reviewing a dissertation chapter draft provided as LaTeX (I will paste the full .tex contents). 

GOAL
Evaluate the QUALITY of the chapter’s STRUCTURE (sections/subsections/subsubsections) and how well the existing written content supports that structure. Then quantify coverage (citations + words). If the outline’s narrative quality is below threshold, propose a refactored outline using only the content that already exists in the draft.

TASKS

1) EXTRACT OUTLINE
   - Extract the hierarchy based on:
     \section{}, \subsection{}, \subsubsection{}
   - Preserve numbering and titles exactly as written.
   - Also note any “stub” items (empty or near-empty).

2) QUANTITATIVE COVERAGE
   A) CITATION COUNTS PER SECTION
      - Count all citation commands inside each section/subsection/subsubsection:
        \cite{...}, \citet{...}, \citep{...}, \citeauthor{...}, \citeyear{...},
        \autocite{...}, \parencite{...}, \textcite{...}, and variants.
      - If multiple keys appear in one command (e.g., \cite{a,b,c}), count each key as 1.
      - Produce totals at:
        i) section level (2.0, 3.0, etc.)
        ii) subsection level (2.1, 2.2, etc.)
        iii) subsubsection level where present (2.5.1, etc.)
      - If a part is a stub/empty, still list it with 0 citations.

   B) WORD COUNTS PER SECTION
      - Estimate words per section/subsection/subsubsection by counting “readable prose words.”
      - Exclude: LaTeX commands, labels, refs, cite commands, figure environments, tables, math, code listings, and bibliography blocks.
      - Include: normal paragraphs and list item text (bullets) that constitute prose.
      - If exact counting is not possible, provide best-effort approximations and mark as “approx.”

3) OUTLINE NARRATIVE SCORE (STRUCTURE-LEVEL SCORING)
   - Score the outline’s narrative effectiveness on a 0–10 scale based on the content that is actually present.
   - Use these criteria (score each 0–2; total 0–10):
     (i) Logical progression / funnel toward the chapter’s purpose
     (ii) Bridge quality between major sections (no abrupt jumps)
     (iii) Role clarity: each section has a distinct job (low redundancy)
     (iv) Balance: no single subsection dominates without structural justification
     (v) Content support: headings match what’s written (few stubs/mismatches)
   - Provide:
     * Overall score /10
     * Subscores for each criterion
     * 5–10 sentences justifying the score with references to specific section numbers/titles.

4) NARRATIVE DIAGNOSIS
   - In 5–10 sentences: “What narrative does the current outline tell?”
   - Identify where the narrative is strongest and where it becomes muddled.

5) WEAKNESS DIAGNOSIS
   - Where is the chapter weak and why (structure, missing bridges, unsupported claims, imbalance of citations, overlong subsections, empty stubs)?
   - Identify “big citation gaps”: subsections that do important argumentative work but have 0–1 citations.
   - Identify “coverage imbalance”: subsections with extremely high citation density or word count relative to their structural role.

6) CONDITIONAL REFACTOR: PROPOSE A NEW OUTLINE IF SCORE < 7/10
   IF (Overall narrative score < 7/10):
     - Propose a revised outline (sections/subsections/subsubsections) that improves the narrative and fixes redundancy.
     - IMPORTANT: You may only reorganize and rename based on content that already exists in the draft.
       * Do NOT invent new major topical content.
       * You may add placeholder headings ONLY when needed to group existing paragraphs already present (label them “[REFACTOR GROUPING]”).
     - Provide a “mapping” from old → new:
       * For each new subsection, list which old subsections/paragraph topics move into it.
     - Provide 5–10 bullet “refactor actions” (e.g., “Split 2.1 into 2.1 and 2.2; move contamination under dataset lifecycle; move tools into its own section; promote SE-specific gap discussion to the end of Section 2 to funnel into SysEngBench”).

OUTPUT FORMAT (match exactly)

A) High-level verdict (2–4 sentences)

B) Outline flow assessment
   - Flow strengths (bullets)
   - Flow breaks / missing bridges (bullets)
   - Overlap/redundancy hotspots (bullets)

C) Coverage table (hierarchical)
   - For each section/subsection/subsubsection:
     * Word count (approx ok)
     * Citation count
     * Coverage note (e.g., “bridge section thin,” “survey-heavy,” “stub/empty”)

D) Outline narrative score
   - Overall score /10
   - Subscores (each criterion 0–2)
   - Justification (5–10 sentences)

E) Narrative: what story the outline tells (5–10 sentences)

F) Where it’s weak (bullets)
   - Structural weaknesses
   - Evidence/citation weaknesses
   - What to fix first (top 5, ranked)

G) Big citation gaps list (bullets)
   - For each gap: (section number + title) + 1 sentence why it needs citations.

H) (Conditional) Proposed refactored outline (ONLY if score < 7/10)
   - New outline (numbered)
   - Old → new mapping table (bulleted is fine)
   - Refactor actions (bullets)

IMPORTANT CONSTRAINTS
- Do NOT rewrite the chapter.
- Do NOT invent citations.
- Be concrete: refer to exact section numbers/titles.
- If the LaTeX contains TODOs/placeholders, call them out and treat them as weaknesses.
- Prefer minimal disruption: improve flow while preserving intent.

INPUT
[PASTE FULL LATEX CHAPTER HERE]

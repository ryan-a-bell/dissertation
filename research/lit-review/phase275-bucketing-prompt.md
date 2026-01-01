You are assisting with a literature review draft in LaTeX. The .tex file currently contains raw “evidence ingestion” notes: citation keys, pasted quotes/snippets, and rough placement into sections.

GOAL
Organize and bucket concepts across the entire .tex so that each outline section becomes:
- a set of coherent THEMATIC BUCKETS (subtopics),
- each bucket contains the best evidence items (quote/snippet + citation key),
- duplicates and misfiled items are flagged,
- cross-cutting buckets are tagged for reuse in multiple sections.

IMPORTANT RULES
- Do NOT rewrite my paper yet. This step is organization only.
- Do NOT paraphrase quoted text; keep evidence items verbatim as they appear in my .tex.
- Do NOT fabricate citations, claims, or quotes.
- If an evidence snippet lacks a citation key, flag it as “NEEDS CITATION KEY”.
- Keep output structured and directly actionable.

INPUTS
A) My outline bins (use these exact names):
[PASTE OUTLINE HERE — same bins as earlier]

B) My LaTeX file content:
----------------
[PASTE .TEX HERE]
----------------

TASKS
1) Parse the .tex and identify “evidence items”. An evidence item is one of:
   - a direct quote (in quotes or blockquote-like formatting),
   - a short factual snippet tied to a citation key,
   - a noted limitation/result/method tied to a citation key.

2) For each top-level outline bin, create 3–10 THEMATIC BUCKETS.
   - Each bucket should have a short label (3–8 words).
   - Buckets should be mutually distinct where possible.

3) Assign each evidence item to:
   - a primary bucket, and optionally
   - 1–2 secondary buckets if it is truly cross-cutting.

4) Produce a “CLEANUP” list:
   - duplicates (same idea repeated with same citation),
   - conflicts/tensions (two papers disagree),
   - misfiled items (clearly placed in wrong bin),
   - missing citation keys,
   - “needs more context” items (snippet too vague to use).

OUTPUT FORMAT (use exactly)

A) Global inventory (high level)
- Total evidence items found: #
- Citation keys found: #
- Items missing citation keys: #
- Bins with most evidence: ...
- Bins with least evidence: ...

B) Bucketed map by bin
- Bin: <exact bin name>
  - Bucket 1: <label>
    - Evidence items:
      - (CitationKey, p.__ if present): “verbatim snippet/quote”
      - ...
    - Notes (optional): duplicates/conflicts/cross-tags
  - Bucket 2: <label>
    - Evidence items:
      - ...
  - Cross-cutting tags for this bin (optional): #tag1 #tag2 ...

C) Cross-cutting buckets (global)
- Bucket label:
  - Appears in bins: ...
  - Key evidence items (top 3–8):
    - ...

D) Cleanup / action list
- Duplicates:
  - ...
- Conflicts/Tensions:
  - ...
- Misfiled:
  - ...
- Missing citation keys:
  - ...
- Needs more context:
  - ...

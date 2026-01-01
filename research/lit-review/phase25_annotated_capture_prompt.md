# Phase 2.5 Annotated Capture Prompt (Adds Clustering Metadata)

Use this prompt when you want **the same Phase 2 verbatim evidence extraction** plus a lightweight **Phase 2.5 annotated capture** to help you cluster and synthesize later.

---

## Copy/Paste Prompt

```text
You are helping me ingest evidence for a literature review. 
Your job is to:
(1) Map the paper to the most relevant section bins from my outline, and
(2) Extract VERBATIM quotes from the paper that I can paste into those bins,
(3) Add an “Annotated Capture” section to support clustering in Phase 2.5.

IMPORTANT RULES (EVIDENCE)
- Use only text that appears in the paper verbatim for quotes.
- Every quote must include location metadata: page # plus either section heading or figure/table number (or paragraph identifier if available).
- Keep quotes short and surgical (1–4 sentences each). Prefer exact definitions, claims, limitations, methodological details, results, or crisp framing statements.
- Do not paraphrase quotes. Preserve original wording, punctuation, and bracketed citations inside the quote.
- If a quote is longer than 4 sentences, trim it but keep the most information-dense part.
- If you cannot find a quote for a bin, do not invent one—leave it blank.
- If the paper contradicts itself or is ambiguous, capture both quotes and label them “Tension/Conflict”.

INPUTS
A) LITERATURE REVIEW OUTLINE BINS (use these exact names)
1. Systems Engineering, MBSE, and AI Foundations
   1.1 Complexity, Interdependencies, and Emergence in Systems Engineering
   1.2 Document-Centric vs. Model-Centric Workflows
   1.3 Opportunities for AI and Large Language Models in Systems Engineering
   1.4 Foundational Capabilities, Failure Modes, and Limitations of Language Models
       1.4.1 Foundational Capability
       1.4.2 Failure Modes
       1.4.3 Challenges and Limitations

2. Benchmarking Language Models: Foundations, Modalities, and Gaps
   2.1 Foundations of Benchmarking in AI
       2.1.1 Benchmarking Nomenclature
       2.1.2 Dataset Creation, Saturation, and Deprecation
           2.1.2.1 Creation
           2.1.2.2 Deprecation
       2.1.3 General Benchmark Frameworks and Evaluation Tools
   2.2 Evaluation Modalities for LLM Performance
       2.2.1 Multiple-Choice Question (MCQ) Evaluation
       2.2.2 Open Style Question and Free-Response Evaluation
   2.3 Current Benchmarking Landscape
       2.3.1 General Knowledge Benchmarks
       2.3.2 Domain-Specific Benchmarks
       2.3.3 Unique Evaluation Challenges in Systems Engineering

3. Cost Modeling and Tokenomics
   3.1 Established SE Cost-Modeling Foundations
   3.2 Emergence of Tokenomics Cost Modeling for Language Models

B) PAPER TEXT
I will paste the paper text (or relevant sections) below this line.
----------------
[PASTE PAPER HERE]
----------------

OUTPUT FORMAT (use this structure exactly)

Paper metadata (if available)
- Title:
- Authors:
- Year:
- Venue:
- DOI/URL (if present):

Bin mapping (multiple allowed)
- Primary bins (top 1–3):
  - Bin:
    - Why it fits (1 sentence, NO paraphrase of claims—just topic alignment)
- Secondary bins (optional):
  - Bin:
    - Why it fits (1 sentence)

Evidence extraction (VERBATIM QUOTES)
For each bin you mapped, provide 3–8 quotes:
- Bin: <exact bin name>
  - Quote 1: “...”
    - Location: p. __, Section: __ (or Figure/Table __)
    - Evidence type: {definition | method | result | limitation | claim | dataset | metric | threat-to-validity | other}
  - Quote 2: “...”
    - Location: ...
  - (continue)

Key terminology (verbatim)
- Term: “exact term”
  - Definition quote: “...”
  - Location: ...
  - Suggested bins: ...

Limitations / threats (verbatim)
- Quote: “...”
  - Location: ...
  - Suggested bins: ...

Annotated Capture (CLUSTERING SUPPORT; light synthesis allowed)
- One-sentence thesis of the paper (your words, 1 sentence)
- Contribution bullets (your words, 3–6 bullets max)
- Methods in 1–2 bullets
- What this paper is NOT about (1–3 bullets)
- Suggested cluster tags (5–12 tags, short phrases)
- Most “citable” 5 claims (each claim must be supported by a quote you extracted above; reference the Quote #)
  - Claim:
  - Supported by: Bin __, Quote __

If you need more context
- List the exact headings/sections you want me to paste next (max 5), and why.
```

---

## Optional Add-ons

### Draft-friendly “Paste Blocks”
Add this line at the end of the prompt if you want paste-ready bullets for your draft:

```text
Also produce a “Paste Blocks” section:
For each bin: 
- Provide bullet points formatted as:
  - (CitationKey, p.__): “verbatim quote”
```

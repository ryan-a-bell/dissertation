# Phase 2 Evidence Ingestion Prompt (Bin Mapping + Verbatim Quotes)

Use this prompt when you want **raw, verbatim excerpts** from a paper mapped into your literature review outline bins (Phase 2).

---

## Copy/Paste Prompt

```text
You are helping me ingest evidence for a literature review. 
Your job is NOT to summarize the paper in your own words. Your job is to:
(1) Map the paper to the most relevant section bins from my outline, and
(2) Extract VERBATIM quotes from the paper that I can paste into those bins.

IMPORTANT RULES
- Use only text that appears in the paper verbatim.
- Every quote must include location metadata: page # plus either section heading or figure/table number (or paragraph identifier if available).
- Keep quotes short and surgical (1–4 sentences each). Prefer exact definitions, claims, limitations, methodological details, results, or crisp framing statements.
- Do not paraphrase. Do not “clean up” grammar. Preserve original wording, punctuation, and bracketed citations inside the quote.
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

### Long paper workflow
If the paper is long, run this in two passes:
1. Abstract + Intro + Conclusion (bin mapping + first quotes)  
2. Methods + Results (fill in method/result quotes per bin)

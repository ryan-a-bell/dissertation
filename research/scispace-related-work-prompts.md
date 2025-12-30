# SciSpace/Elicit Related-Work Prompts for Dissertation
# Ready-to-Use Prompts for Literature Analysis

> **Purpose**: Drop-in prompts for analyzing external research papers and generating dissertation-ready related-work subsections. Copy the appropriate prompt variant below, replace the `[EXTERNAL WORK]` section with the paper you're analyzing, and use with SciSpace, Elicit, or similar tools.

---

## Table of Contents

1. [Core Prompt (Recommended)](#1-core-prompt-recommended)
2. [Variant A: Ultra-Tight (Space-Constrained)](#2-variant-a-ultra-tight-space-constrained)
3. [Variant B: Comparative Emphasis](#3-variant-b-comparative-emphasis)
4. [Variant C: Gap-Highlighting](#4-variant-c-gap-highlighting)
5. [Variant D: Methodological Focus](#5-variant-d-methodological-focus)
6. [Usage Instructions](#usage-instructions)

---

## 1. Core Prompt (Recommended)

**Use this for most papers.** Produces 1-3 well-structured paragraphs suitable for Chapter 2 (Literature Review).

```
You are an academic writing assistant supporting a doctoral dissertation.

**Dissertation Context**

* **Title (working):**
  "Evaluation Modality Alignment to Systems Engineering Task Types: A Methodological Study of Language Models' Domain-Specific and Task-Specific Effectiveness Using Distractor Variation and Consensus-Based Grading"

* **Domain:**
  Systems Engineering, AI/LLMs, benchmarking, evaluation methodology, question format analysis, and LLM-as-Judge frameworks

* **Core Problem Addressed:**
  Systems Engineering (SE) lacks domain-specific benchmarks for evaluating Large Language Models (LLMs). Generic language benchmarks fail to capture SE-specific task types, vocabulary, MBSE reasoning, lifecycle analysis, or trade-space thinking. Without systematic evaluation, SE practitioners cannot reliably deploy LLMs in high-stakes workflows where faulty logic may influence architecture decisions, verification steps, or safety-critical systems. This dissertation addresses the gap by developing SysEngBench—a benchmark specifically designed for SE contexts—and investigates how evaluation modality (Multiple-Choice Questions vs. Open-Style Questions) affects measurement validity, difficulty, leniency, and cost-efficiency across different SE task categories aligned to INCOSE Handbook domains.

* **Primary Contributions:**

  * **C1: Task–Modality Alignment Framework for Systems Engineering Evaluation**
    Develops a systematic approach to match SE task types with appropriate evaluation formats (MCQ vs OSQ), incorporating suitability classification, multi-approach LLM judging, and correlation/consistency metrics.

  * **C2: Robustness Analysis of MCQ Evaluation Using Distractor Variation**
    Quantifies position bias in MCQ evaluation by generating position-rotated variants (answers at positions A, B, C, D) and applying statistical tests with effect-size quantification to measure evaluation robustness.

  * **C3: Extension of SysEngBench to Multi-Format Evaluation Items**
    Extends the base SysEngBench dataset to SysEngBench-A, -B, -C, -D (position variants) and SysEngBench-OSQ (open-style questions) through LLM-assisted conversion with rubric and Bloom's taxonomy assignment.

  * **C4: Comparative Effectiveness of MCQ, OSQ, and Hybrid Evaluation Modalities**
    Compares multiple-choice and open-style question formats across standardized inference tasks using rubric-based LLM-as-Judge evaluation and cross-format statistical comparison to identify format-specific strengths and limitations.

  * **C5: Tokenomics Analysis**
    Analyzes cost–accuracy trade-offs through token tracking, ROI computation, and efficiency-frontier analysis to guide practical deployment decisions in resource-constrained SE environments.

  * **C6: Evidence-Based Guidance for Practical LLM Integration in SE Workflows**
    Synthesizes empirical findings into actionable recommendations for evaluation design, model selection, and deployment strategies tailored to real-world SE practice.

* **Methodological Framing:**
  The research employs a 6-phase pipeline:

  1. **Phase 1 (Data Preparation)**: Downloads and explores the base SysEngBench dataset from HuggingFace
  2. **Phase 2 (MCQ→OSQ Conversion)**: Uses frontier LLMs to assess MCQ-to-OSQ suitability and performs conversion with rubric generation for qualifying questions
  3. **Phase 3 (Position Variant Generation)**: Creates four position-rotated MCQ variants (correct answer systematically at A, B, C, D) to enable position bias detection
  4. **Phase 4 (Model Inference)**: Evaluates models across six tasks using lm-evaluation-harness: base SysEngBench, four position variants, and SysEngBench-OSQ
  5. **Phase 5 (LLM-as-a-Judge)**: Applies three academically-grounded judge prompts (multi-dimensional reference-based, chain-of-thought, pairwise comparative) to score OSQ responses
  6. **Phase 6 (Analysis)**: Performs statistical analysis including position bias detection, MCQ vs OSQ format comparison, inter-rater agreement analysis, and tokenomics evaluation

  Evaluation uses multiple judge models, Bloom's taxonomy alignment, and statistical testing for position bias, format differences, and cost-efficiency across INCOSE Handbook SE task categories.

---

**Task**
Analyze the provided external work and explain **how it relates to this dissertation**.

Your output should:

1. Briefly summarize the external work's **objective, methodology, and key findings**.
2. Clearly articulate **points of alignment** with this dissertation (e.g., similar goals, methods, evaluation philosophy, benchmarking approaches).
3. Explicitly identify **differences or gaps** (e.g., domain specificity, evaluation rigor, question format, judge modeling, scalability, position bias analysis, cost awareness).
4. Explain **how this dissertation extends, generalizes, or challenges** the external work.
5. Position the external work naturally within a **Related Work / Literature Review** narrative suitable for Chapter 2.

---

**Output Constraints**

* Write in **formal academic prose** suitable for direct inclusion in a dissertation chapter.
* Do **not** use bullet points in the final output.
* Do **not** overstate claims; avoid speculative language.
* Assume the reader is familiar with systems engineering and AI evaluation research.
* Length target: **1–3 well-structured paragraphs**.

---

**Narrative Guidance**

* Frame the external work as part of the broader evolution of LLM evaluation methodology, domain-specific benchmarking, or AI-assisted SE practices.
* Maintain a neutral, scholarly tone.
* Let the narrative flow naturally without explicitly listing "similarities" or "differences" as sections.
* Consider how the work relates to evaluation modality choices (MCQ vs OSQ), robustness testing, judge frameworks, or cost-aware deployment.

---

**External Work to Analyze**

[PASTE PAPER ABSTRACT / FULL TEXT / SCISPACE COLUMN CONTENT HERE]
```

---

## 2. Variant A: Ultra-Tight (Space-Constrained)

**Use when:** Chapter space is limited, or you need concise coverage of many papers.

```
You are an academic writing assistant supporting a doctoral dissertation on evaluation modality alignment for LLM benchmarking in Systems Engineering contexts.

**Dissertation Focus:**
This work develops SysEngBench and investigates MCQ vs OSQ evaluation modalities, position bias robustness, LLM-as-Judge frameworks, and tokenomics analysis for SE-specific tasks.

**Task:**
Produce a **single cohesive paragraph** (4-6 sentences) situating the external work relative to this dissertation. Emphasize methodological overlap and key distinctions. Avoid redundancy with prior related-work sections.

**Output Requirements:**
- Formal academic prose
- No bullet points
- Suitable for direct inclusion in Chapter 2
- Focus on how the work informs or contrasts with SysEngBench's multi-format evaluation approach

**External Work:**
[PASTE PAPER CONTENT HERE]
```

---

## 3. Variant B: Comparative Emphasis

**Use when:** You need to emphasize design choices and contrasts (good for benchmarking or evaluation papers).

```
You are an academic writing assistant supporting a doctoral dissertation titled:

"Evaluation Modality Alignment to Systems Engineering Task Types: A Methodological Study of Language Models' Domain-Specific and Task-Specific Effectiveness Using Distractor Variation and Consensus-Based Grading"

**Dissertation Core:**
- Develops SysEngBench for SE-specific LLM evaluation
- Compares MCQ vs OSQ evaluation formats
- Analyzes position bias through distractor rotation
- Implements multi-judge LLM-as-Judge frameworks
- Conducts tokenomics (cost-accuracy) analysis

**Task:**
Analyze the external work with **comparative emphasis** on:
1. Evaluation design choices (question format, task structure, domain specificity)
2. Judgment mechanisms (human judges, LLM judges, automated metrics)
3. Robustness testing (position bias, judge agreement, contamination)
4. Scalability and cost considerations

Explain how the external work's approach **compares and contrasts** with SysEngBench's methodology, particularly regarding question difficulty, subjectivity handling, and practical deployment.

**Output:**
1-3 paragraphs of formal academic prose suitable for Chapter 2.

**External Work:**
[PASTE PAPER CONTENT HERE]
```

---

## 4. Variant C: Gap-Highlighting

**Use when:** You need to justify your dissertation's novelty by identifying limitations in prior work.

```
You are an academic writing assistant supporting a doctoral dissertation on LLM evaluation for Systems Engineering.

**Dissertation Contributions:**
- Domain-specific benchmark (SysEngBench) for SE tasks
- Multi-format evaluation (MCQ with position variants, OSQ with rubrics)
- Position bias quantification and robustness analysis
- LLM-as-Judge with inter-rater agreement analysis
- Cost-aware evaluation (tokenomics)

**Task:**
Analyze the external work and **explicitly highlight limitations** that motivate the need for approaches introduced in this dissertation.

Focus on gaps such as:
- Lack of domain-specific evaluation for Systems Engineering
- Absence of multi-format comparison (MCQ vs OSQ)
- Insufficient position bias testing in MCQ benchmarks
- Limited judge diversity or consensus analysis
- Missing cost-efficiency considerations

**Output:**
1-3 paragraphs of formal academic prose that position this dissertation as addressing identified gaps.

**External Work:**
[PASTE PAPER CONTENT HERE]
```

---

## 5. Variant D: Methodological Focus

**Use when:** The external work has strong methodological relevance (judge design, statistical methods, benchmark construction).

```
You are an academic writing assistant supporting a doctoral dissertation on evaluation methodology for LLM benchmarking in Systems Engineering.

**Dissertation Methodology:**
- 6-phase pipeline: data prep, MCQ→OSQ conversion, position variant generation, model inference, LLM-as-Judge, statistical analysis
- Three judge prompts: multi-dimensional (LLM-Eval-inspired), chain-of-thought (MT-Bench/G-Eval), pairwise (AlpacaEval)
- Statistical tests for position bias, format comparison, and inter-rater agreement
- Bloom's taxonomy alignment and INCOSE domain categorization
- Token-cost tracking and efficiency frontier analysis

**Task:**
Analyze the external work's **methodological contributions** and explain:
1. How its methods informed or validated approaches used in this dissertation
2. Which aspects were adapted or extended for SE contexts
3. What methodological gaps this dissertation addresses

**Output:**
1-3 paragraphs emphasizing methodological lineage and innovation.

**External Work:**
[PASTE PAPER CONTENT HERE]
```

---

## Usage Instructions

### Step 1: Select Your Prompt Variant
- **Most papers**: Use Core Prompt (Variant 1)
- **Space-limited chapters**: Use Ultra-Tight (Variant A)
- **Benchmarking/evaluation papers**: Use Comparative Emphasis (Variant B)
- **Justifying novelty**: Use Gap-Highlighting (Variant C)
- **Methodology-heavy papers**: Use Methodological Focus (Variant D)

### Step 2: Populate External Work Section
Replace `[PASTE PAPER CONTENT HERE]` with:
- Paper abstract + methods section (recommended)
- Full paper text (if available)
- SciSpace/Elicit summary column content

### Step 3: Process with LLM Tool
- Copy complete prompt to SciSpace, Elicit, Claude, or ChatGPT
- Run once per paper
- No need to modify dissertation context between papers

### Step 4: Human Review Pass
- Check for hallucinations (compare against source paper)
- Adjust tone for consistency with your writing voice
- Remove phrases like "novel" or "first" unless in original source
- Verify technical accuracy of SE terminology

### Step 5: Integration
- Paste into appropriate Chapter 2 subsection
- Add in-text citation
- Perform final coherence check with surrounding paragraphs

---

## Tips for Best Results

**To Reduce Hallucinations:**
- Always include methods section, not just abstract
- Verify specific claims against source material
- Cross-check numeric results and publication venues

**To Maintain Narrative Coherence:**
- Use same dissertation context for all papers in a cluster
- Group related papers and process sequentially
- Consider thematic subsections (e.g., "Benchmarking", "LLM-as-Judge", "Position Bias")

**To Scale Efficiently:**
- Process papers in batches (5-10 at a time)
- Use Ultra-Tight variant for less-central papers
- Save outputs to individual files for later assembly

**For LaTeX Integration:**
- Request LaTeX-compatible output if needed (add "use LaTeX formatting" to output constraints)
- Ensure citation placeholders are clearly marked

---

## Example Workflow

**Scenario:** You're analyzing MT-Bench (Zheng et al., 2023) for your LLM-as-Judge section.

1. **Select**: Core Prompt (comprehensive coverage)
2. **Populate**: Paste MT-Bench abstract + methodology from paper PDF
3. **Process**: Run through Claude/ChatGPT
4. **Review**: Check that pairwise comparison method is accurately described
5. **Integrate**: Place in Chapter 2, Section "LLM-as-Judge Frameworks"
6. **Cite**: Add `\cite{zheng_mt_bench_2023}` in LaTeX

---

## Advanced Customization

### Adding Chapter-Specific Context
If targeting a specific chapter subsection, add to the dissertation context:

```
**Current Chapter Focus:**
This analysis will appear in Section 2.X: [Subsection Title], which covers [brief description].
```

### Requesting Specific Format
Add to output constraints:

```
* Include a topic sentence that explicitly connects to [specific concept]
* Conclude with a transition sentence to [next subsection topic]
* Use LaTeX citation format: \cite{author_year}
```

### Batch Processing Automation
For scripting (Python example):

```python
prompt_template = open('core_prompt.txt').read()
papers = load_papers_from_csv('papers.csv')

for paper in papers:
    filled_prompt = prompt_template.replace('[PASTE PAPER CONTENT HERE]', paper.content)
    result = llm_api_call(filled_prompt)
    save_output(f"{paper.id}_related_work.txt", result)
```

---

## Related Files in This Repository

- `/research/se_ai_consensus_agent_frameworks_research_master_notes.md` - Extended research notes on consensus methods
- `/src/phase5_llm_as_a_judge/llm-as-a-judge-from-academia.md` - Academic foundations for judge prompts
- `/manuscript/overleaf/chapter2.tex` - LaTeX source for Literature Review chapter
- `/docs/publications/` - Publication artifacts and conference submissions

---

## Questions or Customization Needed?

If you need:
- **Exact alignment to a specific Chapter 2 subsection** (e.g., "MBSE and AI", "Benchmarking Evolution")
- **LaTeX-ready output with specific formatting**
- **A worked example using one of your known papers**
- **Automation scripts for batch processing**

Let me know which papers you're analyzing and I can generate custom variants or worked examples.

---

**Version:** 1.0
**Last Updated:** 2025-12-30
**Compatible with:** SciSpace, Elicit, Claude, ChatGPT, Gemini
**License:** MIT (same as dissertation repository)

# Worked Examples: Related-Work Prompts in Action

> **Purpose**: Concrete examples showing what output to expect from each prompt variant. Use these to calibrate quality and style expectations.

---

## Example 1: Core Prompt Applied to MT-Bench

### Input Context
**External Work**: Zheng et al. (2023) - "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"

**Paper Summary**: MT-Bench introduces a multi-turn conversation benchmark using LLM-as-a-judge evaluation with pairwise comparison and chain-of-thought reasoning. Tests models across 8 categories with GPT-4 as primary judge.

**Prompt Used**: Core Prompt (Variant 1)

---

### Expected Output (Academic Prose, 3 paragraphs)

Zheng et al. (2023) introduced MT-Bench as a multi-turn conversation benchmark that leverages large language models as evaluators, specifically employing GPT-4 to judge model responses through pairwise comparison. The framework incorporates chain-of-thought reasoning to enhance transparency in the evaluation process and tests models across eight distinct conversational categories including writing, roleplay, reasoning, and coding. This work demonstrated that LLM-based judges can achieve over 80% agreement with human preferences while offering significantly faster and more scalable evaluation compared to traditional human annotation pipelines. The methodological emphasis on structured prompting and bias mitigation strategies—such as randomizing response order to counteract position effects—establishes MT-Bench as a foundational reference for automated evaluation in conversational AI contexts.

The MT-Bench approach aligns with this dissertation's LLM-as-a-Judge framework introduced in Phase 5, particularly in its adoption of structured prompting and multi-dimensional assessment. However, this dissertation extends beyond conversational evaluation to domain-specific systems engineering tasks, incorporating three distinct judge variants: multi-dimensional reference-based evaluation (inspired by LLM-Eval), chain-of-thought reference-guided assessment (adapting MT-Bench's reasoning approach), and pairwise comparative evaluation (drawing from both MT-Bench and AlpacaEval). While MT-Bench focuses on open-ended conversational quality, this research applies similar judging principles to both Multiple-Choice Questions and Open-Style Questions grounded in INCOSE-aligned SE task categories, enabling direct comparison of evaluation modalities within a controlled domain context.

A key distinction lies in the treatment of ground truth and rubric design. MT-Bench operates in domains where "correct" answers are subjective and multifaceted, relying on holistic quality judgments. In contrast, SysEngBench incorporates both objective MCQ scoring and rubric-based OSQ evaluation with explicit Bloom's taxonomy alignment, full-credit criteria, partial-credit criteria, and no-credit thresholds derived from SE educational standards. This dissertation further addresses position bias through systematic distractor rotation (SysEngBench-A, -B, -C, -D variants) and analyzes inter-judge agreement across multiple judge models, providing robustness analysis not present in MT-Bench's single-judge paradigm. Additionally, the inclusion of tokenomics analysis offers cost-aware evaluation guidance essential for practical SE deployment, extending MT-Bench's methodological contributions into resource-constrained engineering workflows.

---

### Why This Works
- **First paragraph**: Summarizes MT-Bench objectively
- **Second paragraph**: Identifies alignments (LLM-as-Judge, structured prompting)
- **Third paragraph**: Highlights differences (domain, ground truth, robustness, cost)
- **Throughout**: Natural narrative flow, formal tone, no bullet points
- **Integration**: Ready to drop into Chapter 2, Section 2.5 (LLM-as-Judge Frameworks)

---

## Example 2: Ultra-Tight Variant Applied to MMLU

### Input Context
**External Work**: Hendrycks et al. (2021) - "Measuring Massive Multitask Language Understanding (MMLU)"

**Paper Summary**: MMLU benchmark covering 57 subjects across STEM, humanities, social sciences using multiple-choice questions. Tests knowledge breadth and zero-shot/few-shot capabilities.

**Prompt Used**: Ultra-Tight Variant A

---

### Expected Output (Single Paragraph)

Hendrycks et al. (2021) introduced MMLU as a broad-coverage multiple-choice benchmark spanning 57 academic subjects to assess language models' multitask knowledge capabilities across STEM, humanities, and social sciences. While MMLU demonstrated the value of diverse domain coverage and MCQ-based evaluation for measuring zero-shot and few-shot performance, it lacks the domain depth required for specialized fields like systems engineering. This dissertation builds on MMLU's MCQ methodology but focuses exclusively on SE-specific task types aligned to INCOSE categories, incorporates position-rotated variants to quantify robustness, and extends evaluation to open-style questions with rubric-based judging, addressing gaps in both domain specialization and evaluation modality analysis.

---

### Why This Works
- **Compact**: Single paragraph, ~100 words
- **Complete**: Covers objective, alignment, gaps
- **Efficient**: Suitable for less-central papers in Chapter 2
- **Transition-ready**: Can easily link to next paper or subsection

---

## Example 3: Comparative Emphasis Applied to BIG-Bench

### Input Context
**External Work**: Srivastava et al. (2022) - "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models (BIG-Bench)"

**Paper Summary**: Collaborative benchmark with 200+ diverse tasks targeting areas where LLMs struggle. Community-driven, includes human baselines, focuses on model scaling trends.

**Prompt Used**: Comparative Emphasis Variant B

---

### Expected Output (2 paragraphs with comparison focus)

Srivastava et al. (2022) developed BIG-Bench as a community-driven benchmark comprising over 200 diverse tasks explicitly designed to probe language model limitations and scaling behaviors. The benchmark emphasizes breadth over depth, incorporating tasks ranging from linguistic reasoning and mathematical problem-solving to social understanding and algorithmic challenges. BIG-Bench's methodology includes human baseline comparisons to contextualize model performance and extensive documentation of task construction principles, enabling researchers to assess how model capabilities evolve with parameter scale. The collaborative, open-source nature of BIG-Bench facilitated rapid expansion of evaluation coverage across multiple domains, demonstrating the value of community-contributed task curation for comprehensive capability assessment.

Where BIG-Bench prioritizes task diversity and scaling analysis across general cognitive domains, this dissertation emphasizes domain-specific depth and evaluation modality alignment within systems engineering contexts. BIG-Bench's 200+ tasks span numerous fields at surface level, whereas SysEngBench's 400+ items concentrate exclusively on SE task categories aligned to INCOSE Handbook domains—requirements analysis, architecture design, verification and validation, lifecycle management—ensuring representative coverage of SE-specific reasoning structures. BIG-Bench tasks are predominantly multiple-choice or short-answer format evaluated via exact-match or rule-based scoring, while this research systematically compares MCQ evaluation (including robustness testing through position-rotated variants) against OSQ evaluation using LLM-as-a-Judge with academically-grounded rubrics. Furthermore, BIG-Bench does not address position bias in MCQ evaluation, inter-judge agreement in LLM-based scoring, or tokenomics analysis—all central contributions of this dissertation. While BIG-Bench provides valuable insights into model scaling trends, this work offers actionable guidance for deploying LLMs in specialized SE workflows where domain fidelity, cost-efficiency, and evaluation reliability are paramount.

---

### Why This Works
- **Explicit comparison**: Highlights design trade-offs (breadth vs depth)
- **Structured contrast**: BIG-Bench approach → SysEngBench differences
- **Actionable**: Shows how dissertation addresses different problem space
- **Professional**: Acknowledges BIG-Bench's value while establishing differentiation

---

## Example 4: Gap-Highlighting Applied to a Generic LLM Evaluation Paper

### Input Context
**External Work**: Hypothetical paper on general LLM capabilities without domain specialization

**Prompt Used**: Gap-Highlighting Variant C

---

### Expected Output (Emphasizing what's missing)

While [Author et al.] demonstrate LLM performance improvements on general-purpose language tasks, their evaluation framework lacks the domain-specific rigor required for specialized engineering disciplines. The reliance on broad benchmarks such as GLUE and SuperGLUE fails to capture the conceptual reasoning, trade-space analysis, and lifecycle-oriented thinking central to systems engineering practice. Furthermore, their exclusive use of multiple-choice evaluation with correct answers at fixed positions introduces potential position bias artifacts that remain unquantified in their results. The absence of open-ended evaluation formats prevents assessment of how models perform when generating free-form engineering analyses, a critical capability for SE workflows where practitioners require detailed justifications and multi-faceted reasoning rather than single-letter responses.

This dissertation addresses these gaps through SysEngBench's domain-specific focus on INCOSE-aligned SE tasks, systematic position bias quantification via distractor-rotated variants (A, B, C, D), and direct comparison of MCQ versus OSQ evaluation modalities using academically-grounded LLM-as-a-Judge frameworks. Where [Author et al.] report aggregate accuracy without cost consideration, this work incorporates tokenomics analysis to guide practical deployment decisions in resource-constrained engineering environments. The multi-judge consensus approach with inter-rater agreement metrics further provides robustness assurances absent in single-metric evaluation paradigms, ensuring that SE practitioners can deploy LLMs with evidence-based confidence rather than extrapolating from generic language benchmarks.

---

### Why This Works
- **Critical but professional**: Points out limitations constructively
- **Specific gaps**: Domain, format, bias, cost, consensus
- **Solution-oriented**: Shows how dissertation addresses each gap
- **Justifies novelty**: Makes clear case for contribution's value

---

## Example 5: Methodological Focus Applied to G-Eval

### Input Context
**External Work**: Liu et al. (2023) - "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment"

**Paper Summary**: Introduces chain-of-thought reasoning for LLM-based evaluation of natural language generation, showing improved alignment with human judgments.

**Prompt Used**: Methodological Focus Variant D

---

### Expected Output (Emphasis on methods)

Liu et al. (2023) advanced LLM-based evaluation methodology through G-Eval, which employs chain-of-thought reasoning to assess natural language generation quality. Their approach structures the evaluation process into explicit reasoning steps before scoring, enhancing transparency and improving alignment with human judgments compared to direct scoring methods. By prompting the judge model to articulate its reasoning process—identifying relevant criteria, analyzing text features, and justifying scores—G-Eval achieved stronger correlation with human evaluations across multiple NLG tasks including summarization and dialogue generation. This methodology demonstrated that guiding LLM judges through structured reasoning paths yields more reliable and interpretable evaluations than unstructured prompting approaches.

This dissertation adapts G-Eval's chain-of-thought methodology in Phase 5's Judge Prompt V2, specifically tailoring it for systems engineering educational assessment. Where G-Eval focuses on NLG quality dimensions (coherence, fluency, relevance), this research operationalizes chain-of-thought reasoning for SE-specific evaluation criteria including technical accuracy, conceptual understanding, Bloom's taxonomy alignment, completeness relative to expected answers, and professional communication quality. The structured 5-step analysis process—independent expert analysis, reference comparison, model response assessment, rubric application, and final scoring—draws directly from G-Eval's principles while incorporating domain-specific SE standards and educational frameworks. Additionally, this dissertation extends beyond single-judge evaluation to compare three distinct judge variants (multi-dimensional, chain-of-thought, and pairwise), analyzing inter-judge agreement and consensus stability—methodological robustness considerations not addressed in G-Eval's original formulation. The application of G-Eval-inspired reasoning to both MCQ suitability classification (Phase 2) and OSQ scoring (Phase 5) demonstrates the generalizability of structured judge reasoning across multiple evaluation contexts within a single SE benchmark pipeline.

---

### Why This Works
- **Method-centric**: Focuses on HOW rather than WHAT
- **Lineage**: Clearly traces methodological inheritance (G-Eval → Judge V2)
- **Adaptation**: Shows how methods were tailored for SE domain
- **Extension**: Highlights novel methodological contributions (multi-judge, consensus)
- **Integration**: Explains role across multiple dissertation phases

---

## Style and Tone Guidelines (Demonstrated in Examples)

### ✅ DO Use:
- Formal academic register
- Past tense for describing prior work
- Present tense for this dissertation's contributions
- Precise technical terminology
- Concrete comparisons with specifics
- Transitional phrases ("While X demonstrates...", "In contrast...", "This dissertation extends...")

### ❌ DON'T Use:
- Bullet points in final prose (save for methodological tables)
- Superlatives without evidence ("groundbreaking", "revolutionary")
- Vague claims ("somewhat better", "more advanced")
- First person ("I developed...")
- Colloquialisms or informal language
- Unsubstantiated "novel" or "first" claims

---

## Integration Examples: Where These Fit in Chapter 2

### Chapter 2 Structure (Example)

```latex
\chapter{Literature Review}\label{ch:literature_review}

\section{Systems Engineering Foundations}\label{sec:se_foundations}
% General SE papers go here (use Ultra-Tight for most)

\section{AI and LLMs in Engineering Contexts}\label{sec:ai_engineering}
% SE+AI integration papers (use Core or Ultra-Tight)

\section{Benchmarking and Evaluation Methodology}\label{sec:benchmarking}
\subsection{Evolution of LLM Benchmarks}
% MMLU, BIG-Bench, domain-specific benchmarks (use Comparative)
% PASTE EXAMPLE 2 OUTPUT HERE for MMLU

\subsection{Evaluation Modalities and Question Formats}
% MCQ vs open-ended studies (use Comparative)

\subsection{LLM-as-a-Judge Frameworks}
% MT-Bench, G-Eval, AlpacaEval (use Methodological)
% PASTE EXAMPLE 1 OUTPUT HERE for MT-Bench
% PASTE EXAMPLE 5 OUTPUT HERE for G-Eval

\subsection{Position Bias and Robustness}
% Bias detection studies (use Methodological)

\section{Gaps and Opportunities}\label{sec:gaps}
% Use Gap-Highlighting variant
% PASTE EXAMPLE 4 OUTPUT HERE for generic papers
```

---

## Quality Control Checklist

Use these examples as templates. Your outputs should:

- [ ] Match the formality level of Example 1
- [ ] Use similar paragraph structure (3-5 sentences per paragraph)
- [ ] Include specific methodological details (like Example 5)
- [ ] Make explicit comparisons (like Example 3)
- [ ] Avoid bullet points in prose (unlike this checklist!)
- [ ] Use transition phrases naturally
- [ ] Cite specific numbers/metrics from source papers
- [ ] Maintain objective, scholarly tone throughout

---

## Common Output Issues and Fixes

### Issue: Too Listy
**Bad**:
> MT-Bench has the following features:
> - Pairwise comparison
> - Chain-of-thought reasoning
> - Eight categories

**Good** (see Example 1):
> The framework incorporates chain-of-thought reasoning to enhance transparency in the evaluation process and tests models across eight distinct conversational categories...

---

### Issue: Too Vague
**Bad**:
> Their approach is similar to ours in some ways but different in others.

**Good** (see Example 3):
> Where BIG-Bench prioritizes task diversity and scaling analysis across general cognitive domains, this dissertation emphasizes domain-specific depth and evaluation modality alignment within systems engineering contexts.

---

### Issue: Overstating Novelty
**Bad**:
> Unlike all prior work, this dissertation is the first to ever consider position bias.

**Good** (see Example 4):
> The absence of open-ended evaluation formats prevents assessment of how models perform when generating free-form engineering analyses...this dissertation addresses these gaps through SysEngBench's domain-specific focus...

---

### Issue: Missing Integration
**Bad**:
> MT-Bench is a good benchmark. [End of paragraph, no connection to dissertation]

**Good** (see Example 1):
> The MT-Bench approach aligns with this dissertation's LLM-as-a-Judge framework introduced in Phase 5, particularly in its adoption of structured prompting and multi-dimensional assessment.

---

## Next Steps After Generating Content

1. **Validate against source**: Check that claims about the paper are accurate
2. **Check integration**: Ensure it connects naturally to adjacent paragraphs
3. **Add citations**: Insert `\cite{author_year}` references
4. **Review terminology**: Verify SE-specific terms are used correctly
5. **Read aloud**: Formal prose should flow smoothly when spoken
6. **Compare to examples**: Match tone and structure to examples above

---

## Files Referenced

- Full prompts: `/research/scispace-related-work-prompts.md`
- Quick reference: `/research/prompt-quick-reference.md`
- This file: `/research/prompt-worked-examples.md`

Use these three files together for comprehensive related-work generation support.

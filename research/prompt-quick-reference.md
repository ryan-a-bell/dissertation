# Quick Reference Card: Related-Work Prompts

> **TL;DR**: Copy-paste prompts for analyzing papers with SciSpace/Elicit. See full details in `scispace-related-work-prompts.md`.

---

## Decision Tree: Which Prompt to Use?

```
Is the paper central to your methodology?
├─ YES → Use CORE PROMPT (Variant 1)
└─ NO
   ├─ Need concise coverage? → Use ULTRA-TIGHT (Variant A)
   ├─ Benchmarking/evaluation paper? → Use COMPARATIVE (Variant B)
   ├─ Justifying novelty? → Use GAP-HIGHLIGHTING (Variant C)
   └─ Methodology-heavy? → Use METHODOLOGICAL (Variant D)
```

---

## Core Dissertation Context (Copy This Part for All Prompts)

```
**Dissertation Title:**
"Evaluation Modality Alignment to Systems Engineering Task Types: A Methodological Study of Language Models' Domain-Specific and Task-Specific Effectiveness Using Distractor Variation and Consensus-Based Grading"

**Core Problem:**
Systems Engineering lacks domain-specific LLM benchmarks. Generic benchmarks fail to capture SE task types, vocabulary, MBSE reasoning, and trade-space thinking. This dissertation develops SysEngBench and investigates MCQ vs OSQ evaluation modalities, position bias, LLM-as-Judge frameworks, and cost-efficiency.

**Six Contributions:**
C1: Task–Modality Alignment Framework
C2: Robustness Analysis via Distractor Variation
C3: Multi-Format SysEngBench Extension (A/B/C/D variants, OSQ)
C4: Comparative Effectiveness (MCQ vs OSQ)
C5: Tokenomics Analysis
C6: Evidence-Based SE Integration Guidance

**Methodology:**
6-phase pipeline: data prep → MCQ→OSQ conversion → position variants → inference → LLM-as-Judge → statistical analysis
```

---

## One-Liner Prompts for Quick Use

### For Most Papers (80% use case)
```
Analyze this paper for my dissertation on LLM evaluation modalities in Systems Engineering. My work develops SysEngBench (MCQ + OSQ), analyzes position bias, implements multi-judge frameworks, and conducts cost analysis. Write 2-3 formal academic paragraphs for Chapter 2 explaining how this work relates. [PASTE PAPER]
```

### For Tight Space
```
Write a single paragraph relating this work to my dissertation on MCQ vs OSQ evaluation for SE benchmarking with position bias analysis and LLM judges. [PASTE PAPER]
```

### For Gaps/Novelty
```
Analyze this paper and highlight gaps that my dissertation addresses: domain-specific SE benchmarking, multi-format evaluation, position bias testing, judge consensus, and cost analysis. [PASTE PAPER]
```

---

## Common Paper Types and Recommended Variants

| Paper Type | Recommended Prompt | Why |
|------------|-------------------|-----|
| Benchmarking papers (MMLU, BIG-Bench, etc.) | Comparative (B) | Emphasizes design choices |
| LLM-as-Judge papers (MT-Bench, AlpacaEval) | Methodological (D) | Focuses on judge design |
| Position bias / robustness studies | Methodological (D) | Highlights statistical methods |
| SE + AI integration papers | Core (1) | Comprehensive domain coverage |
| General LLM capability papers | Ultra-Tight (A) | Brief coverage sufficient |
| Evaluation methodology theory | Core (1) or Gap (C) | Depends on centrality |

---

## Chapter 2 Subsection Mapping

**Suggested placement** (adjust to your actual chapter structure):

| Chapter 2 Subsection | Relevant Paper Types | Recommended Prompt |
|---------------------|---------------------|-------------------|
| 2.1 SE Foundations, MBSE | SE complexity, MBSE tools | Core (1) |
| 2.2 LLM Capabilities & Limitations | GPT papers, capability studies | Ultra-Tight (A) |
| 2.3 Benchmarking Evolution | MMLU, BIG-Bench, domain benchmarks | Comparative (B) |
| 2.4 Evaluation Modalities | MCQ vs open-ended studies | Comparative (B) |
| 2.5 LLM-as-Judge Frameworks | MT-Bench, G-Eval, AlpacaEval | Methodological (D) |
| 2.6 Position Bias & Robustness | Bias detection studies | Methodological (D) |
| 2.7 Cost & Efficiency | Tokenomics, inference optimization | Core (1) or Comparative (B) |

---

## Example: Processing MT-Bench Paper

**Step 1**: Select Methodological Focus (Variant D)

**Step 2**: Copy full prompt from `scispace-related-work-prompts.md` → Variant D

**Step 3**: Paste MT-Bench abstract + methodology section at `[PASTE PAPER CONTENT HERE]`

**Step 4**: Run in Claude/ChatGPT/SciSpace

**Step 5**: Expected output (2-3 paragraphs) discussing:
- MT-Bench's pairwise comparison approach
- Chain-of-thought judge prompting
- How your Phase 5 adapted this for SE contexts
- Differences (domain, rubrics, multi-judge consensus)

**Step 6**: Paste into Chapter 2, Section 2.5 (LLM-as-Judge Frameworks)

**Step 7**: Add citation: `\cite{zheng_mt_bench_2023}`

---

## Checklist Before Submitting Prompt

- [ ] Selected appropriate prompt variant for paper type
- [ ] Included abstract + methods (not just abstract)
- [ ] Specified output length preference (if different from default)
- [ ] Included any chapter-specific context (if targeting specific subsection)
- [ ] Ready to paste results into Chapter 2 LaTeX file

---

## Post-Processing Checklist

After receiving LLM output:

- [ ] Verify technical accuracy against source paper
- [ ] Check for hallucinations (especially numbers, dates, claims)
- [ ] Ensure SE terminology is correct
- [ ] Remove unsubstantiated "novel" or "first" claims
- [ ] Adjust tone for consistency with your voice
- [ ] Add in-text citation in LaTeX: `\cite{author_year}`
- [ ] Verify flow with adjacent paragraphs

---

## Batch Processing Template (Python Pseudocode)

```python
# Load prompt template
prompt = load_file('core_prompt.txt')

# Load papers to analyze
papers = [
    {'id': 'zheng2023', 'title': 'MT-Bench', 'content': '...'},
    {'id': 'lin2023', 'title': 'LLM-Eval', 'content': '...'},
    # ... more papers
]

# Process each
for paper in papers:
    filled = prompt.replace('[PASTE PAPER CONTENT HERE]', paper['content'])
    result = call_llm_api(filled)
    save_file(f"output/{paper['id']}_related_work.txt", result)
```

---

## Troubleshooting

**Problem**: Output is too generic
**Solution**: Add more methodological detail to dissertation context or use Methodological Focus variant

**Problem**: Output claims things not in source paper
**Solution**: Always include methods section, not just abstract. Post-process with fact-checking.

**Problem**: Output doesn't fit chapter subsection
**Solution**: Add "Current Chapter Focus" to dissertation context specifying subsection topic

**Problem**: Need LaTeX formatting
**Solution**: Add to output constraints: "Use LaTeX citation format \cite{} and preserve formatting for direct inclusion"

**Problem**: Need batch processing 50+ papers
**Solution**: Use scripting approach (see batch template above) with Ultra-Tight variant for efficiency

---

## File Locations

- **Full Prompts**: `/research/scispace-related-work-prompts.md`
- **This Quick Reference**: `/research/prompt-quick-reference.md`
- **Chapter 2 LaTeX**: `/manuscript/overleaf/chapter2.tex`
- **LLM Judge Details**: `/src/phase5_llm_as_a_judge/llm-as-a-judge-from-academia.md`

---

**Print this card** or keep open in a second window while processing papers.

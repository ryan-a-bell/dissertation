# Chapter 3 Review: Comparison Against Source Code Implementation

**Review Date:** 2025-12-29
**Reviewed By:** Claude (Automated Analysis)
**Scope:** chapter3.tex vs. src/phase1-6 implementations

---

## Summary Table: Chapter 3 vs. Source Code Comparison

| Phase | Section | Issue Type | Description | Suggestion |
|-------|---------|------------|-------------|------------|
| **1** | 3.3.1 | Minor Omission | Chapter doesn't mention INCOSE category explosion (1,144 → 1,210 rows when multi-category questions are exploded) | Add sentence about data transformation and row expansion |
| **1** | 3.3.1 | Minor Omission | Visualizations generated (pie/bar/stacked charts) not mentioned | Reference that visualizations were created for exploratory analysis |
| **2** | 3.3.2 | Glaring Omission | **Conversion statistics missing**: 845/1,144 (73.9%) converted, 299 rejected, avg suitability score 7.53 | Add paragraph with conversion yield statistics |
| **2** | 3.3.2 | Minor | JSON parsing retry logic not mentioned (code retries once on parse errors) | Add to quality control section |
| **2** | 3.3.2 | Minor | Comprehensive logging to `raw_queries/` not documented | Mention artifact logging for reproducibility |
| **4** | 3.4.1 | **Glaring Omission** | **DoD HPC execution environment not mentioned** - code has SLURM scripts, Singularity containers, Open OnDemand integration | Add subsection or paragraph on DoD HPC infrastructure |
| **4** | 3.4.1 | Moderate | Model selection test runs (`test-evals-for-model-selection/`) not documented | Mention preliminary model selection process |
| **4** | 3.4.1 | Minor | Thinking model handling (o1, o3) with empty `until` sequences and higher token limits not specified | Add note about reasoning model configuration differences |
| **5** | 3.4.3 | **Glaring - Incomplete** | Placeholder text remains: "I only ended up doing the rubric-based judging for now" | Complete section - remove informal notes, formalize scope |
| **5** | 3.4.3 | **Glaring Omission** | **Multiple judge models used** (gpt-5, gpt-5-mini, gpt-oss_120b per output files) but chapter doesn't specify which judges were actually used | Specify judge models used and rationale for selection |
| **5** | 3.4.3 | Moderate | Judge prompt not included (marked as "<<consider adding a prompt snippet>>") | Include actual judging prompt in chapter or Appendix |
| **5** | 3.4.3 | Moderate | Pre-processing step (`process_osq_for_judging.py`) not documented | Document the OSQ response preparation workflow |
| **5** | 3.4.3 | Moderate | Multi-dimensional scoring described but only rubric-based actually used - creates confusion | Either remove multi-dimensional section or clarify it wasn't used |
| **6** | 3.5.1 | Moderate | **Additional statistical tests in code not documented**: Kruskal-Wallis H test, ANOVA, Pairwise McNemar tests | Add these to position bias section or justify exclusion |
| **6** | 3.5.1 | Minor | **Additional effect sizes in code**: Kendall's W, Epsilon-squared (ε²) | Add to effect size descriptions |
| **6** | 3.5.2 | Minor | Inter-judge agreement analysis details sparse (code computes Spearman correlations between judges) | Expand description of how judge consistency is measured |
| **6** | 3.5.4 | Minor | Tokenomics section lacks specifics on how token counts are extracted from lm-eval output | Add detail on token extraction methodology |
| **Gen** | Throughout | Minor | `parsers.py` utility module not mentioned | Reference data parsing utilities |
| **Gen** | 3.2 | Minor | `model-list.xlsx` in src/ root not referenced | Consider mentioning model tracking spreadsheet |

---

## Priority Recommendations

### Priority 1: Glaring Issues (Must Fix)

#### 1. Phase 5 (LLM-as-Judge) Section Needs Completion

**Location:** Section 3.4.3 (lines ~549-630)

**Issues:**
- Placeholder text remains: *"I only ended up doing the rubric-based judging for now"* (line ~567)
- Placeholder: *"<<consider adding a prompt snippet>>"* (line ~578)
- Multi-dimensional scoring is described in detail but apparently not used
- Judge models actually used are not specified

**Evidence from code:**
```
src/phase5_llm_as_a_judge/sysengbench-osq-llm-judge/
├── anthropic__claude-sonnet-4.5/
│   ├── *__gpt-oss_120b-p1.jsonl
│   ├── *__openai_gpt-5-mini-p1.jsonl
│   └── *__openai_gpt-5-p1.jsonl
```

This shows three judge models were used: `gpt-5`, `gpt-5-mini`, and `gpt-oss_120b`.

**Suggested fix:**
1. Remove informal placeholder text
2. Specify the three judge models used and rationale
3. Either remove multi-dimensional scoring section or clearly state it was planned but not implemented
4. Add the actual judging prompt to Appendix

---

#### 2. Phase 2 Conversion Statistics Missing

**Location:** Section 3.3.2 (around line ~380)

**Missing data from code:**
- Total questions processed: 1,144
- Questions converted: 845 (73.9%)
- Questions rejected: 299 (26.1%)
- Average suitability score: 7.53
- Threshold used: ≥7

**Suggested addition after Quality Control subsection:**
```latex
\subsubsection{Conversion Yield}

Of the 1,144 MCQs in SysEngBench, 845 (73.9\%) met the suitability
threshold of $\geq 7$ and were successfully converted to OSQ format.
The remaining 299 questions (26.1\%) were excluded due to factors
such as heavy dependence on distractor options, visual requirements,
or inherent ambiguity. The average suitability score across all
questions was 7.53.
```

---

#### 3. DoD HPC Infrastructure Missing

**Location:** Section 3.2.1 (after RunPod description, ~line 123)

**Evidence from code:**
```
src/phase4_inference/dodhpc/
├── README.md
├── containers/lm_eval_ollama.def    # Singularity container
├── jobs/*.sbatch                     # SLURM batch scripts
├── scripts/submit_eval_jobs_*.py     # Job submission automation
└── ood_app/                          # Open OnDemand integration
```

**Suggested addition:**
```latex
\paragraph{DoD High-Performance Computing}

A subset of model evaluations utilized DoD HPC resources via SLURM
job scheduling. Singularity (Apptainer) containers were built from
definition files to ensure reproducible execution environments.
Job scripts automated the submission of evaluation tasks across
multiple nodes. An Open OnDemand web interface provided interactive
access for debugging and monitoring.
```

---

### Priority 2: Moderate Issues

#### 4. Phase 6 Statistical Tests Incomplete

**Location:** Section 3.5.1 (Position Bias Analysis)

**Tests in code but not documented:**
- Kruskal-Wallis H test (non-parametric alternative to ANOVA)
- ANOVA (one-way analysis of variance)
- Pairwise McNemar tests (paired comparisons between positions)

**Effect sizes in code but not documented:**
- Kendall's W (effect size for Friedman test)
- Epsilon-squared (ε²) (effect size for Kruskal-Wallis)

**Options:**
1. Add these to the methodology, OR
2. State they were computed but not reported if not used in results

---

#### 5. Model Selection Process Undocumented

**Location:** Section 3.4.1

**Evidence from code:**
```
src/phase4_inference/test-evals-for-model-selection/
├── anthropic__claude-sonnet-4.5/
├── google__gemini-2.5-pro/
├── gpt-4o-mini/
├── gpt-5.1/
├── openai__gpt-4.1/
└── openai__gpt-4o/
```

**Suggested addition:**
```latex
\paragraph{Model Selection}

Prior to full-scale evaluation, preliminary test runs were conducted
on a subset of questions to verify model compatibility, estimate
inference times, and identify any configuration issues. This informed
the final model selection and resource allocation strategy.
```

---

### Priority 3: Minor Issues

| Issue | Location | Quick Fix |
|-------|----------|-----------|
| INCOSE category explosion not mentioned | 3.3.1 | Add: "Questions belonging to multiple INCOSE categories were expanded, resulting in 1,210 category-question pairs for distributional analysis." |
| Exploratory visualizations not mentioned | 3.3.1 | Add: "Pie charts, bar charts, and stacked visualizations were generated to characterize benchmark coverage." |
| JSON retry logic | 3.3.2 | Add to Quality Control: "JSON parsing errors triggered automatic retry with a reminder prompt." |
| Logging to raw_queries/ | 3.3.2 | Add: "All LLM prompts and responses were logged with timestamps to enable audit trails." |
| Thinking model config | 3.4.1 | Add note: "Reasoning-extended models (e.g., o1, o3) required empty stop sequences and higher token limits." |
| Inter-judge Spearman correlation | 3.5.2 | Expand: "Inter-judge consistency was quantified using Spearman rank correlations between judge scores." |
| Token extraction method | 3.5.4 | Add: "Token counts were extracted from lm-evaluation-harness output logs." |
| parsers.py utility | General | Optional reference to data parsing utilities in reproducibility section |

---

## Files Referenced

### Source Code Reviewed:
- `src/phase1_prep/README.md`
- `src/phase1_prep/1.1_benchmark_download_and_analysis.ipynb`
- `src/phase2_conversion/README.md`
- `src/phase2_conversion/2.1_Converting_MCQ_to_OSQ.ipynb`
- `src/phase3_variants/README.md`
- `src/phase4_inference/README.md`
- `src/phase4_inference/dodhpc/README.md`
- `src/phase5_llm_as_a_judge/README.md`
- `src/phase6_analysis/README.md`
- `src/phase6_analysis/parsers.py`

### Manuscript Reviewed:
- `manuscript/overleaf/chapter3.tex`

---

## Action Items Checklist

- [ ] **P1:** Complete Phase 5 section - remove placeholders, specify judge models
- [ ] **P1:** Add Phase 2 conversion statistics (845/1144, 73.9%)
- [ ] **P1:** Add DoD HPC infrastructure paragraph
- [ ] **P2:** Document additional Phase 6 statistical tests or justify omission
- [ ] **P2:** Add model selection process description
- [ ] **P2:** Include judge prompt in Appendix
- [ ] **P3:** Address minor omissions as time permits

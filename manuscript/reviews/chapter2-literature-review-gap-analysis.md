# Chapter 2 Literature Review Gap Analysis

**Document:** `manuscript/overleaf/chapter2.tex`
**Review Date:** 2025-12-30
**Reviewer:** Claude (Opus 4.5)

---

## Executive Summary

Chapter 2 provides solid foundational coverage of systems engineering, MBSE, LLM basics, and benchmarking concepts. However, several gaps exist between the literature reviewed and the methodology employed in Chapters 3-4. The most critical omissions relate to **LLM-as-a-Judge methodology**, **position bias research**, and **AI4SE/SE4AI domain literature**—the latter already noted in the author's own to-do list (lines 3-9).

---

## Current Chapter Structure

| Section | Subsection | Status |
|---------|------------|--------|
| 2.1 SE, MBSE, and AI Foundations | SE complexity, interdependencies, emergence | Draft - needs citations |
| | Document-centric vs. Model-centric workflows | Draft - needs expansion |
| | Opportunities for AI/LLMs in SE | Placeholder |
| | LLM foundations, failure modes, limitations | Partial content |
| 2.2 Benchmarking Language Models | Foundations of benchmarking | Partial content |
| | General benchmark frameworks and tools | Placeholder |
| | Evaluation modalities (MCQ/OSQ) | Good foundation |
| | Current benchmarking landscape | Placeholder |
| | SE-specific evaluation challenges | Placeholder |
| 2.3 Cost Modeling and Tokenomics | COCOMO/COSYSMO foundations | Good |
| | Tokenomics for LLMs | Brief |

---

## Gap Analysis Summary Table

| Priority | Gap/Omission | Current Coverage | Suggested Additions | Relevant to |
|----------|--------------|------------------|---------------------|-------------|
| **HIGH** | LLM-as-a-Judge methodology | Figure reference only (lines 243-248) | Foundational papers: Zheng et al. 2023 (MT-Bench), Li et al. 2024 survey, Gu et al. 2025 survey. Discuss judge reliability, biases, agreement rates. | Phase 5 methodology |
| **HIGH** | Position bias in MCQ evaluation | Mentioned conceptually | Zheng et al. 2024 (already cited in Ch3), Ko et al. 2024, Pezeshkpour & Hruschka 2023. Discuss order effects, primacy/recency bias. | Phase 3 position variants |
| **HIGH** | AI4SE / SE4AI literature | Author's to-do (line 5-7) | INCOSE IS 2023/24/25 proceedings, SERC conference papers, Chagnon et al. 2024 (in refs), Longshore's work. | Domain positioning |
| **HIGH** | Inter-rater reliability metrics | None | Cohen's Kappa, Krippendorff's Alpha, ICC for LLM judges. Lin & Chen 2023 multi-dimensional scoring. | Phase 5 judge validation |
| **MEDIUM** | Bloom's Taxonomy in assessment | None | Anderson & Krathwohl 2001 revised taxonomy. Discuss cognitive levels for question classification. | OSQ conversion (Phase 2) |
| **MEDIUM** | Rubric-based evaluation | None | Educational measurement literature on analytic vs. holistic rubrics. Connects to OSQ grading criteria. | Phase 2 rubric generation |
| **MEDIUM** | Reasoning models & chain-of-thought | Brief mention (lines 87-88, 229) | Wei et al. 2022 (CoT), OpenAI o1 technical report, DeepSeek R1 paper. Discuss reasoning traces, thinking tokens. | Tokenomics analysis |
| **MEDIUM** | Human expert baselines | None | Studies comparing LLM to human performance in domain tasks. Sets context for "good enough" thresholds. | Results interpretation |
| **MEDIUM** | Prompt engineering strategies | Brief mention (lines 109-112) | Brown et al. 2020 (few-shot), systematic prompting literature. Important for reproducibility. | Phase 4 inference |
| **MEDIUM** | Data contamination detection | Brief mention (line 128) | Golchin & Surdeanu 2023, Sainz et al. 2023. Methods for detecting training data leakage. | Benchmark validity |
| **LOW** | Open vs. proprietary model comparison | None | Literature on capability gaps, transparency, reproducibility tradeoffs. | Model selection rationale |
| **LOW** | Digital Engineering Strategy | None | DoD DE Strategy 2018, NIST frameworks. Contextualizes AI adoption in defense SE. | Motivation |
| **LOW** | SysML v2 transition | Only SysML mentioned | OMG SysML v2 spec, transition challenges. | MBSE currency |
| **LOW** | Emergent capabilities at scale | Brief (line 87) | Wei et al. 2022 emergent abilities, scaling laws literature. | LLM foundations |
| **LOW** | Quantization effects on performance | None (covered in separate paper) | Cross-reference Bell 2025 quantization paper if relevant. | Tokenomics context |

---

## Detailed Recommendations

### 1. LLM-as-a-Judge (HIGH PRIORITY)

**Current state:** Only a figure and caption reference (lines 243-248) to Li et al. survey.

**Recommended additions:**
- Define LLM-as-a-Judge paradigm and its emergence as alternative to human evaluation
- Discuss key papers:
  - Zheng et al. 2023 - "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (foundational)
  - Li et al. 2024 - "LLMs-as-Judges: A Comprehensive Survey" (already in refs)
  - Gu et al. 2025 - "A Survey on LLM-as-a-Judge" (already in refs)
- Cover known limitations: position bias, verbosity bias, self-enhancement bias
- Discuss agreement rates between LLM judges and humans (Figure already included at line 251)
- Address judge model selection rationale (why GPT-4 class models)

**Suggested location:** New subsubsection under 2.2.3 (OSQ evaluation)

---

### 2. Position Bias Research (HIGH PRIORITY)

**Current state:** Conceptually mentioned in MCQ section but no dedicated literature review.

**Recommended additions:**
- Zheng et al. 2024 - Position bias in LLM MCQ evaluation (cited in Ch3, should be in Ch2)
- Ko et al. 2024 - "Large Language Models are Inconsistent and Biased Evaluators"
- Discuss primacy effect (preference for early options) vs. recency effect
- Connect to your Phase 3 methodology rationale

**Suggested location:** Under 2.2.3.1 (MCQ Evaluation) or new dedicated subsection

---

### 3. AI4SE / SE4AI Literature (HIGH PRIORITY)

**Current state:** Author's own to-do item (lines 5-7).

**Recommended additions:**
- INCOSE International Symposium 2023/24/25 proceedings on AI in SE
- SERC (Systems Engineering Research Center) conference papers
- Chagnon et al. 2024 - "A case study of AI usage within the INCOSE technical process" (in refs)
- Vaneman's recent MBSE + AI work
- Longshore's work on LLMs for MBSE (mentioned in Ch1 line 86)
- Wach's work (mentioned in Ch1 line 86)

**Suggested location:** New subsection 2.1.3 or integrated into 2.1.3 (Opportunities for AI)

---

### 4. Inter-rater Reliability Metrics (HIGH PRIORITY)

**Current state:** Not discussed.

**Recommended additions:**
- Cohen's Kappa for pairwise agreement
- Krippendorff's Alpha for multiple raters
- Intraclass Correlation Coefficient (ICC)
- Application to LLM judge consistency (multiple judges on same responses)
- Lin & Chen 2023 multi-dimensional scoring approach (cited in Ch3 line 582)

**Suggested location:** Under LLM-as-a-Judge section or new 2.2.4

---

### 5. Bloom's Taxonomy (MEDIUM PRIORITY)

**Current state:** Not mentioned in Chapter 2, but used in Phase 2 OSQ conversion.

**Recommended additions:**
- Anderson & Krathwohl 2001 - Revised Bloom's Taxonomy
- Six cognitive levels: Remember, Understand, Apply, Analyze, Evaluate, Create
- Application to question difficulty classification
- Relevance to measuring "depth" of understanding vs. surface recall

**Suggested location:** Under 2.2.3 evaluation modalities, connecting to OSQ design

---

### 6. Rubric-Based Evaluation (MEDIUM PRIORITY)

**Current state:** Not discussed despite Phase 2 generating rubrics.

**Recommended additions:**
- Educational measurement literature on rubric design
- Analytic vs. holistic rubrics
- Criteria for effective rubrics (validity, reliability, fairness)
- Application to automated scoring

**Suggested location:** Under 2.2.3.2 (OSQ evaluation)

---

### 7. Reasoning Models (MEDIUM PRIORITY)

**Current state:** Brief mentions of o1 and DeepSeek R1 (lines 229, 75 in Ch1).

**Recommended additions:**
- Wei et al. 2022 - "Chain-of-Thought Prompting Elicits Reasoning"
- OpenAI o1 technical reports
- DeepSeek R1 paper (already cited)
- Distinction between "thinking tokens" and "answer tokens"
- Implications for tokenomics (reasoning models generate more tokens)

**Suggested location:** Under 2.1.4 (LLM foundations) and 2.3.2 (tokenomics)

---

## References Already in Bib (Underutilized)

The following references exist in `references.bib` but are not adequately discussed in Chapter 2:

| Reference Key | Topic | Recommendation |
|---------------|-------|----------------|
| `li_llms_as_judges_2024` | LLM-as-Judge survey | Expand discussion beyond figure caption |
| `gu_survey_on_llm_as_a_judge_2025` | LLM-as-Judge survey | Cite and discuss |
| `zheng_large_2024` | Position bias | Move discussion from Ch3 to Ch2 |
| `Chagnon2024AIUsageINCOSE` | AI in INCOSE process | Cite in AI4SE section |
| `incose_is2024_2024` | INCOSE symposium | Reference for AI4SE trends |
| `lin2023multidim` | Multi-dimensional scoring | Discuss methodology basis |

---

## Structural Suggestions

1. **Add section numbers to to-do items** - Lines 3-9 have placeholder items without clear placement.

2. **Complete placeholder sections** - Several subsections have only bullet points or `<<add figure>>` notes.

3. **Consolidate LLM evaluation content** - Currently split between 2.1.4 (failure modes) and 2.2.3 (evaluation modalities). Consider reorganizing for flow.

4. **Add transition paragraphs** - Between major sections to improve narrative flow.

5. **Standardize figure labels** - Multiple figures use `\label{fig:placeholder}` which will cause cross-reference issues.

---

## Author's To-Do Items (from lines 3-9)

| Item | Status | Recommendation |
|------|--------|----------------|
| AI4SE and SE4AI 23/24/25 | Not addressed | HIGH priority - add dedicated subsection |
| INCOSE IS, etc | Not addressed | Integrate with AI4SE section |
| SERC conferences | Not addressed | Integrate with AI4SE section |
| Dimensions research GPT 53/54/40/6 | Unclear reference | Clarify and address |

---

## Next Steps

1. Address HIGH priority gaps first (LLM-as-Judge, Position Bias, AI4SE, Inter-rater reliability)
2. Complete placeholder sections with actual content
3. Fix duplicate/placeholder figure labels
4. Add missing citations from existing bib file
5. Review MEDIUM priority items for inclusion based on page constraints

---

*This analysis is based on the current draft state of Chapter 2 as of 2025-12-30.*

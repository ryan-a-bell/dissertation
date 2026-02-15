# Source Placement Recommendations for Chapter 2

**Date:** 2026-02-08
**Methodology:** Following source-placement-prompt workflow
**Objective:** Place 6-8 strongest papers from each .bib file into chapter2.tex

---

## Executive Summary

This document provides precise placement recommendations for strengthening Chapter 2's literature review by integrating high-quality sources from 15 .bib files. Each recommendation includes:
- **Exact location** (section, paragraph, sentence)
- **Citation to add**
- **Rationale** for placement
- **Optional patched sentence** if needed for coherence

---

## 1. Evaluation Modalities.bib (12 entries)

### Strongest 6-8 Papers:
1. **fu_mcq_reasoning_more_confident_when_wrong_2025** - MCQ confidence calibration
2. **wang_fake_alignment_2024** - MCQ vs OSQ performance discrepancy
3. **myrzakhan_open_llm_leaderboard_2024** - Selection bias and open-style questions
4. **goral_when_all_options_are_wrong_2024** - Critical thinking in MCQs
5. **wangAnswersReviewingRationality2024** - Response Variability Syndrome (REVAS)
6. **wangMyAnswerFirstToken2024** - First-token vs text answer misalignment
7. **ghanem_DISTO_2023** - Distractor quality evaluation
8. **yigitAdversarialDistractorGeneration2025** - Adversarial distractor generation

### Placement Recommendations:

#### **Placement 1: §2.5.1 Multiple-choice question (MCQ) evaluation, Line ~440**
**Current text (line 440):**
> "...relying solely on MCQs risks obtaining an incomplete picture of the model's actual capabilities."

**Recommendation:**
Add after line 440:
> Recent research reveals multiple systematic biases in MCQ evaluation that limit their reliability for qualification evidence. LLMs exhibit increased confidence when providing chain-of-thought reasoning before answering MCQs, regardless of correctness \cite{fu_mcq_reasoning_more_confident_when_wrong_2025}. Furthermore, LLM performance exhibits severe misalignment between multiple-choice and open-ended formats on identical safety questions, exposing what Wang et al.\ term ``fake alignment''—models that memorize answer styles without genuine understanding \cite{wang_fake_alignment_2024}. Response variability across question reformulations (REVAS) further demonstrates that MCQ-based benchmarks may not capture true LLM capabilities \cite{wangAnswersReviewingRationality2024}.

**Rationale:**
Lines 437-440 discuss MCQ limitations but lack concrete evidence. These three papers provide empirical support for why MCQs are insufficient for SE qualification.

---

#### **Placement 2: §2.5.1, Line ~410 (Selection bias discussion)**
**Current text (line 410-414):**
> Discusses selection bias (Zheng et al.)

**Recommendation:**
After line 414, add:
> The transition from MCQ to open-style evaluation eliminates selection bias and random guessing but introduces challenges in answer validation \cite{myrzakhan_open_llm_leaderboard_2024}. When evaluating instruction-tuned models, first-token probabilities diverge severely from generated text answers, with mismatch rates exceeding 60\%, especially for safety-tuned models \cite{wangMyAnswerFirstToken2024}.

**Rationale:**
Strengthens the argument about MCQ limitations and motivates the shift to open-style questions discussed later.

---

#### **Placement 3: §2.5.1, Line ~422-426 (Distractor discussion)**
**Current text:**
> References DISTO and adversarial distractors

**Recommendation:**
Expand inline comment into text:
> Distractor quality fundamentally affects MCQ measurement validity. Standard machine translation metrics misjudge distractor suitability; learned metrics like DISTO better correlate with human quality ratings \cite{ghanem_DISTO_2023}. Adversarial distractor generation using in-context learning and rule-based approaches can systematically reduce model performance, revealing evaluation brittleness \cite{yigitAdversarialDistractorGeneration2025}.

**Rationale:**
Inline comments at lines 422-426 need to be integrated as proper claims with citations.

---

#### **Placement 4: §2.5.1, NEW paragraph after line 442**
**Recommendation:**
Add new paragraph:
> MCQs also fail to assess critical thinking when no correct answer exists—a crucial capability for qualification contexts where models must recognize uncertainty or incomplete information. Evaluations with all-incorrect options reveal significant performance gaps, with only the largest models (e.g., Llama-3.1-405B) successfully detecting invalid questions \cite{goral_when_all_options_are_wrong_2024}. This limitation is particularly consequential in systems engineering, where recognizing incomplete or contradictory requirements is as important as selecting correct options.

**Rationale:**
Adds a new dimension to MCQ limitations directly relevant to SE (recognizing invalid/incomplete specifications).

---

## 2. Dataset Creation and Deprecation.bib (36 entries)

### Strongest 6-8 Papers:
1. **Ayrton_San_Joaquin_2025_Deprecating_Benchmarks** - Benchmark deprecation criteria
2. **Liangtai_Sun_2023_SciEval_Benchmark** - Dynamic evaluation, Bloom's taxonomy
3. **varshneyCreatingSyntheticData2024** - Synthetic data generation pipeline
4. **chen_diversity_2024** - Diversity in synthetic data
5. **fuQGEvalBenchmarkingMultidimensional2024** - Multi-dimensional question evaluation
6. **Tianle_Li_2024_BenchBuilder_ArenaHard_LLM_Benchmarking** - Dynamic benchmark construction
7. **reuel_Better_Bench_Assessing_AI2024** - Benchmark quality framework
8. **Y_Thomas_Hou_2024_CompoundQA** - Compound question complexity

### Placement Recommendations:

#### **Placement 1: §2.6.2 Dataset lifecycle hazards, Line ~666**
**Current text (line 666):**
> "...benchmarks can become actively misleading unless versioned, retired, or scoped appropriately."

**Recommendation:**
Replace inline citation with expanded text:
> As tasks drift away from stakeholder-relevant work, benchmarks can become actively misleading unless versioned, retired, or scoped appropriately. Emerging work proposes explicit deprecation criteria including benchmark longevity distorting model evaluation and transparent deprecation frameworks to prevent misuse \cite{Ayrton_San_Joaquin_2025_Deprecating_Benchmarks}. Benchmark quality assessment frameworks evaluate 46 best practices across the benchmark lifecycle, revealing that commonly used benchmarks suffer from significant issues including lack of statistical significance reporting and poor replicability \cite{reuel_Better_Bench_Assessing_AI2024}.

**Rationale:**
Lines 666-667 mention deprecation but lack concrete frameworks. These papers provide actionable criteria.

---

#### **Placement 2: §2.6.2, Line ~642**
**Current text (line 642):**
> "...Bloom-style mappings and cognitive complexity frameworks can help align item difficulty with intended constructs"

**Recommendation:**
After the citation, add:
> SciEval demonstrates this approach by using Bloom's taxonomy to systematically evaluate scientific research ability across four dimensions, introducing dynamic question generation to prevent data leakage \cite{Liangtai_Sun_2023_SciEval_Benchmark}. Multi-dimensional evaluation frameworks like QGEval further decompose question quality into fluency, clarity, conciseness, relevance, consistency, answerability, and answer consistency, revealing that existing metrics fail to align well with human judgments across these dimensions \cite{fuQGEvalBenchmarkingMultidimensional2024}.

**Rationale:**
Provides concrete examples of Bloom's taxonomy application and multi-dimensional quality assessment.

---

#### **Placement 3: §2.6.2, Line ~654 (Synthetic data discussion)**
**Current text (line 654):**
> "...diversity and generation choices (seeds, prompts, model, real/synthetic ratios) measurably affect downstream performance and robustness"

**Recommendation:**
After existing citation, add:
> Synthetic data generation pipelines for LLMs now encompass question complexity manipulation (extractive, abstractive, diagnostic, aggregative, sentiment-driven), template-based variant creation, and quality filtering \cite{varshneyCreatingSyntheticData2024}. Synthetic data diversity—measured via cluster-based LLM scoring—correlates positively with both pre-training and supervised fine-tuning performance, with diversity effects being more pronounced during fine-tuning than pre-training \cite{chen_diversity_2024}.

**Rationale:**
Lines 653-654 mention diversity but lack implementation details. These papers provide concrete pipelines and empirical evidence.

---

#### **Placement 4: NEW subsection in §2.6.2 after Line ~667**
**Recommendation:**
Add new paragraph:

> \paragraph{Dynamic benchmark construction for continuous evaluation.}
> To address saturation and deprecation pressures, benchmark construction is shifting from static datasets to dynamic generation pipelines. BenchBuilder automatically curates high-quality prompts from crowdsourced data sources (e.g., Chatbot Arena) using LLM annotators to identify challenging, domain-diverse items, achieving 98.6\% correlation with human preference rankings at minimal cost \cite{Tianle_Li_2024_BenchBuilder_ArenaHard_LLM_Benchmarking}. Such approaches enable continuous benchmark updates without human labeling overhead, though they introduce new validity risks related to prompt selection bias and LLM annotator reliability.

**Rationale:**
Addresses the gap between static benchmarks and the need for continuous, evolving evaluation—directly relevant to SE qualification where requirements and practices evolve.

---

## 3. Dataset Decontamination.bib (9 entries)

### Strongest 6-8 Papers:
1. **Cheng_2024_Benchmark_Data_Contamination** - Comprehensive BDC survey
2. **yang_rethinking_2023** - Paraphrase-based contamination bypassing
3. **oren_black_box_contamination_2023** - Proving contamination in black-box models
4. **Dekoninck_2024_ConStat** - Performance-based contamination detection
5. **Ahuja_2024_Multilingual_Benchmark_Contamination** - Multilingual contamination
6. **Bordt_2024_Forgetting_Data_Contamination** - Forgetting dynamics

### Placement Recommendations:

#### **Placement 1: §2.6.2, Lines 660-669 (Contamination discussion)**
**Current text (lines 664-665):**
> "...Recent work distinguishes contamination types and proposes detection methods beyond naive string matching"

**Recommendation:**
Expand with concrete frameworks:
> Recent work systematically categorizes Benchmark Data Contamination (BDC) into levels ranging from semantic/topic exposure to full label exposure, emphasizing that even benchmark metadata and public analyses can indirectly bias evaluations \cite{Cheng_2024_Benchmark_Data_Contamination}. String-matching decontamination is insufficient: simple paraphrasing, translation, or code formatting changes bypass n-gram filters, enabling models to achieve GPT-4-level performance through overfitting \cite{yang_rethinking_2023}. For black-box models, contamination can be proven by testing whether canonical benchmark orderings are significantly more likely than shuffled variants—a signal that emerges from memorized example order rather than understanding \cite{oren_black_box_contamination_2023}.

**Rationale:**
Lines 664-665 mention detection methods but lack specificity. These three papers provide concrete, complementary approaches (categorization, attack methods, detection).

---

#### **Placement 2: §2.6.2, NEW paragraph after line 670**
**Recommendation:**
Add:
> \paragraph{Performance-based and statistical contamination detection.}
> Beyond training data inspection, contamination can be detected statistically by comparing performance on primary benchmarks against reference sets. ConStat reframes contamination as non-generalizing performance inflation, enabling detection without access to uncontaminated samples by measuring whether models exhibit abnormally high performance relative to reference models \cite{Dekoninck_2024_ConStat}. Multilingual settings introduce additional leakage pathways because translations and parallel corpora blur dataset boundaries, requiring contamination analysis across language pairs \cite{Ahuja_2024_Multilingual_Benchmark_Contamination}. Conversely, forgetting dynamics suggest that contamination effects may diminish under large-scale training, as sufficiently scaled regimes can erase early memorization \cite{Bordt_2024_Forgetting_Data_Contamination}.

**Rationale:**
Adds statistical detection methods and nuances (multilingual leakage, forgetting dynamics) absent from current text.

---

## 4. LLM as a Judge.bib (27 entries) + 3 Evaluation Methods for LLMs.bib (44 entries)

### Strongest 6-8 Papers from LLM-as-Judge context:
1. **li_llms_as_judges_2024** - Comprehensive survey
2. **gu_survey_on_llm_as_a_judge_2025** - Survey with bias taxonomy
3. **thakurJudgingJudgesEvaluating2025** - Meta-evaluation of judges
4. **dubois_Length_Controlled_Alpaca_Eval_Simple_2025** - Length bias mitigation
5. **zhouMitigatingBiasLarge2024** - Bias mitigation strategies
6. **huTrainingLLMasaJudgeModel2025** - Judge training pipeline
7. **zhengJudgingLLMasaJudgeMTBench2023** - MT-Bench and judge validation
8. **chandakAnswerMatchingOutperforms2025** - Answer matching vs MCQ

### Placement Recommendations:

#### **Placement 1: §2.5.3 LLM-as-judge, Line ~512**
**Current text (line 512):**
> "LLM-as-judge methods offer a scalable approach to evaluating OSQ outputs when golden answers are infeasible. However, judges can introduce systematic biases..."

**Recommendation:**
After line 512, expand with concrete bias taxonomy:
> Comprehensive surveys identify multiple bias categories affecting LLM judges: position bias (preference for first/last options), verbosity bias (favoring longer responses), self-enhancement bias (preferring own outputs), and style bias (alignment with judge's training distribution) \cite{li_llms_as_judges_2024, gu_survey_on_llm_as_a_judge_2025}. Meta-evaluations reveal that even best-performing judges differ from humans by up to 5 points, with percent agreement masking vast score differences \cite{thakurJudgingJudgesEvaluating2025}.

**Rationale:**
Line 512 mentions biases generically; these papers provide systematic taxonomies essential for qualification contexts.

---

#### **Placement 2: §2.5.3, NEW paragraph after line 512**
**Recommendation:**
Add:
> \paragraph{Mitigating judge bias through calibration and debiasing.}
> Length bias—where judges prefer longer outputs regardless of quality—can be mitigated through regression-based calibration that predicts preferences conditioning on zero length difference, improving correlation with human preferences from 0.94 to 0.98 \cite{dubois_Length_Controlled_Alpaca_Eval_Simple_2025}. More generally, bias mitigation strategies include prompt-level calibration, training-based debiasing with curated negative samples, and multi-judge ensembles \cite{zhouMitigatingBiasLarge2024}. Fine-tuned judge models can achieve human-level correlation on in-domain tasks but underperform GPT-4 on generalizability, fairness, and adaptability, revealing that judges function as task-specific classifiers rather than general evaluators \cite{huTrainingLLMasaJudgeModel2025}.

**Rationale:**
Current text mentions bias but not mitigation. These papers provide actionable solutions.

---

#### **Placement 3: §2.5.3, Line ~530-531 (BLEU discussion)**
**Current text (lines 517-527):**
> Discusses BLEU as early automatic judge

**Recommendation:**
After line 527, add transition to modern approaches:
> Modern LLM-as-judge approaches extend this lineage but introduce reasoning capabilities. For MCQ-style tasks, answer matching—where the model generates a free-form answer that is then validated against the reference using another LLM—outperforms traditional multiple-choice evaluation and LLM-as-judge without references, achieving near-perfect agreement with human grading \cite{chandakAnswerMatchingOutperforms2025}. MT-Bench demonstrates that strong LLM judges like GPT-4 can match controlled and crowdsourced human preferences at over 80\% agreement, though position, verbosity, and self-enhancement biases require explicit mitigation \cite{zhengJudgingLLMasaJudgeMTBench2023}.

**Rationale:**
Bridges historical BLEU discussion to modern LLM judges with concrete evidence of reliability and limitations.

---

## 5. Domain Specific Benchmarks.bib (16 entries)

### Strongest 6-8 Papers:
1. **zhouEngiBenchBenchmarkEvaluating2025** - Engineering problem-solving benchmark
2. **mudurFEABenchEvaluatingLanguage2025** - Multiphysics reasoning (FEA)
3. **syedBenchmarkingCapabilitiesLarge2024** - Transportation engineering benchmark
4. **guhaLegalBenchCollaborativelyBuilt2023** - Legal reasoning benchmark
5. **islamFinanceBenchNewBenchmark2023** - Financial QA benchmark
6. **Lingzhi_Yan_2024_LLM_Benchmarks_Medical** - Medical benchmarks survey
7. **dorisDesignQAMultimodalBenchmark2024** - Engineering documentation (multimodal)
8. **liEEEBenchComprehensiveMultimodal2025** - Electrical engineering benchmark

### Placement Recommendations:

#### **Placement 1: §2.4.1 Benchmarking in the LLM ecosystem, Line ~291**
**Current text (line 291):**
> "...Evidence from specialized benchmarking efforts consistently suggests that strong performance on broad or generic evaluations does not guarantee robust performance on domain-constrained tasks"

**Recommendation:**
After line 291, add concrete examples:
> Domain-specific benchmarks in engineering reveal this gap concretely. EngiBench evaluates LLMs across foundational knowledge retrieval, multi-step contextual reasoning, and open-ended modeling, demonstrating that models struggle as task complexity increases and perform poorly under perturbations \cite{zhouEngiBenchBenchmarkEvaluating2025}. FEABench shows that even when LLM reasoning appears coherent and code is executable, small physics or solver misconfigurations prevent numerically correct outcomes in finite element analysis tasks \cite{mudurFEABenchEvaluatingLanguage2025}. Similarly, transportation engineering evaluations reveal impressive accuracy but unexpected inconsistency in problem-solving behaviors across system design, planning, and control tasks \cite{syedBenchmarkingCapabilitiesLarge2024}. Legal and financial QA benchmarks further demonstrate that domain-specific terminology, multi-step reasoning, and evidence grounding requirements are not captured by general-purpose evaluations \cite{guhaLegalBenchCollaborativelyBuilt2023, islamFinanceBenchNewBenchmark2023}.

**Rationale:**
Line 291 makes a claim without concrete evidence. These five papers span engineering, legal, and financial domains, providing strong empirical support.

---

#### **Placement 2: §2.1 Systems Engineering Practice (NEW subsection)**
**Recommendation:**
After §2.1, add new subsection before §2.2:

> \subsection{Domain-specific evaluation requirements for systems engineering}
> Systems engineering evaluation introduces requirements absent from general NLP tasks. Engineering problems demand integration of visual and textual information (e.g., circuit diagrams, CAD models, system diagrams) alongside professional instructions, making them excellent candidates for rigorous LMM evaluation \cite{liEEEBenchComprehensiveMultimodal2025}. Multimodal engineering documentation benchmarks reveal that current models struggle to retrieve relevant design rules from technical standards, recognize components in CAD images, and analyze engineering drawings \cite{dorisDesignQAMultimodalBenchmark2024}. Medical domain benchmarks similarly emphasize that evaluation must span modalities (text, image, multimodal), clinical domains (EHRs, QA, imaging), and linguistic diversity, with dataset structure and clinical impact varying significantly across use cases \cite{Lingzhi_Yan_2024_LLM_Benchmarks_Medical}. Collectively, these domain-specific efforts demonstrate that SE qualification evidence requires task formulations, grading criteria, and robustness checks aligned to SE-specific artifact types, failure modes, and consequence profiles.

**Rationale:**
Adds explicit motivation for domain-specific evaluation before discussing SE practice, using engineering and medical examples to frame SE-specific requirements.

---

## 6. Governance of AI.bib (17 entries)

### Strongest 6-8 Papers:
1. **nist_ai_rmf_2023** - NIST AI RMF framework
2. **Office_of_Management_and_Budget_2024_M24-10_AI_Governance** - Federal AI governance
3. **Johnson_Operationalizing_AI_Assurance_2025** - DoD AI assurance operationalization
4. **Lanus_Tailorable_Risk_Informed_AI_Test_Evaluation_Strategy_2025** - TRAITES framework
5. **Charnetzki_Hazard_Analysis_RAG_LLM_Systems_2025** - STPA hazard analysis for RAG-LLMs
6. **Szajnfarber_SERC_Perspective_AI4SE_SE4AI_2025** - Workflow-aware AI assessment
7. **heckle2024responsible** - RAI principles in SE practice
8. **Pomales_Measuring_Influencing_Trustworthiness_AI_Enabled_Systems_2025** - Trustworthiness metrics

### Placement Recommendations:

#### **Placement 1: §2.4.3 Governance as forcing function, Line ~320**
**Current text (lines 320-322):**
> "...policy instruments similarly push agencies toward inventorying AI uses, applying risk-based safeguards, and documenting evidence commensurate with impacts"

**Recommendation:**
After line 322, expand with concrete frameworks:
> Operational AI governance frameworks translate these directives into lifecycle-aligned practices. The NIST AI RMF defines four core functions—Govern, Map, Measure, and Manage—across seven trustworthiness characteristics (validity, safety, fairness, transparency, etc.), framing AI risk as socio-technical and emphasizing tradeoffs among characteristics \cite{nist_ai_rmf_2023}. Federal guidance requires agencies to designate Chief AI Officers, inventory AI use cases annually, and apply minimum risk management practices for safety- and rights-impacting AI \cite{Office_of_Management_and_Budget_2024_M24-10_AI_Governance}. DoD operationalizes these principles through the Responsible AI Toolkit, SHIELD assessments, and assurance portals spanning development through sustainment \cite{Johnson_Operationalizing_AI_Assurance_2025}.

**Rationale:**
Lines 320-322 reference policy but lack concrete implementation frameworks. These three sources provide actionable governance structures.

---

#### **Placement 2: §2.4.3, NEW paragraph after line 324**
**Recommendation:**
Add:
> \paragraph{Risk-informed T\&E strategies for AI-enabled systems.}
> Tailorable Risk-Informed AI Test and Evaluation Strategy (TRAITES) categorizes AI risks by lifecycle phase, problem domain, learning algorithm, and system interactions, guiding appropriate test methods and metrics aligned to where and how AI introduces risk \cite{Lanus_Tailorable_Risk_Informed_AI_Test_Evaluation_Strategy_2025}. For specific AI architectures like RAG-LLMs, Systems Theoretic Process Analysis (STPA) integrated with MBSE identifies archetypal hazard scenarios (malicious use, undetected poor-quality output, over/under-reliance) and maps them to multi-level T\&E approaches \cite{Charnetzki_Hazard_Analysis_RAG_LLM_Systems_2025}. Workflow integration is critical: identical AI capabilities exhibit different performance-risk tradeoffs depending on how they are embedded in human processes, necessitating systems-level assessment rather than isolated model scoring \cite{Szajnfarber_SERC_Perspective_AI4SE_SE4AI_2025}.

**Rationale:**
Provides concrete T\&E frameworks aligned to SE practice, directly supporting the qualification evidence argument.

---

#### **Placement 3: §2.4.3, after new paragraph above**
**Recommendation:**
Add:
> Integrating Responsible AI principles into systems engineering methods requires modifying risk assessments to address AI-specific vulnerabilities, incorporating testable ethics and risk mitigation requirements, and embedding AI governance into existing SE processes \cite{heckle2024responsible}. Trustworthiness measurement itself becomes a lifecycle process: multidimensional metrics tied to concrete activities (explainability, bias mitigation, logging, cybersecurity) inform test strategy and planning rather than serving as pass/fail criteria \cite{Pomales_Measuring_Influencing_Trustworthiness_AI_Enabled_Systems_2025}.

**Rationale:**
Connects governance to SE practice and trustworthiness measurement, closing the loop between policy and operational evaluation.

---

## 7. LLM Costs.bib (9 entries) + Tokenomics.bib (7 entries)

### Strongest 6-8 Papers:
1. **dongLargeLanguageModels2024** - Tokenomics definitions (TTFT, TPOT, throughput)
2. **cottierRisingCostsTraining2024** - Training cost growth trends
3. **Junlin_Wang_2024_Budget_Aware_Reasoning** - Budget-aware evaluation
4. **Abi_Aryan_2023** - Generalization, evaluation, cost trade-offs
5. **Siddharth_Samsi_2023** - Energy costs of LLM inference
6. **Zheng_WenLin_2024_Rho1_Selective_LM** - Selective training on high-value tokens
7. **Bharath_Raj_S_2024_Optimal_Segmentation** - Optimal BPE segmentation
8. **Dong_Liu_2025_SemToken** - Semantic-aware tokenization

### Placement Recommendations:

#### **Placement 1: §2.7 Cost section, Line ~795**
**Current text (line 795):**
> "...Dong et al.\ describe ``tokenomics'' in terms of throughput (tokens/second), cost (e.g., USD per million tokens), and quality-of-experience (QoE) measures"

**Recommendation:**
No change needed—already well cited. Add after line 796:
> These metrics map directly to evaluation feasibility: throughput and latency determine wall-clock time for benchmark runs; TTFT and TPOT shape the practical cost of multi-sample robustness procedures \cite{dongLargeLanguageModels2024}.

**Rationale:**
Reinforces the existing citation and clarifies why tokenomics matters for evaluation.

---

#### **Placement 2: §2.7, Line ~806**
**Current text (lines 805-807):**
> Discusses training cost growth

**Recommendation:**
After line 807, add:
> The amortized cost to train the most compute-intensive models has grown at 2.4× per year since 2016, with frontier models like GPT-4 and Gemini incurring tens of millions of dollars in accelerator chips and staff costs alone \cite{cottierRisingCostsTraining2024}. If this trend continues, the largest training runs will exceed one billion dollars by 2027, concentrating frontier model development among well-funded organizations and motivating cost-reduction strategies such as quantization, selective training, and efficient tokenization.

**Rationale:**
Provides concrete cost growth data and motivates efficiency strategies discussed later.

---

#### **Placement 3: §2.7, Line ~822 (Inference cost discussion)**
**Current text (line 822):**
> "...judges with high percent agreement can still assign vastly different scores."

**Recommendation:**
After line 822, add:
> Budget-aware evaluation frameworks reveal that many reasoning strategies appear superior primarily due to larger compute allocation; when compute is normalized, simpler methods like self-consistency often outperform complex multi-agent or debate-based approaches \cite{Junlin_Wang_2024_Budget_Aware_Reasoning}. This underscores that evaluation conclusions depend on whether performance and cost are reported jointly or in isolation \cite{Abi_Aryan_2023}.

**Rationale:**
Connects inference cost to evaluation reliability—directly relevant to RQ3 and cost-aware qualification.

---

#### **Placement 4: §2.7, NEW subsection after line 827**
**Recommendation:**
Add:

> \paragraph{Token-level efficiency and optimization strategies.}
> Token efficiency directly affects both training and inference costs. Selective Language Modeling (SLM) trains only on high-loss tokens identified via reference model scoring, achieving state-of-the-art math reasoning with 3× fewer training tokens than baseline approaches \cite{Zheng_WenLin_2024_Rho1_Selective_LM}. Optimal BPE segmentation reduces token count compared to greedy segmentation, yielding token-saving percentages and performance benefits especially for smaller and multilingual models \cite{Bharath_Raj_S_2024_Optimal_Segmentation}. Semantic-aware tokenization merges semantically equivalent spans, reducing token count by up to 2.4× and improving efficiency without accuracy loss in long-context tasks \cite{Dong_Liu_2025_SemToken}.

**Rationale:**
Adds actionable efficiency strategies directly relevant to cost-aware evaluation design (RQ3).

---

## Summary Statistics

| Source File | Entries | Selected | Placements |
|-------------|---------|----------|-----------|
| Evaluation Modalities | 12 | 8 | 4 |
| Dataset Creation & Deprecation | 36 | 8 | 4 |
| Dataset Decontamination | 9 | 6 | 2 |
| LLM as a Judge / Eval Methods | 71 | 8 | 3 |
| Domain Specific Benchmarks | 16 | 8 | 2 |
| Governance of AI | 17 | 8 | 3 |
| LLM Costs + Tokenomics | 16 | 8 | 4 |
| **TOTAL** | **177** | **54** | **22** |

---

## Implementation Strategy

1. **Phase 1:** Implement high-confidence placements in §2.5 (MCQ/OSQ/Judge) - Lines 377-550
2. **Phase 2:** Implement §2.6 (Dataset lifecycle) - Lines 635-747
3. **Phase 3:** Implement §2.4 (Governance) - Lines 317-327
4. **Phase 4:** Implement §2.7 (Cost) - Lines 753-830
5. **Phase 5:** Implement §2.4.1 (Domain benchmarks) - Lines 287-296
6. **Review:** Check for over-citation, balance, and flow

---

## Notes on Methodology

- **Minimal edits:** Prefer adding citations over rewriting
- **Max 1 sentence per source** if context requires it for coherence
- **Exact locations** provided using line numbers from chapter2.tex
- **Rationale** explains why each source strengthens specific claims
- **Avoids overclaiming:** Only place sources where they genuinely support existing or implied claims


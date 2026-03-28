---
title: Glossary
---

# Glossary and Terminology Reference

This glossary defines key terms and acronyms used throughout the dissertation and this documentation site. Definitions are drawn from the manuscript chapters, INCOSE standards, and DoD references.

---

## Core Domains

### Systems Engineering (SE)

An interdisciplinary approach and means to enable the full life cycle of successful product, service and enterprise systems. It includes problem discovery and formulation, solution definition and realization, and operational use, sustainment, and disposal. It can be applied to single-problem situations or to the management of multiple interventions in commercial or public enterprises (SEBoK v2.13).

### Model-Based Systems Engineering (MBSE)

A paradigm that uses formalized representations of systems, known as models, to support the performance of systems engineering tasks throughout the system lifecycle, in contrast to legacy document-centric approaches. The Systems Engineering Body of Knowledge (SEBoK) similarly defines MBSE as "a paradigm that uses formalized representations of systems, known as models, to support and facilitate the performance of systems engineering tasks throughout a system's life cycle."

### Digital Thread

An interconnected network of linked lifecycle artifacts that supports querying, transforming, reconciling, and propagating changes across the artifact network. Value is created by maintaining coherence across this network under change, enabling audit, impact analysis, and assurance arguments across the lifecycle.

### Digital Twin

A digital representation of a physical system or process that is continuously updated with real-world data. In the context of this dissertation, digital twins are part of the broader digital engineering ecosystem where AI tools may be embedded.

---

## Evaluation Concepts

### Benchmarking

Evaluating models on standardized datasets and tasks under a defined protocol to (i) compare models, (ii) track progress over time, and (iii) provide selection signals for downstream use. The dissertation surveys the evolution of modern benchmarking, including known failure modes such as data leakage, contamination, and dataset lifecycle challenges.

### SysEngBench

A community-driven, open-source benchmark dataset of 1,144 multiple-choice questions covering systems engineering knowledge areas aligned with the INCOSE Systems Engineering Handbook. This dissertation extends SysEngBench into a paired, multi-format evaluation instrument with controlled MCQ variants (A, B, C, D position rotations) and matched Open Style Questions (OSQs).

### Multiple Choice Question (MCQ)

A constrained-response evaluation format in which the model selects one answer from a fixed set of options. MCQ evaluation measures *recognition competence*: the ability to identify a correct answer among distractors.

### Open Style Question (OSQ)

A free-text evaluation format in which the model must generate and articulate a complete response. OSQ evaluation measures *generative competence*: the ability to produce rubric-satisfying explanations, rationale, and technical content without the scaffolding of provided answer options.

### Distractor

In the MCQ context, a distractor is an incorrect answer option designed to be plausible. The distractor structure of an MCQ can influence measured performance; some items depend on the discriminative power of their distractors rather than the stem alone.

### LLM-as-a-Judge

A rubric-based evaluation methodology in which a language model scores open-ended responses against predefined rubrics and expected answers. Because OSQ responses cannot be assessed via simple string matching, this framework assigns structured, multi-dimensional scores. Judge selection, scoring protocol, and judge reliability validation ensure that OSQ scores function as a defensible measurement instrument.

---

## Evaluation Properties

### Qualification

An evidence-based decision about whether a specific LLM is acceptable for a specified SE use context, under explicit constraints and risk tolerance. A qualification claim is not a general statement that a model is "good"; it is a bounded statement of *intended use* (task class and artifact role), *permitted operating conditions* (inputs, prompt scaffolds, and workflow placement), and *required controls* (evaluation modality, robustness checks, and human oversight).

### Position Bias

A systematic preference for particular answer positions (A, B, C, D) independent of question content. If present, such bias can inflate or deflate apparent model accuracy depending on the distribution of correct answers in the benchmark, confounding cross-model comparisons.

### Robustness

In the context of MCQ evaluation, robustness is supported when (i) accuracy does not differ meaningfully across answer positions (*global invariance*), (ii) within-item correctness is stable across rotations (*item-level invariance*), and (iii) any detected differences are negligible in magnitude as quantified by standardized effect sizes.

### Modality Separation

The empirically measurable gap between MCQ and OSQ performance on semantically aligned questions. Cross-modality separation is category-dependent: where MCQ and OSQ diverge more strongly, MCQ-only results are more likely to overstate deployable competence and OSQ becomes necessary to validate generative adequacy.

### Benchmark Saturation

The condition in which an evaluation instrument no longer differentiates performance because many models reach the scoring ceiling. Saturation reduces discriminative power and can create misleading impressions of equivalence among strong models. The MCQ heatmaps show ceiling effects in easier categories where repeated high-90% to 100% cells compress differences among high-capability models.

### Recognition Competence

Evidence that a model can select correct answers under fixed options and distractors (Tier 1 claim). MCQ outcomes support claims about recognition competence under constrained response form.

### Generative Competence

Evidence that a model can generate rubric-satisfying responses including explanations, rationale, and technical justification (Tier 2 claim). OSQ outcomes support claims about generative competence under rubric-scored evaluation.

---

## Analytical Frameworks

### Evaluation Modality Fusion

The practice of treating MCQ and OSQ as complementary sources of evidence rather than functional equivalents. Because the modalities impose different response constraints, they probe different capabilities and surface different failure modes, even when questions are semantically aligned. The dissertation defines three claim tiers:

- **Tier 1 -- Recognition competence (MCQ).** Evidence supports the ability to select correct answers under fixed options and distractors.
- **Tier 2 -- Generative competence (OSQ).** Evidence supports the ability to generate rubric-satisfying responses.
- **Tier 3 -- Hybrid competence.** Evidence integrates MCQ and OSQ outcomes and includes robustness and feasibility checks to support operational constraints.

### Evaluation Profiles

Minimum evidence bundles required to support a tier of qualification claim for a task family:

- **Profile A (Screening):** MCQ accuracy + MCQ robustness checks (rotation/distractors) with variance reporting.
- **Profile B (Dual-modality qualification):** Profile A + OSQ rubric scoring + multi-judge reliability + score distributions.
- **Profile C (Cost-aware qualification):** Profile B + tokenomics (length distributions, quality yield, and an efficiency frontier).

### Tokenomics

The analysis of inference cost as inseparable from output quality. Models differ not only in how many tokens they emit, but in how reliably those tokens produce rubric-satisfying content. Cost is better understood as *expected tokens per acceptable response* rather than raw token count alone.

### Pareto Frontier

In the quality--token trade space, the set of models for which no alternative achieves both equal or higher mean OSQ score *and* equal or lower mean token consumption. Models on the Pareto frontier represent resource-efficient candidates. Dominated models (below and to the right of the frontier) represent less efficient trade-offs that are difficult to justify absent external constraints.

---

## AI and Machine Learning

### Large Language Model (LLM)

Advanced AI systems trained on large text corpora to model and generate natural language. Modern LLMs typically use transformer architectures and have demonstrated strong performance across a wide range of knowledge and reasoning-style benchmarks.

### Small Language Model (SLM)

A language model with a smaller parameter count than frontier LLMs, often designed for efficiency, on-device deployment, or domain-specific fine-tuning.

### Hallucination

The generation of plausible-sounding but factually false or nonsensical content by a language model. Hallucination is a key failure mode alongside susceptibility to prompt injection, training data contamination, and non-transparent reasoning behaviors.

### Retrieval-Augmented Generation (RAG)

A technique that augments language model generation with retrieved context from external knowledge sources to improve factual grounding and reduce hallucination.

### Supervised Fine-Tuning (SFT)

A training procedure in which a pre-trained language model is further trained on labeled, task-specific data to improve performance on targeted tasks.

---

## Acronyms

| Acronym | Full Form |
|---------|-----------|
| AGI | Artificial General Intelligence |
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| ASOT | Authoritative Source of Truth |
| COCOMO | Constructive Cost Model |
| COSYSMO | Constructive Systems Engineering Cost Model |
| DOD | Department of Defense |
| DODAF | Department of Defense Architecture Framework |
| GenAI | Generative Artificial Intelligence |
| GPU | Graphics Processing Unit |
| GPUaaS | Graphics Processing Unit as a Service |
| GPT | Generative Pre-trained Transformer |
| IDE | Integrated Development Environment |
| INCOSE | International Council on Systems Engineering |
| KDE | Kernel Density Estimation |
| LLM | Large Language Model |
| MBSE | Model-Based Systems Engineering |
| MCQ | Multiple Choice Question |
| ML | Machine Learning |
| NIST | National Institute of Standards and Technology |
| NPS | Naval Postgraduate School |
| OSQ | Open Style Question |
| RAG | Retrieval-Augmented Generation |
| SE | Systems Engineering |
| SEBoK | Systems Engineering Body of Knowledge |
| SERC | Systems Engineering Research Center |
| SFT | Supervised Fine-Tuning |
| SLM | Small Language Model |
| SoS | System of Systems |
| T&E | Test and Evaluation |
| V&V | Verification and Validation |
| VRAM | Video Random-Access Memory |

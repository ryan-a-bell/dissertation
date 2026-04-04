---
title: Source Code
---

<div class="phase-nav" markdown>
<a href="./" class="active">Overview</a>
<a href="phase1_prep/">Phase 1: Prep</a>
<a href="phase2_conversion/">Phase 2: Conversion</a>
<a href="phase3_variants/">Phase 3: Variants</a>
<a href="phase4_inference/">Phase 4: Inference</a>
<a href="phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="phase6_analysis/">Phase 6: Analysis</a>
</div>

# Source Code

This dissertation implements a six-phase modality evaluation pipeline that transforms the SysEngBench dataset through deterministic dataset derivation procedures, evaluates LLMs across both MCQ and OSQ formats under standardized inference controls, applies rubric-based LLM-as-a-Judge scoring for open responses, and performs statistical analyses tailored to each research objective.

![Modality Evaluation Pipeline](modality-evaluation-pipeline.jpg)

---

## Phases

| Phase | Description | Key Output |
|-------|-------------|------------|
| [Phase 1: Benchmark Preparation](phase1_prep/) | Download SysEngBench from HuggingFace, explore data, analyze benchmark composition | 1,144 MCQs with INCOSE category distribution |
| [Phase 2: MCQ to OSQ Conversion](phase2_conversion/) | LLM-based two-stage pipeline to convert MCQs to open-ended questions with rubrics | 845 converted OSQs (73.9% conversion rate) |
| [Phase 3: MCQ Golden Answer Variants](phase3_variants/) | Systematically shift correct answer to positions A-D to control for position bias | Four position-controlled datasets |
| [Phase 4: Model Inference](phase4_inference/) | Run LLM inference across cloud GPU, DoD HPC, and proprietary APIs | Per-model response files for MCQ and OSQ |
| [Phase 5: LLM-as-a-Judge](phase5_llm_as_a_judge/) | Rubric-based scoring with binary, multi-dimensional, and G-Eval approaches | Judged JSONL files across four methodologies |
| [Phase 6: Analysis](phase6_analysis/) | Statistical analysis of position bias, format comparison, and judge consensus | Publication-ready figures and LaTeX tables |

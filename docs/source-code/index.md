# Source Code

## Research Pipeline Overview

This dissertation implements a six-phase modality evaluation pipeline that transforms the SysEngBench dataset through deterministic dataset derivation procedures, evaluates LLMs across both MCQ and OSQ formats under standardized inference controls, applies rubric-based LLM-as-a-Judge scoring for open responses, and performs statistical analyses tailored to each research objective. Each phase produces well-defined artifacts -- datasets, model responses, scoring outputs, and statistical results -- that serve as inputs to subsequent stages.

![Modality Evaluation Pipeline](modality-evaluation-pipeline.jpg)

---

## Phases

<div class="research-grid">

<a href="phase1_prep/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 1: Benchmark Preparation</h3>
<p>Downloads the SysEngBench dataset from HuggingFace, performs initial data exploration, and generates statistical analysis and visualizations of the benchmark composition.</p>
<p><strong>Key output:</strong> 1,144 MCQs in CSV format with INCOSE category distribution analysis</p>
</a>

<a href="phase2_conversion/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 2: MCQ to OSQ Conversion</h3>
<p>Converts Multiple-Choice Questions to Open-ended Short-answer Questions using an LLM-based two-stage pipeline (classification and conversion) with rubric generation.</p>
<p><strong>Key output:</strong> 845 converted OSQs (73.9% conversion rate) with rubrics and grading criteria</p>
</a>

<a href="phase3_variants/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 3: MCQ Golden Answer Variants</h3>
<p>Creates four variants of the SysEngBench MCQ dataset by systematically shifting the correct answer to positions A, B, C, or D to control for position bias in model evaluation.</p>
<p><strong>Key output:</strong> Four position-controlled CSV datasets (1,144 questions each)</p>
</a>

<a href="phase4_inference/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 4: Model Inference</h3>
<p>Runs LLM inference on all benchmark variants using multiple execution environments (cloud GPU, DoD HPC, proprietary APIs) to generate model responses for both MCQ and OSQ formats.</p>
<p><strong>Key output:</strong> Per-model result files with question IDs, responses, and correctness scores</p>
</a>

<a href="phase5_llm_as_a_judge/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 5: LLM-as-a-Judge</h3>
<p>Uses LLM judges to evaluate OSQ responses with academically-validated rubrics through multiple scoring approaches: binary, rubric-based, multi-dimensional, and chain-of-thought (G-Eval).</p>
<p><strong>Key output:</strong> Judged JSONL files with scores across four evaluation methodologies</p>
</a>

<a href="phase6_analysis/" class="research-card" style="text-decoration: none; color: inherit; display: block;">
<h3>Phase 6: Results Processing and Analysis</h3>
<p>Aggregates results from all previous phases and performs comprehensive statistical analysis including position bias detection, MCQ and OSQ analyses, and cross-modality comparison.</p>
<p><strong>Key output:</strong> Statistical test results, publication-ready figures, and LaTeX tables</p>
</a>

</div>

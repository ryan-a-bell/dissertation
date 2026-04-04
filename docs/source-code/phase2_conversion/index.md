---
title: "Phase 2: MCQ to OSQ Conversion"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="../phase1_prep/">Phase 1: Prep</a>
<a href="./" class="active">Phase 2: Conversion</a>
<a href="../phase3_variants/">Phase 3: Variants</a>
<a href="../phase4_inference/">Phase 4: Inference</a>
<a href="../phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="../phase6_analysis/">Phase 6: Analysis</a>
</div>

# Phase 2: MCQ to OSQ Conversion

Converts Multiple-Choice Questions to Open-ended Short-answer Questions using an LLM-based two-stage pipeline (classification and conversion) with rubric generation.

**Key output:** 845 converted OSQs (73.9% conversion rate) with rubrics and grading criteria

---

```
phase2_conversion/
├── 2.1_Converting_MCQ_to_OSQ.ipynb            # Two-stage LLM pipeline (classify + convert)
├── other-prompt-variants.md                   # Alternative prompt designs explored
└── artifacts_mcq2osq/
    ├── sysengbench_osq.csv                    # Full conversion output (all MCQs attempted)
    ├── sysengbench_osq.jsonl                  # JSONL format of conversion output
    ├── sysengbench_osq_filtered.csv           # Filtered to 845 high-confidence OSQs
    └── test.csv                               # HuggingFace-ready copy of filtered dataset
```

- [MCQ to OSQ Conversion](2.1_Converting_MCQ_to_OSQ/) -- Jupyter notebook: classifier prompts, converter pipeline, suitability scoring, and output visualizations
- [Other Prompt Variants](other-prompt-variants/) -- Alternative prompt designs explored during development
- [Conversion Artifacts](artifacts_mcq2osq/) -- Output datasets with CSV previews:
    - [sysengbench_osq.csv](artifacts_mcq2osq/sysengbench_osq/) -- Full output (includes unconverted rows)
    - [sysengbench_osq_filtered.csv](artifacts_mcq2osq/sysengbench_osq_filtered/) -- Filtered to 845 OSQs passing confidence threshold
    - [test.csv](artifacts_mcq2osq/test/) -- Renamed copy uploaded to [HuggingFace](https://huggingface.co/datasets/rabell/SysEngBench-OSQ)

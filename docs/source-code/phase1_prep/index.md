---
title: "Phase 1: Benchmark Preparation"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="./" class="active">Phase 1: Prep</a>
<a href="../phase2_conversion/">Phase 2: Conversion</a>
<a href="../phase3_variants/">Phase 3: Variants</a>
<a href="../phase4_inference/">Phase 4: Inference</a>
<a href="../phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="../phase6_analysis/">Phase 6: Analysis</a>
</div>

# Phase 1: Benchmark Preparation

Downloads the SysEngBench dataset from HuggingFace, performs initial data exploration, and generates statistical analysis and visualizations of the benchmark composition.

**Key output:** 1,144 MCQs in CSV format with INCOSE category distribution analysis

---

```
phase1_prep/
├── 1.1_benchmark_download_and_analysis.ipynb  # Download, explore, and visualize SysEngBench
├── sysengbench.csv                            # Primary benchmark dataset (1,144 MCQs)
└── sysengbench.yaml                           # lm-evaluation-harness task configuration
```

- [Benchmark Download and Analysis](1.1_benchmark_download_and_analysis/) -- Jupyter notebook: downloads dataset from HuggingFace, generates category distribution visualizations
- [SysEngBench Dataset Preview](sysengbench/) -- Interactive table preview of all 1,144 MCQs with INCOSE categories

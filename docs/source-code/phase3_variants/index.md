---
title: "Phase 3: MCQ Golden Answer Variants"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="../phase1_prep/">Phase 1: Prep</a>
<a href="../phase2_conversion/">Phase 2: Conversion</a>
<a href="./" class="active">Phase 3: Variants</a>
<a href="../phase4_inference/">Phase 4: Inference</a>
<a href="../phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="../phase6_analysis/">Phase 6: Analysis</a>
</div>

# Phase 3: MCQ Golden Answer Variants

Creates four variants of the SysEngBench MCQ dataset by systematically shifting the correct answer to positions A, B, C, or D to control for position bias in model evaluation.

**Key output:** Four position-controlled CSV datasets (1,144 questions each)

---

```
phase3_variants/
├── 3.1_MCQ_Shift_Golden.ipynb                 # Rotation logic and verification
├── sysengbench_a.csv                          # Variant A: correct answer always in position A
├── sysengbench_b.csv                          # Variant B: correct answer always in position B
├── sysengbench_c.csv                          # Variant C: correct answer always in position C
└── sysengbench_d.csv                          # Variant D: correct answer always in position D
```

- [MCQ Shift Golden Answer](3.1_MCQ_Shift_Golden/) -- Jupyter notebook: cyclic rotation of answer choices with verification checks
- [Variant A](sysengbench_a/) -- All correct answers shifted to position A
- [Variant B](sysengbench_b/) -- All correct answers shifted to position B
- [Variant C](sysengbench_c/) -- All correct answers shifted to position C
- [Variant D](sysengbench_d/) -- All correct answers shifted to position D

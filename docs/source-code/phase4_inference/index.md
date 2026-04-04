---
title: "Phase 4: Model Inference"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="../phase1_prep/">Phase 1: Prep</a>
<a href="../phase2_conversion/">Phase 2: Conversion</a>
<a href="../phase3_variants/">Phase 3: Variants</a>
<a href="./" class="active">Phase 4: Inference</a>
<a href="../phase5_llm_as_a_judge/">Phase 5: Judging</a>
<a href="../phase6_analysis/">Phase 6: Analysis</a>
</div>

# Phase 4: Model Inference

Runs LLM inference on all benchmark variants using multiple execution environments (cloud GPU, DoD HPC, proprietary APIs) to generate model responses for both MCQ and OSQ formats.

**Key output:** Per-model result files with question IDs, responses, and correctness scores

---

```
phase4_inference/
├── proprietary-manual.ipynb                   # Inference via OpenRouter / proprietary APIs
├── runpod-auto-multiple-pods-cli.ipynb        # Automated multi-pod GPU inference
├── runpod-manual-on-vm.ipynb                  # Manual single-VM setup and execution
├── runpod-manual-remote-control.ipynb         # Remote pod lifecycle management via SDK
├── sysengbench.yaml                           # lm-eval task config (original positions)
├── sysengbench-a.yaml                         # lm-eval task config (variant A)
├── sysengbench-b.yaml                         # lm-eval task config (variant B)
├── sysengbench-c.yaml                         # lm-eval task config (variant C)
├── sysengbench-d.yaml                         # lm-eval task config (variant D)
├── sysengbench-osq.yaml                       # lm-eval task config (open-ended questions)
└── output/                                    # Inference results (19 models x 6 variants)
    ├── sysengbench/                            #   Original MCQ position
    ├── sysengbench-a/                          #   Variant A results
    ├── sysengbench-b/                          #   Variant B results
    ├── sysengbench-c/                          #   Variant C results
    ├── sysengbench-d/                          #   Variant D results
    └── sysengbench-osq/                        #   Open-ended question results
```

- [Proprietary API Inference](proprietary-manual/) -- Notebook: OpenRouter integration, monkey-patched lm-eval adapter, batch evaluations
- [RunPod Automated](runpod-auto-multiple-pods-cli/) -- Notebook: parallel pod orchestration, status tracking, automated result collection
- [RunPod Manual (VM)](runpod-manual-on-vm/) -- Notebook: step-by-step pod setup, Ollama installation, model pulling, lm-eval execution
- [RunPod Remote Control](runpod-manual-remote-control/) -- Notebook: programmatic pod creation, SSH provisioning, SCP result retrieval

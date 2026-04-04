---
title: "Phase 5: LLM-as-a-Judge"
---

<div class="phase-nav" markdown>
<a href="../">Overview</a>
<a href="../phase1_prep/">Phase 1: Prep</a>
<a href="../phase2_conversion/">Phase 2: Conversion</a>
<a href="../phase3_variants/">Phase 3: Variants</a>
<a href="../phase4_inference/">Phase 4: Inference</a>
<a href="./" class="active">Phase 5: Judging</a>
<a href="../phase6_analysis/">Phase 6: Analysis</a>
</div>

# Phase 5: LLM-as-a-Judge

Uses LLM judges to evaluate OSQ responses with academically-validated rubrics through multiple scoring approaches: binary, rubric-based, multi-dimensional, and chain-of-thought (G-Eval).

**Key output:** Judged JSONL files with scores across four evaluation methodologies

---

```
phase5_llm_as_a_judge/
├── llm-judge.ipynb                            # Core judging notebook (prompts, execution, retry)
├── llm-judge-parser.ipynb                     # Post-processing: clean markdown fences from JSON
├── llm-judge-runpod-auto-v2.ipynb             # Automated RunPod-based judging pipeline
├── llm-judge-runpod-manual.ipynb              # Manual 24-step RunPod judging walkthrough
├── llm_judge_automation.py                    # AutomationSession class for orchestration
├── llm-as-a-judge-from-academia.md            # Three academically-grounded judge prompts
└── sysengbench-osq-llm-judge/                 # Judged output files (19 models x 2-3 judges)
    ├── anthropic__claude-sonnet-4.5/
    ├── devstral__24b/
    ├── gemma3__1b/
    ├── gemma3__4b/
    ├── gemma3__12b/
    ├── gemma3__27b/
    ├── google__gemini-2.5-flash/
    ├── llama3.2__1b/
    ├── llama3.2__3b/
    ├── llama3.3__70b/
    ├── llama4__16x17b/
    ├── mistral-large__123b/
    ├── mistral-small3.2__24b/
    ├── mixtral__8x22b/
    ├── openai__gpt-4.1/
    ├── phi3__14b/
    ├── phi3.5__3.8b/
    ├── phi4__14b/
    └── phi4-mini__3.8b/
```

- [LLM Judge](llm-judge/) -- Core notebook: prompt variants (scores-only and scores+justification), parallelized execution, retry logic
- [Judge Parser](llm-judge-parser/) -- Notebook: strips markdown code fences from judge JSON, re-parses fields, validates output
- [RunPod Automated Judging](llm-judge-runpod-auto-v2/) -- Notebook: automated pod orchestration with resumption strategy
- [RunPod Manual Judging](llm-judge-runpod-manual/) -- Notebook: detailed 24-step walkthrough for manual pod-based judging
- [Judge Automation Script](llm_judge_automation/) -- Python module: `AutomationSession` class for SSH-based pod management
- [Academic Rubric Background](llm-as-a-judge-from-academia/) -- Three prompt designs grounded in LLM-Eval, G-Eval, and AlpacaEval literature
- [Judged Outputs](sysengbench-osq-llm-judge/) -- Per-model JSONL files with judge scores across binary, multi-dimensional, and G-Eval approaches

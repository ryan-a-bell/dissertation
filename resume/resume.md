# Ryan Bell

PhD Candidate, Systems Engineering | Naval Postgraduate School, Monterey, CA
ryan.a.bell77@gmail.com | github.com/ryan-a-bell | ryan-a-bell.github.io/dissertation

---

## Summary

Systems engineering researcher and ML engineer specializing in the empirical
evaluation of Large Language Models (LLMs). Built an end-to-end, reproducible
benchmarking platform that orchestrates LLM inference across cloud GPU-as-a-Service,
DoD HPC clusters, and commercial APIs, then scores results with rigorous statistics.
Creator of the SysEngBench benchmark and author of 15+ peer-reviewed publications
on AI for systems engineering.

---

## Technical Skills

- **Languages & Tooling:** Python 3.10+, Bash, LaTeX, YAML, Git, Make
- **ML / LLM Stack:** lm-evaluation-harness, Ollama, vLLM, HuggingFace Transformers
  & Datasets, OpenAI / Anthropic / Google / OpenRouter APIs, LLM-as-a-Judge
- **GPU & HPC Infrastructure:** RunPod GPU-as-a-Service (GPUaaS), NVIDIA H200 / A100 /
  A40 GPUs, CUDA, SLURM batch scheduling, Apptainer/Singularity containers,
  NVIDIA PyTorch container images, DoD HPC (Open OnDemand)
- **Data Science:** pandas, NumPy, SciPy, scikit-learn, matplotlib, seaborn,
  hypothesis testing, effect sizes, bootstrap confidence intervals, inter-rater reliability
- **Engineering Practice:** Pydantic data modeling, pytest, mypy (strict), ruff, black,
  pre-commit, GitHub Actions CI/CD, MkDocs Material documentation

---

## Doctoral Research — Meta-Evaluation of LLM Evaluation Methods

*An Empirical Meta-Evaluation of Language Model Evaluation Methods for Systems
Engineering Using Distractor Sensitivity and Consensus Judging*

- Architected a **6-phase, reproducible evaluation pipeline** (prep, MCQ-to-OSQ
  conversion, distractor variants, inference, LLM-as-a-Judge, statistical analysis)
  covering 1,144 multiple-choice and 845 open-style systems engineering questions.
- Designed and published **6 datasets on HuggingFace** (SysEngBench MCQ, four
  position-rotated distractor variants, and an LLM-converted open-style variant).
- Executed **87,000+ model inferences** across **19 LLMs x 4 position variants** and
  **32,000+ LLM-as-a-Judge rubric scorings** with multi-judge consensus, achieving
  strong inter-judge agreement (Spearman rho = 0.90 on ~16k aligned pairs).
- Quantified MCQ position/distractor sensitivity and MCQ-vs-OSQ divergence using
  **chi-square, Kruskal-Wallis, Friedman, McNemar, and ANOVA** tests; correlation
  (**Pearson/Spearman**); paired tests (**Wilcoxon, t-test**); effect sizes
  (**Cramer's V, Kendall's W, Cohen's d, Hedges' g**); **10,000-iteration bootstrap
  confidence intervals**; and agreement metrics (**Cohen's/Fleiss' kappa, ICC**).
- Produced a task-to-modality routing framework and cost-aware ("tokenomics") model
  selection rules now used as practitioner guidance for LLM adoption in SE workflows.

---

## Selected Engineering Accomplishments

**metaeval — LLM Meta-Evaluation Toolkit (Python package, author)**
- Built an installable, pip-distributable package of **70+ modules across 11
  subpackages** exposing a **12-command CLI** (download, convert, variants, analyze,
  judge, report, eval, ...) for the full evaluation lifecycle.
- Implemented a multi-provider **LLM-as-a-Judge** abstraction (Anthropic, OpenAI,
  OpenRouter, Ollama) behind a unified batch interface, plus a statistics library
  spanning 8+ hypothesis tests, effect sizes, and bootstrap CIs.
- Engineered for production quality: **221 tests across 27 files**, strict mypy typing,
  Pydantic schemas, response caching, ruff/black/pre-commit, and publication-ready
  exporters (300-DPI figures, LaTeX booktabs tables, Markdown reports).

**GPU-as-a-Service & DoD HPC Inference Orchestration**
- Automated dynamic provisioning of **NVIDIA GPU pods on RunPod (GPUaaS)** via a CLI
  multi-pod workflow (primary deployment on **NVIDIA H200**), serving open-weight models
  through Ollama and lm-eval-harness with deterministic, zero-shot evaluation protocols.
- Authored a **DoD HPC SLURM** batch workflow: parameterized `.sbatch` job arrays
  (single-pair, multi-model, multi-task), **Apptainer/Singularity** container builds on
  **NVIDIA PyTorch/CUDA** base images (CUDA 11.7-12.8), offline HuggingFace caching for
  network-isolated nodes, and an **Open OnDemand** web app for job submission.

**Documentation & Automation Platform**
- Built a procedurally generated **MkDocs Material** documentation site with a custom
  Python generator, **GitHub Actions CI/CD** auto-deploy to GitHub Pages, Mermaid/PlantUML
  diagrams, and inline notebook/CSV rendering.

---

## Selected Publications

- **Bell, R.**, Madachy, R., Longshore, R. *Introducing SysEngBench: A Novel Benchmark
  for Assessing Large Language Models in Systems Engineering.* NPS Acquisition Research
  Symposium, 2024. *(lead author)*
- **Bell, R.**, Longshore, R., Madachy, R. *Automating AI Expert Consensus: Feasibility
  of Language Model-Assisted Consensus Methods for Systems Engineering.* Acquisition
  Research Symposium, 2025. *(lead author)*
- **Bell, R.**, Madachy, R., Longshore, R. *Balancing Accuracy and Efficiency: Trade-offs
  in LLM Quantization for the Systems Engineering Domain.* Wiley/INCOSE (submitted).
- Wach, P., **Bell, R.**, et al. *The Cost of Expertise: Performance Trade-offs in LLMs
  for Systems Engineering.* INCOSE International Symposium, vol. 35, 2025. doi:10.1002/iis2.70078
- Papakonstantinou, N., Van Bossuyt, D., **Bell, R.**, et al. *PrivateAIDELPHI: Adopting
  and Adapting Private AI for Risk Assessment of Safety-Critical Systems.* IEEE RAMS,
  2025. doi:10.1109/RAMS48127.2025.10935226
- Madachy, R., **Bell, R.**, Longshore, R. *A Generative AI-driven Systems Engineering
  Maturity and Cost Modeling Framework.* CSER 2025, Springer (in press).

*Additional conference papers and INCOSE International Symposium tutorials (2023-2025)
available on request.*

---

## Education

**PhD, Systems Engineering** — Naval Postgraduate School, Monterey, CA *(in progress)*

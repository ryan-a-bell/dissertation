# Ryan Bell

**Solutions Architect — High-Performance Computing & AI/ML**
Naval Postgraduate School, Monterey, CA
ryan.a.bell77@gmail.com | github.com/ryan-a-bell | ryan-a-bell.github.io/dissertation

---

## Professional Summary

AI/ML solutions architect and systems engineer who designs and delivers end-to-end
machine-learning evaluation platforms spanning **hybrid GPU infrastructure** — cloud
GPU-as-a-Service, **DoD HPC clusters**, and commercial model APIs. Strength in
translating ambiguous capability questions into reference architectures, then proving
them out with reproducible, cost-aware engineering: containerized **NVIDIA**
GPU workloads, SLURM-scheduled batch pipelines, multi-provider LLM orchestration, and
statistically defensible benchmarking at scale. Creator of the SysEngBench benchmark
and author of 15+ peer-reviewed publications on AI for engineering. Comfortable
operating as the technical bridge between research stakeholders, infrastructure teams,
and decision-makers — defining trade spaces, sizing compute, and turning evidence into
adoption guidance.

---

## Core Competencies

| Domain | Technologies & Methods |
|--------|------------------------|
| **HPC & GPU Compute** | NVIDIA H200 / A100 / A40, CUDA 11.7-12.8, SLURM batch scheduling, Apptainer/Singularity, NVIDIA PyTorch container images, Open OnDemand, Lustre/GPFS shared storage, offline/air-gapped node patterns |
| **Cloud / GPUaaS** | RunPod GPU-as-a-Service, dynamic multi-pod provisioning, ephemeral compute orchestration, hybrid cloud-HPC-API topologies |
| **AI/ML Serving & Eval** | lm-evaluation-harness, Ollama, vLLM, HuggingFace Transformers & Datasets, OpenAI / Anthropic / Google / OpenRouter APIs, LLM-as-a-Judge, rubric-based scoring, multi-judge consensus |
| **Solution Engineering** | Python 3.10+, Pydantic data modeling, CLI/SDK design, pytest/mypy(strict)/ruff/black, GitHub Actions CI/CD, Make, reproducible pipelines, response caching |
| **Data Science & Trade Studies** | pandas, NumPy, SciPy, scikit-learn, matplotlib/seaborn; hypothesis testing, effect sizes, bootstrap confidence intervals, inter-rater reliability, cost-performance ("tokenomics") optimization |
| **Architecture & Delivery** | Reference-architecture design, infrastructure portability, capacity/cost sizing, MkDocs documentation systems, stakeholder-facing reporting (LaTeX/PNG/Markdown) |

---

## Architecture & Engineering Experience

### Lead Architect — LLM Meta-Evaluation Platform (Doctoral Research)
*Naval Postgraduate School | 2023 - Present*

Designed and built a production-grade platform for evaluating Large Language Models on
specialized systems-engineering content, framing model qualification as a multi-objective
engineering trade space (accuracy x robustness x cost).

**Hybrid HPC / GPU Infrastructure Architecture**
- Architected a **portable, three-tier compute topology** that runs the same evaluation
  workload across (1) **RunPod GPU-as-a-Service**, (2) **DoD HPC** SLURM clusters, and
  (3) commercial model APIs — letting workloads be placed by cost, data-sensitivity, and
  availability rather than being locked to one environment.
- Engineered automated provisioning of **NVIDIA GPU pods (primary: NVIDIA H200)** on
  RunPod via a multi-pod CLI workflow, serving open-weight models through Ollama and the
  lm-evaluation-harness under deterministic, zero-shot protocols.
- Authored the **DoD HPC delivery path**: parameterized SLURM `.sbatch` job arrays
  (single-pair, multi-model, and multi-task patterns), **Apptainer/Singularity** container
  builds on **NVIDIA PyTorch/CUDA** base images spanning **CUDA 11.7-12.8** for
  cross-site portability, offline HuggingFace model/dataset caching for **network-isolated
  nodes**, and an **Open OnDemand** web app so non-CLI users could submit jobs.
- Standardized environment configuration (shared-filesystem model caches, scratch/`SLURM_TMPDIR`
  staging, env-var-driven offline mode) to make runs reproducible across heterogeneous sites.

**AI/ML Solution & Orchestration**
- Built **metaeval**, a pip-installable Python package — **70+ modules across 11
  subpackages** with a **12-command CLI** — covering the full lifecycle: dataset download,
  MCQ-to-OSQ conversion, distractor-variant generation, multi-environment inference,
  LLM-as-a-Judge scoring, statistical analysis, and publication-ready reporting.
- Designed a **multi-provider LLM-as-a-Judge abstraction** (Anthropic, OpenAI, OpenRouter,
  Ollama) behind a unified batch interface using a factory pattern, so judge models are
  swappable without touching pipeline code.
- Implemented operational hardening for long-running GPU jobs: response **caching**
  (SQLite-backed), retry/session management, structured logging with progress, and
  resumable operations to survive preemption and node failures.

**Scale, Reliability, and Cost Optimization**
- Executed **87,000+ model inferences** across **19 LLMs x 4 position variants** and
  **32,000+ LLM-as-a-Judge rubric scorings** with multi-judge consensus, demonstrating
  strong inter-judge reliability (Spearman rho = 0.90 across ~16,000 aligned pairs).
- Defined a **cost-aware model-selection rule ("tokenomics")**: qualify models against a
  quality threshold, then select the lowest-token (lowest-cost/latency) option on the
  quality-token efficiency frontier — directly applicable to right-sizing inference spend.
- Quantified measurement robustness and modality divergence with a full statistics suite —
  chi-square, Kruskal-Wallis, Friedman, McNemar, ANOVA; Pearson/Spearman correlation;
  Wilcoxon and paired t-tests; effect sizes (Cramer's V, Kendall's W, Cohen's d,
  Hedges' g); **10,000-iteration bootstrap confidence intervals**; and agreement metrics
  (Cohen's/Fleiss' kappa, ICC).

**Stakeholder Deliverables & Adoption Guidance**
- Produced a **task-to-modality routing framework** that maps engineering task families to
  the minimum defensible evaluation evidence — a decision aid for where AI/LLM automation can
  be trusted and how it should be bounded.
- Published **6 datasets on HuggingFace** (MCQ benchmark, four position-rotated distractor
  variants, and an LLM-converted open-style variant) to support reproducibility and reuse.
- Built a procedurally generated **MkDocs Material** documentation site with **GitHub Actions
  CI/CD** auto-deploy to GitHub Pages, Mermaid/PlantUML architecture diagrams, and inline
  notebook/CSV rendering — keeping architecture, code, and results in one navigable system.

### Engineering Quality & Practices
- Delivered the platform to production standards: **221 automated tests across 27 files**,
  strict **mypy** typing, **Pydantic** schema validation for all domain objects, and
  **ruff/black/pre-commit** enforcement.
- Generated publication-ready artifacts programmatically: **300-DPI figures**, **LaTeX
  booktabs tables**, and Markdown reports — eliminating manual hand-off between analysis
  and reporting.

---

## Selected Publications & Talks

- **Bell, R.**, Madachy, R., Longshore, R. *Introducing SysEngBench: A Novel Benchmark for
  Assessing Large Language Models in Systems Engineering.* NPS Acquisition Research
  Symposium, 2024. *(lead author)*
- **Bell, R.**, Madachy, R., Longshore, R. *Balancing Accuracy and Efficiency: Trade-offs in
  LLM Quantization for the Systems Engineering Domain.* Wiley/INCOSE *(submitted)* — empirical
  study of 4/8/16/32-bit quantization vs. accuracy, model size, and deployment cost.
- **Bell, R.**, Longshore, R., Madachy, R. *Automating AI Expert Consensus: Feasibility of
  Language Model-Assisted Consensus Methods for Systems Engineering.* Acquisition Research
  Symposium, 2025. *(lead author)*
- Wach, P., **Bell, R.**, et al. *The Cost of Expertise: Performance Trade-offs in LLMs for
  Systems Engineering.* INCOSE International Symposium, vol. 35, 2025. doi:10.1002/iis2.70078
- Papakonstantinou, N., Van Bossuyt, D., **Bell, R.**, et al. *PrivateAIDELPHI: Adopting and
  Adapting Private AI for Risk Assessment of Safety-Critical Systems.* IEEE RAMS, 2025.
  doi:10.1109/RAMS48127.2025.10935226
- Madachy, R., **Bell, R.**, Longshore, R. *A Generative AI-driven Systems Engineering Maturity
  and Cost Modeling Framework.* CSER 2025, Springer (in press).
- Tutorials: *Developing Custom LLMs for Systems Engineering* and *Open Source System Modeling
  with Python and Generative AI*, INCOSE International Symposium, 2025.

*Full publication list (18 entries, 2023-2025) available on request.*

---

## Education

**PhD, Systems Engineering** — Naval Postgraduate School, Monterey, CA *(in progress)*

---

## Selected Keywords

Solutions Architecture · HPC · GPUaaS · NVIDIA GPU (H200/A100/A40) · CUDA · SLURM ·
Apptainer/Singularity · Containerization · Hybrid Cloud · LLM Evaluation · LLM-as-a-Judge ·
vLLM · Ollama · lm-evaluation-harness · MLOps · Reproducible Pipelines · Cost Optimization ·
Trade Studies · CI/CD · Python · Reference Architecture

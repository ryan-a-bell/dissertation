# Phase 4: Model Inference

## Overview
This phase runs LLM inference on the SysEngBench benchmark variants using multiple execution environments (RunPod, DoD HPC, proprietary APIs). It generates model responses for both MCQ and OSQ formats across different models and configurations.

## Purpose
Execute large-scale LLM evaluation by:
- Running inference on multiple LLM models across benchmark variants
- Supporting diverse compute environments (cloud GPU, HPC clusters, API endpoints)
- Generating structured response datasets for downstream analysis
- Testing both MCQ (multiple-choice) and OSQ (open-ended) formats
- Enabling reproducible model evaluation workflows

## Key Files

### Configuration Files (YAML)
- **`sysengbench.yaml`** - Base MCQ benchmark configuration (original mixed answer positions)
- **`sysengbench-a.yaml`** - MCQ variant with answers in position A
- **`sysengbench-b.yaml`** - MCQ variant with answers in position B
- **`sysengbench-c.yaml`** - MCQ variant with answers in position C
- **`sysengbench-d.yaml`** - MCQ variant with answers in position D
- **`sysengbench-osq.yaml`** - OSQ (open-ended) benchmark configuration

### Notebooks

#### RunPod Execution (Cloud GPU)
- **`runpod-auto-multiple-pods-cli.ipynb`** - Automated multi-pod execution via CLI (primary production method)
- **`runpod-manual-on-vm.ipynb`** - Manual execution on single RunPod VM
- **`runpod-manual-on-vm-fixed (merge with previous).ipynb`** - Fixed/merged version of manual approach
- **`runpod-manual-keep-ollama-running-process.ipynb`** - Persistent Ollama server approach
- **`runpod-manual-remote-control.ipynb`** - Remote control interface for RunPod instances

#### Proprietary API Execution
- **`proprietary-manual.ipynb`** - Manual execution using proprietary/commercial API endpoints (OpenAI, Anthropic, etc.)

### Documentation
- **`runpod-ssh-how-to.docx`** - SSH setup and connection guide for RunPod

### Subdirectories

#### `dodhpc/`
DoD HPC (High-Performance Computing) execution environment with SLURM job scheduling:
- `README.md` - Detailed DoD HPC setup and usage instructions
- `dodhpc-auto.ipynb` - Automated job submission notebook
- `scripts/` - SLURM batch scripts
- `jobs/` - Job submission files
- `tasks/` - Task configuration files
- `containers/` - Singularity/Apptainer container definitions
- `logs/` - Job execution logs
- `output/` - Job output files
- `ood_app/` - Open OnDemand web interface integration

#### `output/`
Inference results organized by benchmark variant:
- `sysengbench/` - Results for original MCQ benchmark
- `sysengbench-a/`, `sysengbench-b/`, `sysengbench-c/`, `sysengbench-d/` - Results for position-controlled MCQ variants
- `sysengbench-osq/` - Results for OSQ benchmark

Each output directory contains subdirectories for different models tested.

#### `test-evals-for-model-selection/`
Initial model selection test runs (smaller sample sizes):
- `anthropic__claude-sonnet-4.5/`
- `google__gemini-2.5-pro/`
- `gpt-4o-mini/`
- `gpt-5.1/`
- `openai__gpt-4.1/`
- `openai__gpt-4o/`

## Configuration & Settings

### YAML Configuration Structure
Each benchmark YAML defines:
- `task` - Task identifier
- `dataset_path` - HuggingFace dataset path
- `test_split` - Data split to use
- `doc_to_text` - Prompt template with placeholders
- `doc_to_target` - Expected answer format
- `generation_kwargs`:
  - `max_gen_toks` - Maximum generation tokens (10 for MCQ, higher for OSQ)
  - `temperature` - Sampling temperature (0.0 for deterministic)
  - `until` - Stop sequences (empty for thinking models)
- `filter_list` - Output parsing filters (regex for MCQ, varies for OSQ)
- `metric_list` - Evaluation metrics (exact_match for MCQ)

### Environment-Specific Settings

#### RunPod
- Requires RunPod API key
- GPU instance configuration (model-dependent)
- Docker container with LM Evaluation Harness
- Network storage for datasets and outputs

#### DoD HPC
- SLURM job scheduler
- Apptainer/Singularity containers
- Partition and resource allocation settings
- Module loading for CUDA/dependencies

#### Proprietary APIs
- API keys for each provider (OpenAI, Anthropic, Google, etc.)
- Rate limiting and quota management
- Model-specific endpoint configurations

## Inputs
- Benchmark datasets from Phase 1-3:
  - `../phase1_prep/sysengbench.csv` - Original MCQ
  - `../phase3_variants/sysengbench_[a-d].csv` - Position variants
  - `../phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv` - OSQ version
- YAML configuration files
- Model specifications (determined during model selection)

## Outputs

### Primary Outputs (in `output/` subdirectories)
For each model and benchmark variant:
- **`results.json`** - Aggregated metrics (accuracy, exact match, etc.)
- **`[model_name]_[benchmark].jsonl`** - Per-question results with:
  - Question ID and text
  - Model response
  - Expected answer
  - Correctness (MCQ) or raw response (OSQ)
  - Generation metadata (tokens, latency, etc.)

### Structure
```
output/
├── sysengbench/
│   ├── model1/
│   │   ├── results.json
│   │   └── model1_sysengbench.jsonl
│   └── model2/
│       └── ...
├── sysengbench-a/
│   └── ...
└── sysengbench-osq/
    └── ...
```

## Usage

### 1. RunPod Automated Execution (Recommended for Scale)
```bash
# See runpod-auto-multiple-pods-cli.ipynb
# Launches multiple GPU instances in parallel
# Automatically distributes models across pods
# Monitors execution and aggregates results
```

### 2. DoD HPC Execution
```bash
# See dodhpc/README.md for detailed instructions
# 1. Load modules
# 2. Build container
# 3. Submit SLURM job
# 4. Monitor via squeue
# 5. Retrieve results from output/
```

### 3. Proprietary API Execution
```bash
# See proprietary-manual.ipynb
# Requires API keys in environment
# Rate-limited, suitable for:
# - Closed-source models (GPT-4, Claude, Gemini)
# - Small-scale testing
# - Models without local deployment options
```

### 4. Manual RunPod VM
```bash
# See runpod-manual-on-vm.ipynb
# For debugging or single-model runs
# SSH into RunPod instance
# Run lm-eval commands manually
```

## Dependencies

### Core
```bash
pip install lm-eval datasets transformers torch pandas
```

### Environment-Specific
- **RunPod**: Docker, RunPod SDK
- **DoD HPC**: Apptainer/Singularity, SLURM utilities
- **APIs**: openai, anthropic, google-generativeai (provider-specific SDKs)

## Execution Workflow

1. **Model Selection** - Use `test-evals-for-model-selection/` to identify candidate models
2. **Configuration** - Ensure YAML files point to correct datasets and have appropriate generation settings
3. **Environment Setup** - Choose execution environment based on:
   - Model availability (open vs. closed source)
   - Compute requirements (model size, throughput needs)
   - Budget constraints
4. **Inference Execution** - Run via chosen environment
5. **Result Collection** - Outputs saved to `output/[benchmark]/[model]/`
6. **Verification** - Check `results.json` for completion and basic metrics

## Notes
- MCQ tasks use strict regex filtering to extract single-letter answers (A/B/C/D)
- OSQ tasks require more flexible parsing (handled in Phase 5)
- Temperature=0.0 for deterministic, reproducible results
- Thinking models (e.g., o1, o3) may require adjusted `max_gen_toks` and empty `until` settings
- RunPod auto-execution is most cost-effective for large-scale open-source model evaluation
- Proprietary APIs recommended only for closed-source models or small test runs
- DoD HPC provides best throughput for large model batches with available allocations
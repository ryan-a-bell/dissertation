# HPC LLM Inference Workflow Guide

This guide walks through setting up and running LLM inference evaluations on an Open OnDemand HPC system.

## Quick Start

```bash
# 1. Check CUDA version
nvidia-smi | grep "CUDA Version"

# 2. Build container
cd containers && ./build_container.sh 12.4

# 3. Pre-pull models (on login node)
./scripts/prepull_models.sh gemma3:4b llama3.2:3b mistral:7b

# 4. Cache HuggingFace datasets
./scripts/cache_hf_datasets.sh

# 5. Submit evaluation job
sbatch jobs/eval_lm_single_pair.sbatch gemma3:4b sysengbench tasks output

# 6. Collect results
python scripts/collect_results.py --format tar.gz
```

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| HPC with SLURM | GPU partition available |
| Apptainer or Singularity | Container runtime |
| Internet on login node | For model/dataset downloads |
| Shared filesystem | For model cache (Lustre/GPFS/NFS) |

---

## Step 1: Environment Setup

### Option A: Using the OOD Form (Recommended)

1. Navigate to **Open OnDemand → Apps → LM-Eval Inference**
2. Select **"Setup Environment"** mode
3. Choose your CUDA version
4. Select initial models to cache
5. Click **Submit**
6. Wait ~30 minutes for setup to complete

### Option B: Command Line Setup

#### 1.1 Check Your CUDA Version

```bash
# On login or compute node
nvidia-smi | grep "CUDA Version"
# Example output: CUDA Version: 12.4
```

#### 1.2 Build the Container

```bash
cd /path/to/dodhpc/containers

# Build for your CUDA version
./build_container.sh 12.4

# Verify
ls -la lm_eval_ollama*.sif
```

**Supported CUDA versions:** 11.7, 11.8, 12.1, 12.2, 12.4, 12.6, 12.8

#### 1.3 Set Up Shared Cache Directories

```bash
# Set cache locations (add to ~/.bashrc)
export SHARED_MODELS="${PROJECT}/shared_models/ollama"
export HF_CACHE="${PROJECT}/shared_models/huggingface"

# Create directories
mkdir -p "$SHARED_MODELS" "$HF_CACHE"
```

---

## Step 2: Pre-Pull Models (Login Node)

Models must be cached before running jobs on network-isolated compute nodes.

### Using the Script

```bash
./scripts/prepull_models.sh \
    gemma3:1b \
    gemma3:4b \
    llama3.2:3b \
    mistral:7b \
    phi4:14b
```

### Using the Python CLI

```bash
# Pull models
python scripts/model_cache.py pull gemma3:4b llama3.2:3b

# List cached models
python scripts/model_cache.py list

# Verify specific model
python scripts/model_cache.py verify gemma3:4b
```

### Model Size Reference

| Model | Size | GPU Memory |
|-------|------|------------|
| gemma3:1b | 0.8 GB | ~2 GB |
| gemma3:4b | 2.7 GB | ~6 GB |
| llama3.2:3b | 2.0 GB | ~5 GB |
| mistral:7b | 4.1 GB | ~10 GB |
| phi4:14b | 8.5 GB | ~18 GB |
| gemma3:12b | 7.3 GB | ~16 GB |
| llama3.3:70b-q4 | 40 GB | ~48 GB |

---

## Step 3: Cache HuggingFace Datasets (Login Node)

Required for offline compute nodes.

### Using the Script

```bash
./scripts/cache_hf_datasets.sh
```

### Using Python

```bash
# Cache specific dataset
python scripts/model_cache.py pull-hf rabell/SysEngBench

# List cached datasets
python scripts/model_cache.py list-hf

# Get environment exports
python scripts/model_cache.py env-hf
```

---

## Step 4: Run Evaluations

### Option A: OOD Form

1. Open **LM-Eval Inference** app
2. Select **"Run Evaluation"** mode
3. Check models (only cached ones available)
4. Check tasks
5. Set resources (GPUs, time)
6. Click **Submit**

### Option B: Direct SBATCH

#### Single Model × Task

```bash
sbatch jobs/eval_lm_single_pair.sbatch \
    gemma3:4b \
    sysengbench \
    /path/to/tasks \
    /path/to/output
```

#### Multiple Tasks, Single Model

```bash
# Edit the script to set your models/tasks, then:
python scripts/submit_eval_jobs_multi_task_single_model.py
```

#### Multiple Models, Single Task

```bash
python scripts/submit_eval_jobs_multi_model_single_task.py
```

### Option C: Jupyter Notebook

1. Launch Jupyter via OOD
2. Open `notebooks/01_submit_inference_jobs.ipynb`
3. Configure models and tasks
4. Run cells to submit and monitor jobs

---

## Step 5: Monitor Jobs

### SLURM Commands

```bash
# Check job status
squeue -u $USER

# View job output
tail -f logs/lm_eval_single-12345.out

# Cancel job
scancel 12345
```

### OOD Dashboard

Navigate to **Open OnDemand → Jobs → Active Jobs**

---

## Step 6: Collect Results

### Package All Results

```bash
# Create tar.gz with all results
python scripts/collect_results.py

# Create ZIP instead
python scripts/collect_results.py --format zip

# Output: lm_eval_results_YYYYMMDD_HHMMSS.tar.gz
```

### Filter Results

```bash
# Only specific model
python scripts/collect_results.py --model gemma

# Only specific task
python scripts/collect_results.py --task sysengbench-osq

# Just print summary (no package)
python scripts/collect_results.py --summary
```

### Output Contents

```
lm_eval_results_20240115_143022.tar.gz
├── summary.csv                    # All metrics in one table
├── gemma3_4b/
│   ├── sysengbench/
│   │   ├── results_2024-01-15.json
│   │   └── samples_sysengbench_2024-01-15.jsonl
│   └── sysengbench-osq/
│       └── ...
├── llama3.2_3b/
│   └── ...
└── ...
```

---

## Directory Structure

```
dodhpc/
├── containers/
│   ├── build_container.sh          # Build container for any CUDA
│   ├── lm_eval_ollama.def          # Default container definition
│   └── lm_eval_ollama.def.template # Parameterized template
│
├── jobs/
│   ├── eval_lm_single_pair.sbatch          # One model × one task
│   ├── eval_lm_multi_task_single_model.sbatch
│   └── eval_lm_multi_model_single_task.sbatch
│
├── scripts/
│   ├── prepull_models.sh           # Pre-pull Ollama models
│   ├── cache_hf_datasets.sh        # Cache HuggingFace datasets
│   ├── setup_venv.sh               # Create venv (alt to container)
│   ├── model_cache.py              # Python cache manager
│   ├── collect_results.py          # Package results for download
│   └── submit_eval_jobs_*.py       # Job submission helpers
│
├── tasks/
│   ├── sysengbench.yaml            # MCQ benchmark
│   ├── sysengbench-osq.yaml        # Open-ended questions
│   └── sysengbench-{a,b,c,d}.yaml  # Position bias variants
│
├── ood_app/
│   └── lm_eval_batch/              # Open OnDemand app
│       ├── form.yml                # Web form configuration
│       ├── manifest.yml            # App metadata
│       ├── submit.yml.erb          # Pre-submit hook
│       ├── template/script.sh.erb  # Job template
│       └── bin/check_status.rb     # Status endpoint
│
├── output/                         # Results (created at runtime)
│   └── {model}/{task}/results.json
│
├── logs/                           # SLURM logs
│
├── INTEGRATION_PATTERNS.md         # Detailed pattern documentation
└── WORKFLOW.md                     # This file
```

---

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `SHARED_MODELS` | Ollama model cache | `$PROJECT/shared_models/ollama` |
| `HF_CACHE` | HuggingFace cache | `$PROJECT/shared_models/huggingface` |
| `HF_DATASETS_OFFLINE` | Disable HF downloads | `1` (in jobs) |
| `OLLAMA_MODELS` | Ollama models dir | Same as `SHARED_MODELS` |

Add to `~/.bashrc`:

```bash
export SHARED_MODELS="${PROJECT}/shared_models/ollama"
export HF_CACHE="${PROJECT}/shared_models/huggingface"
export OLLAMA_MODELS="$SHARED_MODELS"
```

---

## Troubleshooting

### "Model not found in cache"

```bash
# On login node, pull the model
./scripts/prepull_models.sh model_name:tag

# Verify it's cached
python scripts/model_cache.py verify model_name:tag
```

### "Container not found"

```bash
# Build the container
cd containers
./build_container.sh $(nvidia-smi | grep -oP 'CUDA Version: \K[\d.]+' | cut -d. -f1,2)
```

### "CUDA version mismatch"

Check driver compatibility:

| Container CUDA | Min Driver |
|----------------|------------|
| 11.8 | 520+ |
| 12.1 | 530+ |
| 12.4 | 550+ |

Rebuild container for your CUDA version if needed.

### "HuggingFace dataset download failed"

```bash
# On login node (with internet)
./scripts/cache_hf_datasets.sh

# Verify
python scripts/model_cache.py list-hf
```

### Job stuck in PENDING

```bash
# Check why
squeue -u $USER -o "%.10i %.9P %.20j %.8T %.10M %.9l %.6D %R"

# Common reasons:
# - Resources: Not enough GPUs available
# - QOSMaxJobsPerUserLimit: Too many jobs queued
# - Priority: Other jobs have higher priority
```

---

## Task Configuration

Tasks are defined in YAML files in `tasks/`:

```yaml
# sysengbench.yaml
task: sysengbench
dataset_path: rabell/SysEngBench
output_type: generate_until
generation_kwargs:
  until: ["\n"]
  max_gen_toks: 10
  temperature: 0.0
metric_list:
  - metric: exact_match
```

### Available Tasks

| Task | Type | Description |
|------|------|-------------|
| `sysengbench` | MCQ | Multiple choice (A/B/C/D) |
| `sysengbench-osq` | Open | Short answer (~500 tokens) |
| `sysengbench-a` | MCQ | Answer always in position A |
| `sysengbench-b` | MCQ | Answer always in position B |
| `sysengbench-c` | MCQ | Answer always in position C |
| `sysengbench-d` | MCQ | Answer always in position D |

---

## Resource Guidelines

| Model Size | GPUs | Memory | Time (per task) |
|------------|------|--------|-----------------|
| 1-4B | 1 | 16 GB | 1-2 hours |
| 7-14B | 1 | 24 GB | 2-4 hours |
| 27-33B | 2 | 48 GB | 4-6 hours |
| 70B+ | 4 | 96 GB | 6-8 hours |

---

## Next Steps

After collecting results:

1. **Download** the results package via OOD File Browser or `scp`
2. **Analyze** using Phase 5 evaluation scripts
3. **Visualize** accuracy across models and tasks

See `../phase5_analysis/` for analysis notebooks.

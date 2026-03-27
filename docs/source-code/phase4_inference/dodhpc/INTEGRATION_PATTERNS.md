# Open OnDemand HPC Integration Patterns for LM Inference

This document outlines 3 integration patterns for deploying the ephemeral LLM inference pipeline on an open/public HPC system using [Open OnDemand](https://openondemand.org/) (OOD).

## Background: Current DoD HPC Implementation

The existing `dodhpc/` implementation provides:
- **Ephemeral execution model**: Each SLURM job pulls models fresh, evaluates, and cleans up
- **Apptainer/Singularity containers**: Portable execution environment with Ollama + lm_eval
- **Three job patterns**: single-pair, multi-task-single-model, multi-model-single-task
- **Basic OOD app**: Simple form-based job submission (`ood_app/lm_eval_simple/`)

## Target Environment: Open OnDemand HPC

Open OnDemand provides:
- Web-based portal for HPC access
- Interactive apps (Jupyter, RStudio, VS Code)
- Form-based batch job submission
- Job monitoring and file browsing
- Shell access via web terminal

---

## Critical Infrastructure: Environment & Network Considerations

### The Problem

Many HPC systems have **network-isolated compute nodes**:
- **Login/head nodes**: Have internet access (can download models, packages)
- **Compute nodes**: No internet (air-gapped for security)

The current implementation does `ollama pull` inside the SLURM job, which **fails on isolated compute nodes**.

### Solution: Dual-Mode Support

We support two deployment modes that can coexist:

| Mode | Internet on Compute? | Model Strategy | Best For |
|------|---------------------|----------------|----------|
| **Online** | Yes | Pull on-demand in job | Cloud HPC, academic clusters with NAT |
| **Offline** | No | Pre-pull to shared cache | DoD, national labs, secure environments |

---

## Environment Setup Options

### Option A: Container-Based (Recommended)

The Apptainer/Singularity container (`lm_eval_ollama.sif`) bundles all dependencies:
- Ollama runtime
- lm_eval with API support
- Python 3.11 + CUDA support

**Advantages:**
- Fully portable across HPC systems
- No module conflicts
- Reproducible environment

#### Multi-CUDA Version Support

Different HPC systems have different CUDA versions. We support building containers for multiple CUDA versions:

| CUDA Version | HPC Compatibility | Build Command |
|--------------|-------------------|---------------|
| **11.7** | Older systems (pre-2023) | `./build_container.sh 11.7` |
| **11.8** | Legacy systems | `./build_container.sh 11.8` |
| **12.1** | Early 2024 systems | `./build_container.sh 12.1` |
| **12.4** | Most modern HPCs (recommended) | `./build_container.sh 12.4` |
| **12.6** | Late 2024 systems | `./build_container.sh 12.6` |
| **12.8** | Cutting edge | `./build_container.sh 12.8` |

**Check your HPC's CUDA version:**
```bash
# On the HPC login or compute node:
nvidia-smi | grep "CUDA Version"
# Or:
nvcc --version
```

**Build for your CUDA version:**
```bash
cd dodhpc/containers

# Build for CUDA 12.4 (most common modern HPC)
./build_container.sh 12.4

# Or for older systems with CUDA 11.8
./build_container.sh 11.8

# Output: lm_eval_ollama_cuda12.4.sif (or similar)
# Also creates symlink: lm_eval_ollama.sif -> your version
```

**How it works:**
- The build script uses NVIDIA's official PyTorch images as base
- Each image is tested with specific CUDA driver versions
- The `--nv` flag in Apptainer maps host GPU drivers into container
- Container CUDA libraries must be compatible with host drivers

**CUDA Driver Compatibility:**
| Container CUDA | Minimum Driver Version |
|----------------|----------------------|
| 11.7 | 515.43.04+ |
| 11.8 | 520.61.05+ |
| 12.1 | 530.30.02+ |
| 12.4 | 550.54.14+ |
| 12.6 | 560.28.03+ |

**Legacy build (if you just need default):**
```bash
cd dodhpc/containers
apptainer build lm_eval_ollama.sif lm_eval_ollama.def
```

### Option B: Virtual Environment (venv)

For systems where containers are restricted or you need more flexibility:

**Setup script (`scripts/setup_venv.sh`):**
```bash
#!/bin/bash
# Run on login node (requires internet)

set -euo pipefail

VENV_DIR="${1:-$HOME/hpc_lm_eval/venv}"

echo "[INFO] Creating virtual environment at $VENV_DIR"

# Load required modules (adjust for your HPC)
module load python/3.11
module load cuda/12.4

# Create venv
python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# Install packages
pip install --upgrade pip
pip install "lm_eval[api]" ollama==0.3.3

# Install Ollama binary to user space
curl -fsSL https://ollama.com/install.sh | OLLAMA_INSTALL_DIR="$VENV_DIR/ollama" sh

echo "[INFO] Setup complete. Activate with: source $VENV_DIR/bin/activate"
echo "[INFO] Ollama binary at: $VENV_DIR/ollama/bin/ollama"
```

### Option C: Hybrid (Container + Shared venv)

Use container for Ollama + CUDA, but mount a shared venv for lm_eval:
```bash
apptainer exec --nv \
  --bind $HOME/hpc_lm_eval/venv:/opt/venv \
  lm_eval_ollama.sif \
  /opt/venv/bin/lm_eval --help
```

---

## Model Caching for Network-Isolated Compute Nodes

### Architecture: Shared Model Cache

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN NODE                               │
│                      (has internet)                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Model Pre-Pull Script                                   │    │
│  │  $ ./prepull_models.sh gemma3:4b llama3.2:3b mistral:7b │    │
│  └─────────────────────────────────────────────────────────┘    │
│              │                                                   │
│              ▼ Downloads to shared filesystem                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Shared Filesystem (Lustre/GPFS/NFS)                     │    │
│  │  $PROJECT/shared_models/                                 │    │
│  │  └── ollama/                                             │    │
│  │      ├── models/                                         │    │
│  │      │   ├── manifests/registry.ollama.ai/...           │    │
│  │      │   └── blobs/sha256-...                           │    │
│  │      └── model_manifest.json  (tracks what's cached)    │    │
│  └─────────────────────────────────────────────────────────┘    │
│              │                                                   │
│              │ OLLAMA_MODELS env var points here                 │
│              ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    COMPUTE NODES                         │    │
│  │                   (no internet)                          │    │
│  │                                                          │    │
│  │  SLURM Job reads from shared cache:                     │    │
│  │  export OLLAMA_MODELS=$PROJECT/shared_models/ollama     │    │
│  │  ollama serve &   # Finds models in cache               │    │
│  │  ollama run gemma3:4b  # No download needed!            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Model Pre-Pull Script (`scripts/prepull_models.sh`)

```bash
#!/bin/bash
# Run on LOGIN NODE before submitting jobs
# Usage: ./prepull_models.sh model1 model2 model3 ...

set -euo pipefail

# Shared model cache location (adjust for your HPC)
SHARED_MODELS="${SHARED_MODELS:-$PROJECT/shared_models/ollama}"

echo "[INFO] Model cache: $SHARED_MODELS"
mkdir -p "$SHARED_MODELS"

# Point Ollama to shared cache
export OLLAMA_MODELS="$SHARED_MODELS"

# Start Ollama temporarily
ollama serve &
OLLAMA_PID=$!
sleep 10

# Pull each model
for MODEL in "$@"; do
    echo "[INFO] Pulling model: $MODEL"
    if ollama pull "$MODEL"; then
        echo "[OK] $MODEL cached successfully"
    else
        echo "[ERROR] Failed to pull $MODEL"
    fi
done

# Record what's cached
ollama list > "$SHARED_MODELS/model_manifest.txt"
echo "[INFO] Cached models:"
cat "$SHARED_MODELS/model_manifest.txt"

kill $OLLAMA_PID 2>/dev/null || true
echo "[INFO] Pre-pull complete"
```

### Model Cache Manager (`scripts/model_cache.py`)

```python
#!/usr/bin/env python3
"""
Model cache manager for HPC environments.
Handles pre-pulling models on login nodes for offline compute nodes.
"""
import subprocess
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ModelInfo:
    name: str
    size: str
    modified: str
    digest: str

class OllamaModelCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(os.environ.get(
            "SHARED_MODELS",
            Path.home() / "hpc_lm_eval" / "shared_models" / "ollama"
        ))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.cache_dir / "model_manifest.json"

    def _set_env(self):
        """Set OLLAMA_MODELS to use shared cache."""
        os.environ["OLLAMA_MODELS"] = str(self.cache_dir)

    def _start_ollama(self) -> subprocess.Popen:
        """Start Ollama server temporarily."""
        self._set_env()
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        import time
        time.sleep(10)  # Wait for server startup
        return proc

    def list_cached(self) -> List[ModelInfo]:
        """List models in cache."""
        self._set_env()
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True
        )
        models = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 4:
                    models.append(ModelInfo(
                        name=parts[0],
                        digest=parts[1],
                        size=parts[2],
                        modified=parts[3]
                    ))
        return models

    def pull_models(self, models: List[str], force: bool = False) -> dict:
        """
        Pull models to shared cache.
        Run this on LOGIN NODE (with internet).
        """
        proc = self._start_ollama()
        results = {"success": [], "failed": [], "skipped": []}

        try:
            cached = {m.name for m in self.list_cached()}

            for model in models:
                if model in cached and not force:
                    print(f"[SKIP] {model} already cached")
                    results["skipped"].append(model)
                    continue

                print(f"[PULL] {model}...")
                pull_result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=True, text=True
                )
                if pull_result.returncode == 0:
                    print(f"[OK] {model}")
                    results["success"].append(model)
                else:
                    print(f"[FAIL] {model}: {pull_result.stderr}")
                    results["failed"].append(model)

            # Update manifest
            self._update_manifest()

        finally:
            proc.terminate()

        return results

    def _update_manifest(self):
        """Update manifest file with cached models."""
        models = self.list_cached()
        manifest = {
            "cache_dir": str(self.cache_dir),
            "models": [
                {"name": m.name, "size": m.size, "digest": m.digest}
                for m in models
            ]
        }
        self.manifest_file.write_text(json.dumps(manifest, indent=2))

    def verify_model(self, model: str) -> bool:
        """Check if model is available in cache."""
        cached = {m.name for m in self.list_cached()}
        # Handle tag variations (model:latest vs model)
        model_base = model.split(":")[0]
        return model in cached or f"{model_base}:latest" in cached

    def get_env_export(self) -> str:
        """Get export command for SBATCH scripts."""
        return f'export OLLAMA_MODELS="{self.cache_dir}"'


# CLI interface
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage Ollama model cache for HPC")
    parser.add_argument("command", choices=["pull", "list", "verify", "env"])
    parser.add_argument("models", nargs="*", help="Models to pull/verify")
    parser.add_argument("--cache-dir", type=Path, help="Cache directory")
    parser.add_argument("--force", action="store_true", help="Re-pull existing models")

    args = parser.parse_args()
    cache = OllamaModelCache(args.cache_dir)

    if args.command == "pull":
        if not args.models:
            print("Error: specify models to pull")
            exit(1)
        results = cache.pull_models(args.models, force=args.force)
        print(f"\nSummary: {len(results['success'])} pulled, "
              f"{len(results['skipped'])} skipped, {len(results['failed'])} failed")

    elif args.command == "list":
        for m in cache.list_cached():
            print(f"{m.name}\t{m.size}\t{m.digest}")

    elif args.command == "verify":
        for model in args.models:
            status = "OK" if cache.verify_model(model) else "MISSING"
            print(f"{model}: {status}")

    elif args.command == "env":
        print(cache.get_env_export())
```

### Updated SBATCH Template with Dual-Mode Support

The SBATCH scripts need modification to:
1. Use shared model cache via `OLLAMA_MODELS`
2. Skip `ollama pull` if model already cached
3. Fall back to pull if online and model missing

**Updated `eval_lm_single_pair.sbatch`:**
```bash
#!/bin/bash
#SBATCH --job-name=lm_eval_single
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

MODEL="$1"
TASK="$2"
TASKS_DIR="$3"
OUTPUT_ROOT="$4"

# === NEW: Shared model cache support ===
# Set this to your shared filesystem location
SHARED_MODELS="${SHARED_MODELS:-$PROJECT/shared_models/ollama}"

if [[ -d "$SHARED_MODELS" ]]; then
    export OLLAMA_MODELS="$SHARED_MODELS"
    echo "[INFO] Using shared model cache: $OLLAMA_MODELS"
    USE_CACHE=true
else
    echo "[INFO] No shared cache found, will attempt online pull"
    USE_CACHE=false
fi
# === END NEW ===

TASKS_DIR="$(readlink -f "$TASKS_DIR")"
OUTPUT_ROOT="$(readlink -f "$OUTPUT_ROOT")"
CONTAINER_IMAGE="$HOME/hpc_lm_eval/containers/lm_eval_ollama.sif"

mkdir -p logs

SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_${SLURM_JOB_ID}}"
mkdir -p "$SCRATCH_DIR"
cd "$SCRATCH_DIR"

echo "[INFO] Running LM-Eval: MODEL=$MODEL TASK=$TASK"

# Detect container runtime
if command -v apptainer &>/dev/null; then
  CNT=apptainer
elif command -v singularity &>/dev/null; then
  CNT=singularity
else
  echo "[ERROR] No container runtime found" >&2
  exit 1
fi

export MODEL TASK TASKS_DIR OUTPUT_ROOT OLLAMA_MODELS USE_CACHE

$CNT exec --nv \
  ${OLLAMA_MODELS:+--bind "$OLLAMA_MODELS:$OLLAMA_MODELS"} \
  "$CONTAINER_IMAGE" bash -lc '
  set -e

  echo "[INFO] Inside container. MODEL=${MODEL} TASK=${TASK}"
  echo "[INFO] OLLAMA_MODELS=${OLLAMA_MODELS:-not set}"

  mkdir -p tasks output
  cp "${TASKS_DIR}/${TASK}.yaml" tasks/

  # Start Ollama server (will use OLLAMA_MODELS if set)
  echo "[INFO] Starting Ollama server..."
  nohup ollama serve > ollama.log 2>&1 &
  OLLAMA_PID=$!
  sleep 15

  # === NEW: Smart model loading ===
  # Check if model is already available
  if ollama list | grep -q "^${MODEL}"; then
      echo "[INFO] Model ${MODEL} found in cache"
  else
      echo "[INFO] Model ${MODEL} not in cache, attempting pull..."
      if ollama pull "${MODEL}"; then
          echo "[INFO] Model pulled successfully"
      else
          echo "[ERROR] Failed to pull model. Is this node network-isolated?"
          echo "[ERROR] Pre-pull models on login node: ./prepull_models.sh ${MODEL}"
          exit 1
      fi
  fi
  # === END NEW ===

  echo "[INFO] Running lm_eval..."
  lm_eval \
    --model local-chat-completions \
    --model_args "model=${MODEL},base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \
    --include_path ./tasks \
    --tasks "${TASK}" \
    --output "output/${TASK}" \
    --log_samples \
    --num_fewshot 0 \
    --batch_size auto \
    --gen_kwargs temperature=0.0 \
    --apply_chat_template

  echo "[INFO] lm_eval completed."
  kill $OLLAMA_PID 2>/dev/null || true
'

DEST_DIR="${OUTPUT_ROOT}/${MODEL//\//_}/${TASK}"
mkdir -p "$DEST_DIR"

if [ -d "${SCRATCH_DIR}/output/${TASK}" ]; then
  cp -r "${SCRATCH_DIR}/output/${TASK}/." "$DEST_DIR/"
  echo "[INFO] Copied results to: $DEST_DIR"
else
  echo "[WARN] No output found"
fi

echo "[INFO] Done: MODEL=$MODEL TASK=$TASK"
```

---

## Workflow Summary: Setting Up for Network-Isolated HPC

### One-Time Setup (Login Node)

```bash
# 0. Check your HPC's CUDA version first!
nvidia-smi | grep "CUDA Version"
# Example output: "CUDA Version: 12.4"

# 1. Build container for YOUR CUDA version
cd dodhpc/containers
./build_container.sh 12.4   # Use your version here!
# Creates: lm_eval_ollama_cuda12.4.sif
# Also symlinks: lm_eval_ollama.sif -> lm_eval_ollama_cuda12.4.sif

# 2. Create shared model cache directory
export SHARED_MODELS=$PROJECT/shared_models/ollama
mkdir -p $SHARED_MODELS

# 3. Pre-pull all models you'll need
./scripts/prepull_models.sh \
    gemma3:1b gemma3:4b gemma3:12b \
    llama3.2:3b llama3.3:70b-instruct-q4_K_M \
    mistral:7b phi4:14b

# 4. Verify cache
python scripts/model_cache.py list
```

### Job Submission

```bash
# Set cache location (add to .bashrc or job scripts)
export SHARED_MODELS=$PROJECT/shared_models/ollama

# Submit jobs - they'll use cached models
sbatch jobs/eval_lm_single_pair.sbatch gemma3:4b sysengbench tasks output
```

---

## Pattern 1: Interactive Jupyter Control Plane

**Concept**: Use OOD's Jupyter Lab app as an interactive control plane for job submission, monitoring, and result analysis.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Open OnDemand Portal                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Jupyter Lab (Interactive App)               │    │
│  │  ┌─────────────────┐  ┌──────────────────────────────┐  │    │
│  │  │ Control Notebook│  │ Results Analysis Notebook    │  │    │
│  │  │ - Define models │  │ - Load JSON results          │  │    │
│  │  │ - Define tasks  │  │ - Aggregate across models    │  │    │
│  │  │ - Submit jobs   │  │ - Visualize performance      │  │    │
│  │  │ - Monitor queue │  │ - Export to phase5           │  │    │
│  │  └────────┬────────┘  └──────────────────────────────┘  │    │
│  └───────────│──────────────────────────────────────────────┘    │
│              │ subprocess.run(["sbatch", ...])                   │
│              ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SLURM Cluster                         │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │    │
│  │  │ GPU Job │ │ GPU Job │ │ GPU Job │ │ GPU Job │ ...   │    │
│  │  │ Model A │ │ Model B │ │ Model C │ │ Model D │       │    │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │    │
│  │       │           │           │           │             │    │
│  │       └───────────┴───────────┴───────────┘             │    │
│  │                       │                                  │    │
│  │                       ▼                                  │    │
│  │              Shared Filesystem                           │    │
│  │              (output/, logs/)                            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Components

#### 1.1 Job Submission Library (`hpc_inference/submit.py`)

```python
"""
Lightweight job submission library for Jupyter notebooks.
"""
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class JobConfig:
    model: str
    task: str
    partition: str = "gpu"
    gpus: int = 1
    cpus: int = 4
    memory: str = "16G"
    time_limit: str = "04:00:00"

class HPCInferenceSubmitter:
    def __init__(self, base_dir: Path, container_image: Path, shared_models: Path = None):
        self.base_dir = Path(base_dir)
        self.container = Path(container_image)
        self.shared_models = Path(shared_models) if shared_models else None
        self.tasks_dir = self.base_dir / "tasks"
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.base_dir / "logs"
        self.sbatch_template = self.base_dir / "jobs" / "eval_lm_single_pair.sbatch"

    def submit_job(self, config: JobConfig) -> str:
        """Submit a single evaluation job, return job ID."""
        cmd = [
            "sbatch",
            f"--partition={config.partition}",
            f"--gres=gpu:{config.gpus}",
            f"--cpus-per-task={config.cpus}",
            f"--mem={config.memory}",
            f"--time={config.time_limit}",
        ]
        # Pass shared model cache location via environment
        if self.shared_models:
            cmd.append(f"--export=ALL,SHARED_MODELS={self.shared_models}")

        cmd.extend([
            str(self.sbatch_template),
            config.model,
            config.task,
            str(self.tasks_dir),
            str(self.output_dir)
        ])
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Parse job ID from "Submitted batch job 12345"
        job_id = result.stdout.strip().split()[-1]
        return job_id

    def submit_batch(self, configs: List[JobConfig]) -> List[str]:
        """Submit multiple jobs, return list of job IDs."""
        return [self.submit_job(cfg) for cfg in configs]

    def get_job_status(self, job_ids: List[str]) -> dict:
        """Query SLURM for job statuses."""
        cmd = ["squeue", "-j", ",".join(job_ids), "-o", "%i|%T|%M|%R", "--noheader"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        status = {}
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                status[parts[0]] = {
                    "state": parts[1],
                    "time": parts[2],
                    "reason": parts[3] if len(parts) > 3 else ""
                }
        return status

    def collect_results(self, model: str, task: str) -> Optional[dict]:
        """Load results JSON for a completed job."""
        model_safe = model.replace("/", "_")
        result_dir = self.output_dir / model_safe / task
        results_file = list(result_dir.glob("results*.json"))
        if results_file:
            return json.loads(results_file[0].read_text())
        return None
```

#### 1.2 Control Notebook Template (`notebooks/01_submit_inference_jobs.ipynb`)

```python
# Cell 0: Environment Setup (run once)
# This cell handles model pre-pulling for network-isolated compute nodes

import subprocess
import os
from pathlib import Path

# Configuration - adjust for your HPC
USE_CONTAINER = True  # False to use venv instead
SHARED_MODELS = Path(os.environ.get("PROJECT", Path.home())) / "shared_models" / "ollama"

# Ensure model cache exists
SHARED_MODELS.mkdir(parents=True, exist_ok=True)
os.environ["SHARED_MODELS"] = str(SHARED_MODELS)
os.environ["OLLAMA_MODELS"] = str(SHARED_MODELS)

print(f"Model cache: {SHARED_MODELS}")
print(f"Using container: {USE_CONTAINER}")

# Cell 0b: Pre-pull models (run on LOGIN NODE with internet)
# Skip this if models are already cached

MODELS_TO_CACHE = [
    "gemma3:1b", "gemma3:4b", "gemma3:12b",
    "llama3.2:3b", "mistral:7b", "phi4:14b"
]

def prepull_models(models):
    """Pre-pull models to shared cache. Run on login node only."""
    from hpc_inference.model_cache import OllamaModelCache
    cache = OllamaModelCache(SHARED_MODELS)
    return cache.pull_models(models)

# Uncomment to pre-pull (takes a while, do once):
# prepull_results = prepull_models(MODELS_TO_CACHE)
# print(prepull_results)

# Cell 1: Configuration
from hpc_inference.submit import HPCInferenceSubmitter, JobConfig
from pathlib import Path

submitter = HPCInferenceSubmitter(
    base_dir=Path.home() / "hpc_lm_eval",
    container_image=Path.home() / "hpc_lm_eval/containers/lm_eval_ollama.sif",
    shared_models=SHARED_MODELS  # Pass cache location to job scripts
)

# Define evaluation matrix
MODELS = [
    "gemma3:1b", "gemma3:4b", "gemma3:12b",
    "llama3.2:3b", "llama3.3:70b-instruct-q4_K_M",
    "mistral:7b", "phi4:14b"
]

TASKS = ["sysengbench", "sysengbench-a", "sysengbench-b",
         "sysengbench-c", "sysengbench-d", "sysengbench-osq"]

# Cell 2: Submit jobs
configs = [
    JobConfig(model=m, task=t, partition="gpu-shared")
    for m in MODELS for t in TASKS
]

job_ids = submitter.submit_batch(configs)
print(f"Submitted {len(job_ids)} jobs: {job_ids[:5]}...")

# Cell 3: Monitor progress
import time
from IPython.display import clear_output

while True:
    status = submitter.get_job_status(job_ids)
    running = sum(1 for s in status.values() if s["state"] == "RUNNING")
    pending = sum(1 for s in status.values() if s["state"] == "PENDING")
    completed = len(job_ids) - len(status)

    clear_output(wait=True)
    print(f"Running: {running} | Pending: {pending} | Completed: {completed}")

    if completed == len(job_ids):
        print("All jobs complete!")
        break
    time.sleep(30)
```

### Advantages
- **Familiar interface**: Researchers already use Jupyter
- **Full Python ecosystem**: Easy result analysis with pandas, matplotlib
- **Interactive debugging**: Can inspect failures in real-time
- **Version controlled**: Notebooks can be committed to git
- **Reproducible**: Re-run cells to reproduce experiments

### Disadvantages
- Requires active Jupyter session for monitoring
- No persistent job tracking across sessions
- Limited to users comfortable with Python

---

## Pattern 2: Enhanced OOD Form Application

**Concept**: Build a **fully automated** Open OnDemand app that handles everything - container setup, model caching, job submission, and results collection - all through the web form.

### Architecture: All-in-One OOD App

```
┌─────────────────────────────────────────────────────────────────┐
│                    Open OnDemand Portal                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         LM-Eval Inference App (All-in-One Form)          │    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ ▼ Environment Status (auto-detected)                ││    │
│  │  │ ┌─────────────────────────────────────────────────┐││    │
│  │  │ │ Container: ✓ Ready (CUDA 12.4)                  │││    │
│  │  │ │ Model Cache: ✓ 6 models cached                  │││    │
│  │  │ │ CUDA Version: 12.4 (compatible)                 │││    │
│  │  │ │ Network: Offline mode (using cache)             │││    │
│  │  │ └─────────────────────────────────────────────────┘││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ ▼ Job Mode: [Run Evaluation ▼]                      ││    │
│  │  │                                                      ││    │
│  │  │   • Run Evaluation - Submit inference jobs          ││    │
│  │  │   • Setup Environment - Build container + pull models││   │
│  │  │   • Add Models - Pre-pull additional models         ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ ▼ Model Selection (shows cache status)              ││    │
│  │  │ ┌─────────────────────────────────────────────────┐││    │
│  │  │ │ [✓] gemma3:4b      ✓ Cached (2.7GB)            │││    │
│  │  │ │ [✓] llama3.2:3b    ✓ Cached (2.0GB)            │││    │
│  │  │ │ [ ] mistral:7b     ✓ Cached (4.1GB)            │││    │
│  │  │ │ [ ] llama3.3:70b   ⚠ Not cached - will fail!   │││    │
│  │  │ └─────────────────────────────────────────────────┘││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ ▼ Task Selection                                    ││    │
│  │  │ [✓] sysengbench  [✓] sysengbench-osq  [ ] a/b/c/d  ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ ▼ Resources                                         ││    │
│  │  │ Partition: [gpu-shared▼]  GPUs: [1▼]  Time: [4h▼]  ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │           [Submit 12 Jobs] or [Setup First]             │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Auto-detects environment status** - Shows if container exists, what's cached
2. **Multiple job modes** - Setup, Add Models, Run Evaluation
3. **Model cache awareness** - Shows which models are cached, warns on uncached
4. **Validation before submit** - Blocks submission if prerequisites missing
5. **One-click setup** - Builds container and pulls models automatically

### Implementation Components

#### 2.1 Form Configuration with Environment Detection (`ood_app/lm_eval_batch/form.yml`)

```yaml
---
title: "LM Evaluation Inference"
cluster: "your_cluster"
description: |
  Run LLM evaluations on SysEngBench. First-time users: select "Setup Environment" mode.

# Form JavaScript for dynamic behavior
form_js: |
  // Check environment status on page load
  async function checkEnvironment() {
    const statusDiv = document.getElementById('env-status');
    const response = await fetch('/pun/sys/lm_eval/check_status');
    const status = await response.json();

    // Update status display
    statusDiv.innerHTML = formatStatus(status);

    // Disable uncached models if offline
    if (status.network_mode === 'offline') {
      document.querySelectorAll('.model-option').forEach(opt => {
        if (!status.cached_models.includes(opt.value)) {
          opt.disabled = true;
          opt.parentElement.classList.add('uncached-warning');
        }
      });
    }
  }

  // Show/hide form sections based on job mode
  document.getElementById('job_mode').addEventListener('change', function() {
    const mode = this.value;
    document.getElementById('eval-options').style.display =
      mode === 'evaluate' ? 'block' : 'none';
    document.getElementById('setup-options').style.display =
      mode === 'setup' ? 'block' : 'none';
    document.getElementById('add-models-options').style.display =
      mode === 'add_models' ? 'block' : 'none';
  });

attributes:
  # ===== Job Mode Selection =====
  job_mode:
    widget: "select"
    label: "Job Mode"
    value: "evaluate"
    options:
      - ["Run Evaluation", "evaluate"]
      - ["Setup Environment (first time)", "setup"]
      - ["Add Models to Cache", "add_models"]
    help: |
      - **Run Evaluation**: Submit inference jobs (requires setup complete)
      - **Setup Environment**: Build container and pull initial models
      - **Add Models**: Pre-pull additional models to cache

  # ===== Setup Mode Options =====
  cuda_version:
    widget: "select"
    label: "CUDA Version (for container build)"
    value: "12.4"
    options:
      - ["CUDA 12.4 (recommended)", "12.4"]
      - ["CUDA 12.6", "12.6"]
      - ["CUDA 12.1", "12.1"]
      - ["CUDA 11.8 (legacy)", "11.8"]
    help: "Run 'nvidia-smi' on login node to check your CUDA version"

  initial_models:
    widget: "check_box"
    label: "Models to pre-pull during setup"
    options:
      - ["Gemma3 1B (0.8GB)", "gemma3:1b"]
      - ["Gemma3 4B (2.7GB)", "gemma3:4b"]
      - ["Llama 3.2 3B (2.0GB)", "llama3.2:3b"]
      - ["Mistral 7B (4.1GB)", "mistral:7b"]
      - ["Phi4 14B (8.5GB)", "phi4:14b"]
    help: "Select models to cache. Larger models need more GPU memory."

  # ===== Add Models Mode Options =====
  additional_models:
    widget: "check_box"
    label: "Additional models to pull"
    options:
      - ["Gemma3 12B (7.3GB)", "gemma3:12b"]
      - ["Gemma3 27B (15GB)", "gemma3:27b"]
      - ["Llama 3.3 70B Q4 (40GB)", "llama3.3:70b-instruct-q4_K_M"]
      - ["Mixtral 8x7B (26GB)", "mixtral:8x7b"]
      - ["DeepSeek Coder 33B (19GB)", "deepseek-coder:33b"]

  # ===== Evaluation Mode Options =====
  models:
    widget: "check_box"
    label: "Models to evaluate"
    # Dynamic options populated by JavaScript based on cache
    options:
      - ["gemma3:1b", "gemma3:1b"]
      - ["gemma3:4b", "gemma3:4b"]
      - ["llama3.2:3b", "llama3.2:3b"]
      - ["mistral:7b", "mistral:7b"]
      - ["phi4:14b", "phi4:14b"]

  tasks:
    widget: "check_box"
    label: "Benchmark tasks"
    value: ["sysengbench", "sysengbench-osq"]
    options:
      - ["SysEngBench MCQ", "sysengbench"]
      - ["SysEngBench OSQ (open-ended)", "sysengbench-osq"]
      - ["Position Bias A", "sysengbench-a"]
      - ["Position Bias B", "sysengbench-b"]
      - ["Position Bias C", "sysengbench-c"]
      - ["Position Bias D", "sysengbench-d"]

  bc_queue:
    widget: "select"
    label: "Partition"
    options:
      - ["GPU Shared", "gpu-shared"]
      - ["GPU Full Node", "gpu"]
      - ["GPU Debug (testing)", "gpu-debug"]

  bc_num_slots:
    widget: "number_field"
    label: "GPUs per job"
    value: 1
    min: 1
    max: 4

  bc_num_hours:
    widget: "number_field"
    label: "Wall time (hours)"
    value: 4
    min: 1
    max: 24

  notify_email:
    widget: "email_field"
    label: "Email on completion (optional)"
    required: false

# Form layout - sections shown/hidden by JavaScript
form:
  - job_mode
  - cuda_version
  - initial_models
  - additional_models
  - models
  - tasks
  - bc_queue
  - bc_num_slots
  - bc_num_hours
  - notify_email
```

#### 2.2 Multi-Mode Job Script (`ood_app/lm_eval_batch/template/script.sh.erb`)

```bash
#!/bin/bash
<% if job_mode == "setup" %>
#SBATCH --job-name=lm_eval_setup
#SBATCH --partition=<%= bc_queue %>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
<% elsif job_mode == "add_models" %>
#SBATCH --job-name=lm_eval_addmodels
#SBATCH --partition=<%= bc_queue %>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
<% else %>
#SBATCH --job-name=lm_eval_batch
#SBATCH --partition=<%= bc_queue %>
#SBATCH --gres=gpu:<%= bc_num_slots %>
#SBATCH --cpus-per-task=4
#SBATCH --mem=<%= bc_num_slots.to_i * 16 %>G
#SBATCH --time=<%= bc_num_hours %>:00:00
#SBATCH --array=1-<%= job_count %>
<% end %>
#SBATCH --output=<%= output_dir %>/logs/%x-%j.out
<% if notify_email.present? %>
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=<%= notify_email %>
<% end %>

set -euo pipefail

# Common paths
BASE_DIR="$HOME/hpc_lm_eval"
CONTAINER_DIR="$BASE_DIR/containers"
SHARED_MODELS="${SHARED_MODELS:-$PROJECT/shared_models/ollama}"
TASKS_DIR="$BASE_DIR/tasks"
OUTPUT_DIR="$BASE_DIR/output"

export OLLAMA_MODELS="$SHARED_MODELS"

<% if job_mode == "setup" %>
#==============================================================================
# SETUP MODE: Build container and pre-pull initial models
#==============================================================================
echo "=========================================="
echo "LM-Eval Environment Setup"
echo "=========================================="

# Create directory structure
mkdir -p "$CONTAINER_DIR" "$SHARED_MODELS" "$TASKS_DIR" "$OUTPUT_DIR" logs

# Step 1: Build container
echo "[1/3] Building container for CUDA <%= cuda_version %>..."
cd "$CONTAINER_DIR"

# Download build script if needed
if [[ ! -f build_container.sh ]]; then
    echo "[INFO] Downloading build scripts..."
    # Copy from shared install location or git
    cp /shared/apps/lm_eval/containers/* . 2>/dev/null || \
    curl -sL https://raw.githubusercontent.com/your-repo/dodhpc/containers/build_container.sh -o build_container.sh
    chmod +x build_container.sh
fi

./build_container.sh <%= cuda_version %>
CONTAINER_IMAGE="$CONTAINER_DIR/lm_eval_ollama_cuda<%= cuda_version %>.sif"

# Step 2: Pre-pull models
echo "[2/3] Pre-pulling models to shared cache..."
echo "[INFO] Cache location: $SHARED_MODELS"

# Start Ollama inside container to pull models
MODELS_TO_PULL="<%= initial_models.join(' ') %>"

if command -v apptainer &>/dev/null; then CNT=apptainer; else CNT=singularity; fi

$CNT exec --nv \
    --bind "$SHARED_MODELS:$SHARED_MODELS" \
    "$CONTAINER_IMAGE" bash -c "
    export OLLAMA_MODELS='$SHARED_MODELS'

    # Start Ollama
    ollama serve &
    sleep 15

    # Pull each model
    for MODEL in $MODELS_TO_PULL; do
        echo \"[PULL] \$MODEL\"
        ollama pull \"\$MODEL\" || echo \"[WARN] Failed to pull \$MODEL\"
    done

    # List what's cached
    echo ''
    echo 'Cached models:'
    ollama list

    pkill ollama || true
"

# Step 3: Copy task YAML files
echo "[3/3] Setting up task configurations..."
cp /shared/apps/lm_eval/tasks/*.yaml "$TASKS_DIR/" 2>/dev/null || \
    echo "[INFO] Copy task YAMLs manually to $TASKS_DIR"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "Container: $CONTAINER_IMAGE"
echo "Model Cache: $SHARED_MODELS"
echo "Tasks Dir: $TASKS_DIR"
echo ""
echo "You can now run evaluations from the form."

<% elsif job_mode == "add_models" %>
#==============================================================================
# ADD MODELS MODE: Pre-pull additional models to cache
#==============================================================================
echo "=========================================="
echo "Adding Models to Cache"
echo "=========================================="

CONTAINER_IMAGE="$CONTAINER_DIR/lm_eval_ollama.sif"
MODELS_TO_PULL="<%= additional_models.join(' ') %>"

if [[ ! -f "$CONTAINER_IMAGE" ]]; then
    echo "[ERROR] Container not found. Run Setup mode first."
    exit 1
fi

if command -v apptainer &>/dev/null; then CNT=apptainer; else CNT=singularity; fi

$CNT exec --nv \
    --bind "$SHARED_MODELS:$SHARED_MODELS" \
    "$CONTAINER_IMAGE" bash -c "
    export OLLAMA_MODELS='$SHARED_MODELS'

    ollama serve &
    sleep 15

    for MODEL in $MODELS_TO_PULL; do
        echo \"[PULL] \$MODEL\"
        ollama pull \"\$MODEL\" || echo \"[WARN] Failed to pull \$MODEL\"
    done

    echo ''
    echo 'All cached models:'
    ollama list

    pkill ollama || true
"

echo "[INFO] Model cache updated."

<% else %>
#==============================================================================
# EVALUATE MODE: Run inference jobs
#==============================================================================

# Read job config for this array task
CONFIG_FILE="<%= output_dir %>/batch_config.txt"
LINE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$CONFIG_FILE")
MODEL=$(echo "$LINE" | cut -d'|' -f1)
TASK=$(echo "$LINE" | cut -d'|' -f2)

echo "[INFO] Evaluation job: MODEL=$MODEL TASK=$TASK"

CONTAINER_IMAGE="$CONTAINER_DIR/lm_eval_ollama.sif"
SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_${SLURM_JOB_ID}}"
mkdir -p "$SCRATCH_DIR"
cd "$SCRATCH_DIR"

if command -v apptainer &>/dev/null; then CNT=apptainer; else CNT=singularity; fi

$CNT exec --nv \
    --bind "$SHARED_MODELS:$SHARED_MODELS" \
    --bind "$TASKS_DIR:$TASKS_DIR" \
    "$CONTAINER_IMAGE" bash -c "
    set -e
    export OLLAMA_MODELS='$SHARED_MODELS'

    mkdir -p tasks output
    cp '$TASKS_DIR/$TASK.yaml' tasks/

    # Start Ollama with cached models
    ollama serve &
    sleep 15

    # Verify model is cached
    if ! ollama list | grep -q '$MODEL'; then
        echo '[ERROR] Model $MODEL not in cache!'
        echo '[ERROR] Run Add Models mode first.'
        exit 1
    fi

    # Run evaluation
    lm_eval \\
        --model local-chat-completions \\
        --model_args 'model=$MODEL,base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1' \\
        --include_path ./tasks \\
        --tasks '$TASK' \\
        --output 'output/$TASK' \\
        --log_samples \\
        --num_fewshot 0 \\
        --batch_size auto \\
        --gen_kwargs temperature=0.0 \\
        --apply_chat_template

    pkill ollama || true
"

# Copy results
DEST_DIR="$OUTPUT_DIR/${MODEL//\//_}/${TASK}"
mkdir -p "$DEST_DIR"
cp -r "$SCRATCH_DIR/output/$TASK/." "$DEST_DIR/" 2>/dev/null || true

echo "[INFO] Results saved to: $DEST_DIR"
<% end %>
```

#### 2.3 Pre-Submit Hook: Generate Job Config (`ood_app/lm_eval_batch/submit.yml.erb`)

```yaml
---
batch_connect:
  template: "basic"

script:
  native:
<% if job_mode == "evaluate" %>
    # Generate job array configuration
    - |
      CONFIG_FILE="<%= output_dir %>/batch_config.txt"
      mkdir -p "<%= output_dir %>"
      rm -f "$CONFIG_FILE"
      <% models.each do |model| %>
      <% tasks.each do |task| %>
      echo "<%= model %>|<%= task %>" >> "$CONFIG_FILE"
      <% end %>
      <% end %>
      echo "[INFO] Generated config with $(wc -l < $CONFIG_FILE) jobs"
<% end %>
```

#### 2.4 Status Check Endpoint (`ood_app/lm_eval_batch/bin/check_status.rb`)

This Ruby script provides the `/check_status` endpoint for the form JavaScript:

```ruby
#!/usr/bin/env ruby
# Returns JSON with environment status for the OOD form

require 'json'

base_dir = File.expand_path("~/hpc_lm_eval")
container_dir = "#{base_dir}/containers"
shared_models = ENV['SHARED_MODELS'] || "#{ENV['PROJECT']}/shared_models/ollama"

status = {
  container_exists: false,
  container_cuda_version: nil,
  cached_models: [],
  network_mode: 'unknown',
  setup_complete: false
}

# Check container
container_files = Dir.glob("#{container_dir}/lm_eval_ollama*.sif")
if container_files.any?
  status[:container_exists] = true
  # Extract CUDA version from filename
  if match = container_files.first.match(/cuda(\d+\.\d+)/)
    status[:container_cuda_version] = match[1]
  end
end

# Check cached models
manifest_file = "#{shared_models}/model_manifest.txt"
if File.exist?(manifest_file)
  status[:cached_models] = File.readlines(manifest_file)
    .drop(1)  # Skip header
    .map { |line| line.split.first }
    .compact
end

# Detect network mode (simplified check)
status[:network_mode] = system("ping -c 1 -W 2 ollama.ai > /dev/null 2>&1") ? 'online' : 'offline'

# Setup complete if container exists and at least one model cached
status[:setup_complete] = status[:container_exists] && status[:cached_models].any?

puts JSON.pretty_generate(status)
```

### User Workflow with All-in-One Form

**First-time user:**
1. Open LM-Eval app in Open OnDemand
2. Form shows "Environment Status: Not configured"
3. Select **"Setup Environment"** mode
4. Choose CUDA version, select initial models
5. Click Submit → Runs setup job
6. Wait ~30 min for container build + model pulls
7. Return to form → Status shows "Ready"

**Running evaluations:**
1. Open LM-Eval app
2. Form shows cached models with ✓ indicators
3. Select **"Run Evaluation"** mode
4. Check models (only cached ones enabled)
5. Check tasks
6. Click Submit → Jobs queued
7. Check OOD "Active Jobs" for progress

**Adding more models:**
1. Select **"Add Models"** mode
2. Check additional models to pull
3. Submit → Pulls to shared cache
4. New models now available for evaluation

### Advantages
- **Zero CLI required**: Everything through web form
- **Auto-detection**: Shows environment status, cached models
- **Validation**: Prevents submission with uncached models on offline nodes
- **Three modes**: Setup, Add Models, Evaluate - covers full lifecycle
- **Job arrays**: Efficient SLURM resource usage

### Disadvantages
- More complex OOD app to develop and maintain
- Requires OOD admin access to deploy
- Setup mode needs internet on login node (or pre-staged container)

---

## Pattern 3: Workflow Orchestration with Nextflow/Snakemake

**Concept**: Use a workflow manager to orchestrate the inference pipeline with dependency tracking, automatic retries, and provenance.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Open OnDemand Portal                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Shell / Jupyter (Workflow Launcher)              │    │
│  │                                                          │    │
│  │  $ nextflow run lm_inference.nf \                       │    │
│  │      --models "gemma3:4b,llama3.2:3b" \                 │    │
│  │      --tasks "sysengbench,sysengbench-osq" \            │    │
│  │      -profile slurm_gpu                                  │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│              │                                                   │
│              ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Nextflow Orchestrator                        │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ Workflow DAG                                        ││    │
│  │  │                                                      ││    │
│  │  │  ┌──────────┐                                       ││    │
│  │  │  │ Build    │ (if container missing)                ││    │
│  │  │  │ Container│                                       ││    │
│  │  │  └────┬─────┘                                       ││    │
│  │  │       │                                              ││    │
│  │  │       ▼                                              ││    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          ││    │
│  │  │  │ Evaluate │  │ Evaluate │  │ Evaluate │  ...     ││    │
│  │  │  │ gemma3:4b│  │ llama3.2 │  │ mistral  │          ││    │
│  │  │  │ syseng   │  │ syseng   │  │ syseng   │          ││    │
│  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          ││    │
│  │  │       │             │             │                 ││    │
│  │  │       └─────────────┼─────────────┘                 ││    │
│  │  │                     ▼                               ││    │
│  │  │              ┌──────────────┐                       ││    │
│  │  │              │  Aggregate   │                       ││    │
│  │  │              │   Results    │                       ││    │
│  │  │              └──────────────┘                       ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  └──────────────────────────────────────────────────────────┘    │
│              │                                                   │
│              ▼ SLURM Jobs (managed by Nextflow)                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │   Nextflow manages:                                      │    │
│  │   - Job submission                                       │    │
│  │   - Dependency resolution                                │    │
│  │   - Automatic retries on failure                         │    │
│  │   - Resource scaling                                     │    │
│  │   - Result caching (resume from failures)                │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Components

#### 3.1 Nextflow Workflow (`workflows/lm_inference.nf`)

```nextflow
#!/usr/bin/env nextflow
nextflow.enable.dsl=2

// Parameters
params.models = "gemma3:4b,llama3.2:3b,mistral:7b"
params.tasks = "sysengbench,sysengbench-osq"
params.tasks_dir = "${HOME}/hpc_lm_eval/tasks"
params.output_dir = "${HOME}/hpc_lm_eval/output"
params.container = "${HOME}/hpc_lm_eval/containers/lm_eval_ollama.sif"

// Parse model and task lists
def models = params.models.tokenize(',')
def tasks = params.tasks.tokenize(',')

// Create channel of all (model, task) pairs
Channel
    .fromList(models)
    .combine(Channel.fromList(tasks))
    .set { model_task_pairs }

// Main evaluation process
process evaluate {
    tag "${model}_${task}"

    container "${params.container}"
    containerOptions '--nv'

    cpus 4
    memory '16 GB'
    time '4h'

    // Retry on transient failures
    errorStrategy { task.attempt <= 3 ? 'retry' : 'finish' }
    maxRetries 3

    input:
    tuple val(model), val(task)

    output:
    tuple val(model), val(task), path("results/*"), emit: results

    script:
    """
    # Setup
    mkdir -p tasks results
    cp ${params.tasks_dir}/${task}.yaml tasks/

    # Start Ollama
    nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
    OLLAMA_PID=\$!
    sleep 15

    # Pull model and evaluate
    ollama pull ${model}

    lm_eval \\
        --model local-chat-completions \\
        --model_args "model=${model},base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \\
        --include_path ./tasks \\
        --tasks ${task} \\
        --output results/ \\
        --log_samples \\
        --num_fewshot 0 \\
        --batch_size auto \\
        --gen_kwargs temperature=0.0 \\
        --apply_chat_template

    kill \$OLLAMA_PID 2>/dev/null || true
    """

    publishDir "${params.output_dir}/${model.replace('/', '_')}/${task}", mode: 'copy'
}

// Aggregation process
process aggregate_results {
    cpus 1
    memory '4 GB'
    time '30m'

    input:
    path(all_results)

    output:
    path("aggregated_results.json")
    path("summary_table.csv")

    script:
    """
    python3 << 'EOF'
import json
import csv
from pathlib import Path
import glob

results = []
for f in glob.glob("**/results*.json", recursive=True):
    with open(f) as fp:
        data = json.load(fp)
        results.append(data)

# Write aggregated JSON
with open("aggregated_results.json", "w") as fp:
    json.dump(results, fp, indent=2)

# Write summary CSV
with open("summary_table.csv", "w", newline="") as fp:
    writer = csv.writer(fp)
    writer.writerow(["model", "task", "metric", "value"])
    for r in results:
        for task_name, task_results in r.get("results", {}).items():
            for metric, value in task_results.items():
                if isinstance(value, (int, float)):
                    writer.writerow([r.get("model", "unknown"), task_name, metric, value])
EOF
    """

    publishDir "${params.output_dir}/aggregated", mode: 'copy'
}

// Workflow
workflow {
    // Run evaluations
    evaluate(model_task_pairs)

    // Aggregate all results
    aggregate_results(evaluate.out.results.collect())
}
```

#### 3.2 SLURM Profile Configuration (`nextflow.config`)

```groovy
// Nextflow configuration for SLURM HPC

profiles {
    slurm_gpu {
        process {
            executor = 'slurm'
            queue = 'gpu-shared'

            // Default resources
            cpus = 4
            memory = '16 GB'
            time = '4h'

            // GPU allocation
            clusterOptions = '--gres=gpu:1'

            // Use Apptainer/Singularity
            container = params.container
            containerOptions = '--nv'
        }

        singularity {
            enabled = true
            autoMounts = true
            runOptions = '--nv'
        }

        executor {
            queueSize = 50          // Max concurrent jobs
            submitRateLimit = '10/1min'  // Rate limit submissions
            pollInterval = '30 sec'
        }
    }

    slurm_gpu_large {
        // Inherits from slurm_gpu
        process {
            executor = 'slurm'
            queue = 'gpu'
            memory = '64 GB'
            clusterOptions = '--gres=gpu:4'
        }
    }

    local {
        // For testing without SLURM
        process {
            executor = 'local'
            cpus = 4
            memory = '16 GB'
        }
    }
}

// Execution reports
report {
    enabled = true
    file = "${params.output_dir}/reports/execution_report.html"
}

timeline {
    enabled = true
    file = "${params.output_dir}/reports/timeline.html"
}

dag {
    enabled = true
    file = "${params.output_dir}/reports/dag.svg"
}

// Resume from cache on re-run
resume = true
```

#### 3.3 Alternative: Snakemake Workflow (`workflows/Snakefile`)

```python
# Snakemake workflow for LM inference

configfile: "config.yaml"

# Extract models and tasks from config
MODELS = config.get("models", ["gemma3:4b", "llama3.2:3b"])
TASKS = config.get("tasks", ["sysengbench", "sysengbench-osq"])

# Output directory
OUTPUT_DIR = config.get("output_dir", "output")

# Container image
CONTAINER = config.get("container", "containers/lm_eval_ollama.sif")

# Final target: aggregated results
rule all:
    input:
        expand(f"{OUTPUT_DIR}/{{model}}/{{task}}/results.json",
               model=[m.replace("/", "_") for m in MODELS],
               task=TASKS),
        f"{OUTPUT_DIR}/aggregated/summary.csv"

# Evaluate a single (model, task) pair
rule evaluate:
    output:
        results = f"{OUTPUT_DIR}/{{model}}/{{task}}/results.json",
        samples = f"{OUTPUT_DIR}/{{model}}/{{task}}/samples.jsonl"
    params:
        model = lambda wc: wc.model.replace("_", "/"),
        task = "{task}",
        tasks_dir = config.get("tasks_dir", "tasks")
    resources:
        gpu = 1,
        mem_mb = 16000,
        time = "4:00:00"
    singularity:
        CONTAINER
    shell:
        """
        mkdir -p tasks output
        cp {params.tasks_dir}/{params.task}.yaml tasks/

        nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
        OLLAMA_PID=$!
        sleep 15

        ollama pull {params.model}

        lm_eval \
            --model local-chat-completions \
            --model_args "model={params.model},base_url=http://localhost:11434/v1/chat/completions,num_concurrent=1" \
            --include_path ./tasks \
            --tasks {params.task} \
            --output output/ \
            --log_samples \
            --num_fewshot 0 \
            --batch_size auto \
            --gen_kwargs temperature=0.0 \
            --apply_chat_template

        kill $OLLAMA_PID 2>/dev/null || true

        # Copy results
        cp output/{params.task}/results*.json {output.results}
        cp output/{params.task}/samples*.jsonl {output.samples}
        """

# Aggregate all results
rule aggregate:
    input:
        expand(f"{OUTPUT_DIR}/{{model}}/{{task}}/results.json",
               model=[m.replace("/", "_") for m in MODELS],
               task=TASKS)
    output:
        f"{OUTPUT_DIR}/aggregated/summary.csv"
    run:
        import json
        import csv

        rows = [["model", "task", "metric", "value"]]
        for f in input:
            with open(f) as fp:
                data = json.load(fp)
                model = f.split("/")[-3]
                task = f.split("/")[-2]
                for metric, value in data.get("results", {}).get(task, {}).items():
                    if isinstance(value, (int, float)):
                        rows.append([model, task, metric, value])

        with open(output[0], "w", newline="") as fp:
            csv.writer(fp).writerows(rows)
```

### Advantages
- **Reproducibility**: Full provenance tracking
- **Fault tolerance**: Automatic retries and resume from failures
- **Scalability**: Handles hundreds of jobs with dependency management
- **Caching**: Skip completed tasks on re-run
- **Reports**: Automatic execution timelines and DAG visualization
- **Portability**: Same workflow runs on local, SLURM, cloud

### Disadvantages
- Learning curve for Nextflow/Snakemake DSL
- Additional software dependency
- Overkill for simple one-off evaluations

---

## Comparison Matrix

| Feature | Pattern 1: Jupyter | Pattern 2: OOD Form | Pattern 3: Workflow |
|---------|-------------------|---------------------|---------------------|
| **User Skill Level** | Python proficient | Any HPC user | Workflow DSL |
| **Setup Complexity** | Low | Medium | Medium |
| **Flexibility** | High | Medium | High |
| **Fault Tolerance** | Manual | Job arrays | Automatic retry |
| **Progress Tracking** | Custom code | OOD built-in | Workflow engine |
| **Reproducibility** | Git notebooks | Limited | Full provenance |
| **Scalability** | Good | Good | Excellent |
| **Result Aggregation** | Custom pandas | Manual | Built-in |
| **Best For** | Researchers | Lab-wide use | Production pipelines |

### Environment Support Matrix

| Environment Option | Pattern 1 | Pattern 2 | Pattern 3 |
|-------------------|-----------|-----------|-----------|
| **Container (Apptainer)** | Yes | Yes | Yes |
| **Virtual Environment** | Yes | Yes | Yes |
| **Hybrid (both)** | Yes | Yes | Yes |
| **Online compute nodes** | Yes | Yes | Yes |
| **Offline compute nodes** | Yes* | Yes* | Yes* |

*Requires pre-pulling models to shared cache on login node

### CUDA Compatibility Matrix

| CUDA Version | Container Support | Typical HPC Systems |
|--------------|------------------|---------------------|
| 11.7 - 11.8 | Yes | Older DoD, legacy academic |
| 12.1 - 12.4 | Yes (recommended) | Most modern HPCs |
| 12.6 - 12.8 | Yes | Cutting-edge systems |

Build for your specific CUDA: `./containers/build_container.sh <version>`

---

## Recommended Approach

For your dissertation research, I recommend a **phased implementation**:

### Phase A: Start with Pattern 1 (Jupyter)
- Quickest to implement
- Use existing notebooks as templates
- Good for exploratory work and debugging

### Phase B: Add Pattern 3 (Nextflow) for production runs
- Once workflow is stable, encode in Nextflow
- Enables reproducible large-scale evaluations
- Provides automatic reports for dissertation appendix

### Phase C: Consider Pattern 2 (OOD Form) for sharing
- If others in your lab need to run evaluations
- Lowers barrier to entry for non-programmers

---

## Next Steps

1. **Verify HPC environment**:
   - Confirm GPU partition names and limits
   - Check Apptainer/Singularity availability
   - Verify network access for model downloads (or set up model cache)

2. **Build container image**:
   ```bash
   cd dodhpc/containers
   apptainer build lm_eval_ollama.sif lm_eval_ollama.def
   ```

3. **Test single job**:
   ```bash
   sbatch jobs/eval_lm_single_pair.sbatch gemma3:1b sysengbench-a tasks output
   ```

4. **Implement chosen pattern(s)**

5. **Scale up evaluation matrix**

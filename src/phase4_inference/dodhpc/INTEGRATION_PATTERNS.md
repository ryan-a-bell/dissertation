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
    def __init__(self, base_dir: Path, container_image: Path):
        self.base_dir = Path(base_dir)
        self.container = Path(container_image)
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
            str(self.sbatch_template),
            config.model,
            config.task,
            str(self.tasks_dir),
            str(self.output_dir)
        ]
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
# Cell 1: Configuration
from hpc_inference.submit import HPCInferenceSubmitter, JobConfig
from pathlib import Path

submitter = HPCInferenceSubmitter(
    base_dir=Path.home() / "hpc_lm_eval",
    container_image=Path.home() / "hpc_lm_eval/containers/lm_eval_ollama.sif"
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

**Concept**: Build a production-ready Open OnDemand batch app with job arrays, progress tracking, and result visualization.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Open OnDemand Portal                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           LM-Eval Batch App (Interactive Form)           │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ Job Configuration Form                              ││    │
│  │  │ ┌─────────────────┐ ┌─────────────────────────────┐││    │
│  │  │ │ Model Selection │ │ Task Selection              │││    │
│  │  │ │ [ ] gemma3:1b   │ │ [x] sysengbench             │││    │
│  │  │ │ [x] gemma3:4b   │ │ [x] sysengbench-osq         │││    │
│  │  │ │ [x] llama3.2:3b │ │ [ ] sysengbench-a           │││    │
│  │  │ └─────────────────┘ └─────────────────────────────┘││    │
│  │  │ ┌─────────────────────────────────────────────────┐││    │
│  │  │ │ Resources: GPUs [1▼] Memory [16G▼] Time [4h▼]   │││    │
│  │  │ └─────────────────────────────────────────────────┘││    │
│  │  │                    [Submit Batch]                   ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  │                                                          │    │
│  │  ┌─────────────────────────────────────────────────────┐│    │
│  │  │ Active Jobs Dashboard                               ││    │
│  │  │ ┌───────────────────────────────────────────────┐  ││    │
│  │  │ │ Batch #4521 (gemma3:4b × sysengbench)         │  ││    │
│  │  │ │ ████████████░░░░░░░░ 60% (6/10 complete)      │  ││    │
│  │  │ │ [View Logs] [Cancel] [View Results]           │  ││    │
│  │  │ └───────────────────────────────────────────────┘  ││    │
│  │  └─────────────────────────────────────────────────────┘│    │
│  └──────────────────────────────────────────────────────────┘    │
│              │                                                   │
│              ▼ SLURM Job Array                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │   Job Array 4521[1-10]                                   │    │
│  │   4521_1: gemma3:4b × sysengbench    [COMPLETED]        │    │
│  │   4521_2: gemma3:4b × sysengbench-a  [RUNNING]          │    │
│  │   4521_3: gemma3:4b × sysengbench-b  [PENDING]          │    │
│  │   ...                                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Components

#### 2.1 Enhanced Form Configuration (`ood_app/lm_eval_batch/form.yml`)

```yaml
---
title: "LM Evaluation Batch Launcher"
cluster: "your_cluster"

attributes:
  bc_num_hours:
    label: "Wall time (hours)"
    value: 4
    min: 1
    max: 24

  bc_num_slots:
    label: "GPUs per job"
    value: 1
    min: 1
    max: 4
    widget: "number_field"

  bc_queue:
    label: "Partition"
    widget: "select"
    options:
      - ["GPU Shared (1-2 GPUs)", "gpu-shared"]
      - ["GPU Full Node (4 GPUs)", "gpu"]
      - ["GPU Debug (15 min)", "gpu-debug"]

  models:
    label: "Models to evaluate"
    widget: "check_box"
    options:
      - ["Gemma3 1B", "gemma3:1b", data-min-gpu: 1]
      - ["Gemma3 4B", "gemma3:4b", data-min-gpu: 1]
      - ["Gemma3 12B", "gemma3:12b", data-min-gpu: 1]
      - ["Llama 3.2 3B", "llama3.2:3b", data-min-gpu: 1]
      - ["Llama 3.3 70B (Q4)", "llama3.3:70b-instruct-q4_K_M", data-min-gpu: 2]
      - ["Mistral 7B", "mistral:7b", data-min-gpu: 1]
      - ["Phi4 14B", "phi4:14b", data-min-gpu: 1]
      - ["Mixtral 8x7B", "mixtral:8x7b", data-min-gpu: 2]

  tasks:
    label: "Benchmark tasks"
    widget: "check_box"
    options:
      - ["SysEngBench (MCQ)", "sysengbench"]
      - ["SysEngBench-A (Position A)", "sysengbench-a"]
      - ["SysEngBench-B (Position B)", "sysengbench-b"]
      - ["SysEngBench-C (Position C)", "sysengbench-c"]
      - ["SysEngBench-D (Position D)", "sysengbench-d"]
      - ["SysEngBench-OSQ (Open Short)", "sysengbench-osq"]

  job_strategy:
    label: "Job submission strategy"
    widget: "select"
    options:
      - ["Single Pair (max parallelism)", "single_pair"]
      - ["Multi-Task per Model (memory efficient)", "multi_task"]
      - ["Multi-Model per Task (task-focused)", "multi_model"]
    help: |
      - Single Pair: One job per (model, task) combination. Most parallel.
      - Multi-Task: One job runs all tasks for a single model. Fewer jobs.
      - Multi-Model: One job runs all models for a single task. Task-focused.

  notify_email:
    label: "Email on completion"
    widget: "email_field"
    required: false

form:
  - bc_queue
  - bc_num_hours
  - bc_num_slots
  - models
  - tasks
  - job_strategy
  - notify_email
```

#### 2.2 Job Array Template (`ood_app/lm_eval_batch/template/script.sh.erb`)

```bash
#!/bin/bash
#SBATCH --job-name=lm_eval_batch
#SBATCH --partition=<%= bc_queue %>
#SBATCH --gres=gpu:<%= bc_num_slots %>
#SBATCH --cpus-per-task=4
#SBATCH --mem=<%= bc_num_slots.to_i * 16 %>G
#SBATCH --time=<%= bc_num_hours %>:00:00
#SBATCH --output=<%= output_dir %>/logs/%x-%A_%a.out
#SBATCH --array=1-<%= job_count %>
<% if notify_email.present? %>
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=<%= notify_email %>
<% end %>

set -euo pipefail

# Job array configuration file (generated by OOD)
CONFIG_FILE="<%= output_dir %>/batch_<%= job_id %>/jobs.txt"

# Read this array task's configuration
LINE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" "$CONFIG_FILE")
MODEL=$(echo "$LINE" | cut -d'|' -f1)
TASK=$(echo "$LINE" | cut -d'|' -f2)

echo "[INFO] Array task ${SLURM_ARRAY_TASK_ID}: MODEL=$MODEL TASK=$TASK"

# Container setup
CONTAINER_IMAGE="$HOME/hpc_lm_eval/containers/lm_eval_ollama.sif"
TASKS_DIR="$HOME/hpc_lm_eval/tasks"
OUTPUT_ROOT="<%= output_dir %>/batch_<%= job_id %>/results"

SCRATCH_DIR="${SLURM_TMPDIR:-/tmp/lm_${SLURM_JOB_ID}}"
mkdir -p "$SCRATCH_DIR"
cd "$SCRATCH_DIR"

# Detect container runtime
if command -v apptainer &>/dev/null; then
  CNT=apptainer
elif command -v singularity &>/dev/null; then
  CNT=singularity
else
  echo "[ERROR] No container runtime found" >&2
  exit 1
fi

export MODEL TASK TASKS_DIR OUTPUT_ROOT

$CNT exec --nv "$CONTAINER_IMAGE" bash -lc '
  set -e

  mkdir -p tasks output
  cp "${TASKS_DIR}/${TASK}.yaml" tasks/

  # Start Ollama
  nohup env OLLAMA_HOST=0.0.0.0 ollama serve > ollama.log 2>&1 &
  OLLAMA_PID=$!
  sleep 15

  ollama pull "${MODEL}"

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

  kill $OLLAMA_PID 2>/dev/null || true
'

# Copy results
DEST_DIR="${OUTPUT_ROOT}/${MODEL//\//_}/${TASK}"
mkdir -p "$DEST_DIR"
cp -r "${SCRATCH_DIR}/output/${TASK}/." "$DEST_DIR/" 2>/dev/null || true

echo "[INFO] Complete: $MODEL × $TASK"
```

#### 2.3 Submit Hook (`ood_app/lm_eval_batch/submit.yml.erb`)

```yaml
---
batch_connect:
  template: "basic"

script:
  native:
    # Generate job configuration file before submission
    - "<%= generate_job_config_file %>"
```

### Advantages
- **User-friendly**: Point-and-click interface for non-programmers
- **Job arrays**: Efficient SLURM resource usage
- **Progress tracking**: OOD's built-in job monitoring
- **Email notifications**: Alert when batches complete
- **Audit trail**: OOD logs all submissions

### Disadvantages
- More complex to develop and maintain
- Requires OOD admin access to deploy
- Less flexible than programmatic approach

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

# hpc_lm_eval

Prototype HPC-friendly LM-Eval + Ollama pipeline designed to mirror your RunPod-based workflow,
but running entirely on a Slurm-based cluster (and accessible via Open OnDemand).

## Layout

```text
hpc_lm_eval/
├── containers/
│   ├── lm_eval_ollama.def       # Singularity/Apptainer definition (build once)
│   └── lm_eval_ollama.sif       # Built container image (you create this)
├── jobs/
│   ├── eval_lm_single_pair.sbatch                # One (model, task) per job
│   ├── eval_lm_multi_task_single_model.sbatch    # One model, many tasks per job
│   └── eval_lm_multi_model_single_task.sbatch    # One task, many models per job
├── scripts/
│   ├── submit_eval_jobs_pairs.py                 # Submits many single-pair jobs
│   ├── submit_eval_jobs_multi_task_single_model.py
│   └── submit_eval_jobs_multi_model_single_task.py
├── tasks/                     # YAML tasks are written here
├── output/                    # Results are written here (per model/task)
├── logs/                      # Slurm stdout logs
└── ood_app/
    └── lm_eval_simple/        # Open OnDemand app prototype
```

## Basic Usage

1. Build the container image on a build/login node:

   ```bash
   cd containers
   apptainer build lm_eval_ollama.sif lm_eval_ollama.def
   ```

   or (depending on your site):

   ```bash
   singularity build lm_eval_ollama.sif lm_eval_ollama.def
   ```

2. Edit the `#SBATCH --partition` lines in `jobs/*.sbatch` to match your GPU partition.

3. Populate `yaml_templates` and mappings in the Python scripts under `scripts/`:

   - `submit_eval_jobs_pairs.py`:
     - `missing_dict = { model: [tasks...] }`
   - `submit_eval_jobs_multi_task_single_model.py`:
     - `model_to_tasks = { model: [tasks...] }`
   - `submit_eval_jobs_multi_model_single_task.py`:
     - `task_to_models = { task: [models...] }`

4. From an Open OnDemand shell or Jupyter session, run for example:

   ```bash
   cd ~/hpc_lm_eval/scripts
   python submit_eval_jobs_pairs.py
   ```

5. Monitor jobs via `squeue` or the Open OnDemand "Jobs" interface. Results will be under
   `~/hpc_lm_eval/output/` and logs under `~/hpc_lm_eval/logs/`.

## Ephemeral Behavior

Each Slurm job:

- Reserves a GPU node
- Creates a node-local scratch dir (`$SLURM_TMPDIR` or `/tmp`)
- Runs inside the `lm_eval_ollama.sif` container
- Starts an Ollama daemon
- Pulls the model (ephemeral)
- Runs `lm_eval`
- Copies results to `output/`
- Leaves no models or intermediate state on the node once the job ends

This closely mirrors the RunPod pattern of "create ephemeral pod -> install/pull -> evaluate -> collect -> delete".

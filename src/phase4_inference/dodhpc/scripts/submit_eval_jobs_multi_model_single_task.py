#!/usr/bin/env python
"""Submit one Slurm job per TASK, running multiple MODELs sequentially.

Uses eval_lm_multi_model_single_task.sbatch.
"""
import subprocess
from pathlib import Path

BASE_DIR = Path.home() / "hpc_lm_eval"
SBATCH_SCRIPT = BASE_DIR / "jobs" / "eval_lm_multi_model_single_task.sbatch"
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_ROOT = BASE_DIR / "output"

def write_task_yamls(yaml_templates: dict):
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    for task_name, yaml_text in yaml_templates.items():
        out_path = TASKS_DIR / f"{task_name}.yaml"
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"[TASK YAML] Wrote {out_path}")

def submit_tasks(task_to_models: dict):
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    jobs = []

    for task, models in task_to_models.items():
        if not models:
            continue

        # Create a model list file
        model_list_file = BASE_DIR / f"model_list_{task}.txt"
        model_list_file.write_text("\n".join(models) + "\n", encoding="utf-8")
        print(f"[MODEL LIST] Wrote {model_list_file}")

        cmd = [
            "sbatch",
            str(SBATCH_SCRIPT),
            task,
            str(TASKS_DIR),
            str(model_list_file),
            str(OUTPUT_ROOT),
        ]
        print(f"[SUBMIT] {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        line = result.stdout.strip()
        print(f"[SLURM] {line}")
        jobs.append((task, line))

    print("\n[SUMMARY] Submitted jobs (multi-model per task):")
    for task, info in jobs:
        print(f"  {task} -> {info}")

if __name__ == "__main__":
    # TODO: Replace with your task -> [models] mapping
    task_to_models = {
        # "sysengbench-a": ["mistral:7b", "mistral:instruct"],
        # "sysengbench-b": ["mistral:7b"],
    }
    yaml_templates = {
        # "sysengbench-a": """<YAML CONTENT HERE>""" ,
        # "sysengbench-b": """<YAML CONTENT HERE>""" ,
    }

    if not task_to_models:
        raise SystemExit("task_to_models is empty. Populate it before running.")
    if not yaml_templates:
        raise SystemExit("yaml_templates is empty. Populate yaml_templates before running.")

    write_task_yamls(yaml_templates)
    submit_tasks(task_to_models)

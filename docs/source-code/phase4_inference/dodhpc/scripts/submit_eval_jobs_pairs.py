#!/usr/bin/env python
"""Submit one Slurm job per (model, task) pair using eval_lm_single_pair.sbatch.

This is the closest analog to your RunPod parallel-pod approach.
"""
import subprocess
from pathlib import Path

BASE_DIR = Path.home() / "hpc_lm_eval"
SBATCH_SCRIPT = BASE_DIR / "jobs" / "eval_lm_single_pair.sbatch"
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_ROOT = BASE_DIR / "output"

def write_task_yamls(yaml_templates: dict):
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    for task_name, yaml_text in yaml_templates.items():
        out_path = TASKS_DIR / f"{task_name}.yaml"
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"[TASK YAML] Wrote {out_path}")

def submit_missing_models(missing_dict: dict):
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    jobs = []

    for model, tasks in missing_dict.items():
        for task in tasks:
            cmd = [
                "sbatch",
                str(SBATCH_SCRIPT),
                model,
                task,
                str(TASKS_DIR),
                str(OUTPUT_ROOT),
            ]
            print(f"[SUBMIT] {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            line = result.stdout.strip()
            print(f"[SLURM] {line}")
            jobs.append((model, task, line))

    print("\n[SUMMARY] Submitted jobs:")
    for model, task, info in jobs:
        print(f"  {model} | {task} -> {info}")

if __name__ == "__main__":
    # TODO: Replace these placeholders with your actual mappings
    missing_dict = {
        # "mistral:7b": ["sysengbench-a", "sysengbench-b"],
        # "mistral:instruct": ["sysengbench-a"],
    }
    yaml_templates = {
        # "sysengbench-a": """<YAML CONTENT HERE>""" ,
        # "sysengbench-b": """<YAML CONTENT HERE>""" ,
    }

    if not missing_dict:
        raise SystemExit("missing_dict is empty. Populate it before running.")
    if not yaml_templates:
        raise SystemExit("yaml_templates is empty. Populate it before running.")

    write_task_yamls(yaml_templates)
    submit_missing_models(missing_dict)

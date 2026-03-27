#!/usr/bin/env python
"""Submit one Slurm job per MODEL, running multiple TASKs sequentially.

Uses eval_lm_multi_task_single_model.sbatch.
"""
import subprocess
from pathlib import Path

BASE_DIR = Path.home() / "hpc_lm_eval"
SBATCH_SCRIPT = BASE_DIR / "jobs" / "eval_lm_multi_task_single_model.sbatch"
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_ROOT = BASE_DIR / "output"

def write_task_yamls(yaml_templates: dict):
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    for task_name, yaml_text in yaml_templates.items():
        out_path = TASKS_DIR / f"{task_name}.yaml"
        out_path.write_text(yaml_text, encoding="utf-8")
        print(f"[TASK YAML] Wrote {out_path}")

def submit_models(model_to_tasks: dict):
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    jobs = []

    for model, tasks in model_to_tasks.items():
        if not tasks:
            continue

        # Create a task list file
        task_list_file = BASE_DIR / f"task_list_{model.replace(':','_')}.txt"
        task_list_file.write_text("\n".join(tasks) + "\n", encoding="utf-8")
        print(f"[TASK LIST] Wrote {task_list_file}")

        cmd = [
            "sbatch",
            str(SBATCH_SCRIPT),
            model,
            str(TASKS_DIR),
            str(task_list_file),
            str(OUTPUT_ROOT),
        ]
        print(f"[SUBMIT] {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        line = result.stdout.strip()
        print(f"[SLURM] {line}")
        jobs.append((model, line))

    print("\n[SUMMARY] Submitted jobs (multi-task per model):")
    for model, info in jobs:
        print(f"  {model} -> {info}")

if __name__ == "__main__":
    # TODO: Replace with your model -> [tasks] mapping
    model_to_tasks = {
        # "mistral:7b": ["sysengbench-a", "sysengbench-b"],
        # "mistral:instruct": ["sysengbench-c"],
    }
    yaml_templates = {
        # "sysengbench-a": """<YAML CONTENT HERE>""" ,
        # "sysengbench-b": """<YAML CONTENT HERE>""" ,
        # "sysengbench-c": """<YAML CONTENT HERE>""" ,
    }

    if not model_to_tasks:
        raise SystemExit("model_to_tasks is empty. Populate it before running.")
    if not yaml_templates:
        raise SystemExit("yaml_templates is empty. Populate yaml_templates before running.")

    write_task_yamls(yaml_templates)
    submit_models(model_to_tasks)

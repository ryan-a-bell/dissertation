"""Task YAML generation for lm-eval harness."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


# Default task configuration
DEFAULT_MCQ_CONFIG = {
    "dataset_path": "ryan-a-bell/SysEngBench",
    "output_type": "multiple_choice",
    "doc_to_text": "{{question}}\nA) {{choice_a}}\nB) {{choice_b}}\nC) {{choice_c}}\nD) {{choice_d}}\nAnswer:",
    "doc_to_target": "answer",
    "doc_to_choice": ["A", "B", "C", "D"],
    "metric_list": [{"metric": "acc", "aggregation": "mean", "higher_is_better": True}],
}

DEFAULT_OSQ_CONFIG = {
    "dataset_path": "ryan-a-bell/SysEngBench-OSQ",
    "output_type": "generate_until",
    "doc_to_text": "{{osq_prompt}}\n\nAnswer:",
    "doc_to_target": "expected_answer",
    "generation_kwargs": {
        "until": ["\n\n", "</s>"],
        "max_gen_toks": 512,
        "temperature": 0.0,
    },
    "metric_list": [
        {"metric": "exact_match", "aggregation": "mean", "higher_is_better": True}
    ],
}


def generate_mcq_task(
    task_name: str,
    dataset_path: str | None = None,
    split: str = "test",
    num_fewshot: int = 0,
    output_path: Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate an MCQ task configuration for lm-eval.

    Args:
        task_name: Name of the task
        dataset_path: HuggingFace dataset path
        split: Dataset split to use
        num_fewshot: Number of few-shot examples
        output_path: Optional path to save YAML
        **kwargs: Additional configuration overrides

    Returns:
        Task configuration dictionary
    """
    config = {
        "task": task_name,
        **DEFAULT_MCQ_CONFIG,
        "test_split": split,
        "num_fewshot": num_fewshot,
    }

    if dataset_path:
        config["dataset_path"] = dataset_path

    config.update(kwargs)

    if output_path:
        save_task_yaml(config, output_path)

    return config


def generate_osq_task(
    task_name: str,
    dataset_path: str | None = None,
    split: str = "test",
    num_fewshot: int = 0,
    max_tokens: int = 512,
    output_path: Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate an OSQ task configuration for lm-eval.

    Args:
        task_name: Name of the task
        dataset_path: HuggingFace dataset path
        split: Dataset split to use
        num_fewshot: Number of few-shot examples
        max_tokens: Maximum generation tokens
        output_path: Optional path to save YAML
        **kwargs: Additional configuration overrides

    Returns:
        Task configuration dictionary
    """
    config = {
        "task": task_name,
        **DEFAULT_OSQ_CONFIG,
        "test_split": split,
        "num_fewshot": num_fewshot,
    }

    if dataset_path:
        config["dataset_path"] = dataset_path

    config["generation_kwargs"]["max_gen_toks"] = max_tokens
    config.update(kwargs)

    if output_path:
        save_task_yaml(config, output_path)

    return config


def generate_task_yaml(
    task_name: str,
    task_type: str = "mcq",
    dataset_path: str | None = None,
    split: str = "test",
    num_fewshot: int = 0,
    output_path: Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate a task configuration for lm-eval.

    Args:
        task_name: Name of the task
        task_type: Type of task ("mcq" or "osq")
        dataset_path: HuggingFace dataset path
        split: Dataset split to use
        num_fewshot: Number of few-shot examples
        output_path: Optional path to save YAML
        **kwargs: Additional configuration overrides

    Returns:
        Task configuration dictionary
    """
    if task_type.lower() == "mcq":
        return generate_mcq_task(
            task_name=task_name,
            dataset_path=dataset_path,
            split=split,
            num_fewshot=num_fewshot,
            output_path=output_path,
            **kwargs,
        )
    elif task_type.lower() == "osq":
        return generate_osq_task(
            task_name=task_name,
            dataset_path=dataset_path,
            split=split,
            num_fewshot=num_fewshot,
            output_path=output_path,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def save_task_yaml(config: dict[str, Any], path: Path) -> None:
    """
    Save task configuration to YAML file.

    Args:
        config: Task configuration dictionary
        path: Output file path
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    logger.info(f"Saved task configuration to {path}")


def load_task_yaml(path: Path) -> dict[str, Any]:
    """
    Load task configuration from YAML file.

    Args:
        path: Input file path

    Returns:
        Task configuration dictionary
    """
    with open(path) as f:
        config = yaml.safe_load(f)

    return config


def generate_variant_tasks(
    base_name: str,
    dataset_paths: dict[str, str],
    output_dir: Path | None = None,
    **kwargs: Any,
) -> dict[str, dict[str, Any]]:
    """
    Generate task configurations for all position variants.

    Args:
        base_name: Base name for tasks
        dataset_paths: Dictionary mapping position (A, B, C, D) to dataset paths
        output_dir: Optional directory to save YAML files
        **kwargs: Additional configuration overrides

    Returns:
        Dictionary mapping position to task configuration
    """
    tasks = {}

    for position, dataset_path in dataset_paths.items():
        task_name = f"{base_name}_{position.lower()}"
        output_path = None
        if output_dir:
            output_path = Path(output_dir) / f"{task_name}.yaml"

        tasks[position] = generate_mcq_task(
            task_name=task_name,
            dataset_path=dataset_path,
            output_path=output_path,
            **kwargs,
        )

    logger.info(f"Generated {len(tasks)} variant task configurations")
    return tasks

"""lm-eval output directory discovery utilities."""

from __future__ import annotations

from pathlib import Path

from metaeval.core.logging import get_logger

logger = get_logger(__name__)


def find_runs(
    base_dir: Path | str,
    task_filter: str | None = None,
    model_filter: str | None = None,
) -> list[Path]:
    """
    Find all lm-eval output directories under a base directory.

    Expected structure:
        base_dir/
            task_name/
                model_name/
                    results_*.json
                    samples_*.jsonl

    Args:
        base_dir: Base output directory
        task_filter: Only include tasks containing this string
        model_filter: Only include models containing this string

    Returns:
        List of paths to model output directories (sorted)
    """
    base_dir = Path(base_dir)
    runs = []

    for task_dir in base_dir.iterdir():
        if not task_dir.is_dir():
            continue
        if task_filter and task_filter not in task_dir.name:
            continue

        for model_dir in task_dir.iterdir():
            if not model_dir.is_dir():
                continue
            if model_filter and model_filter not in model_dir.name:
                continue

            # Check if this looks like an lm-eval output dir
            has_results = (
                list(model_dir.glob("results_*.json")) or
                (model_dir / "results.json").exists()
            )
            has_samples = list(model_dir.glob("samples_*.jsonl"))

            if has_results and has_samples:
                runs.append(model_dir)

    return sorted(runs)


def find_latest_results(model_dir: Path | str) -> Path:
    """
    Find most recent results.json in a model directory.

    Args:
        model_dir: Path to model output directory

    Returns:
        Path to most recent results JSON file

    Raises:
        FileNotFoundError: If no results file found
    """
    model_dir = Path(model_dir)

    # Try timestamped results first
    results_files = list(model_dir.glob("results_*.json"))
    if results_files:
        return max(results_files, key=lambda p: p.stat().st_mtime)

    # Fall back to plain results.json
    plain = model_dir / "results.json"
    if plain.exists():
        return plain

    raise FileNotFoundError(f"No results.json found in {model_dir}")


def find_latest_samples(model_dir: Path | str) -> Path:
    """
    Find most recent samples.jsonl in a model directory.

    Args:
        model_dir: Path to model output directory

    Returns:
        Path to most recent samples JSONL file

    Raises:
        FileNotFoundError: If no samples file found
    """
    model_dir = Path(model_dir)

    samples_files = list(model_dir.glob("samples_*.jsonl"))
    if samples_files:
        return max(samples_files, key=lambda p: p.stat().st_mtime)

    raise FileNotFoundError(f"No samples.jsonl found in {model_dir}")


def list_models(base_dir: Path | str, task: str | None = None) -> list[str]:
    """
    List all models that have results in the output directory.

    Args:
        base_dir: Base output directory
        task: Optional task name to filter by

    Returns:
        Sorted list of unique model names
    """
    runs = find_runs(base_dir, task_filter=task)
    models = set()
    for run in runs:
        models.add(run.name)
    return sorted(models)


def list_tasks(base_dir: Path | str) -> list[str]:
    """
    List all tasks that have results in the output directory.

    Args:
        base_dir: Base output directory

    Returns:
        Sorted list of unique task names
    """
    base_dir = Path(base_dir)
    tasks = set()

    for task_dir in base_dir.iterdir():
        if not task_dir.is_dir():
            continue
        # Check if any model has results for this task
        for model_dir in task_dir.iterdir():
            if model_dir.is_dir():
                has_results = (
                    list(model_dir.glob("results_*.json")) or
                    (model_dir / "results.json").exists()
                )
                if has_results:
                    tasks.add(task_dir.name)
                    break

    return sorted(tasks)


def get_run_summary(base_dir: Path | str) -> dict[str, dict[str, int]]:
    """
    Get summary of runs by task and model.

    Args:
        base_dir: Base output directory

    Returns:
        Nested dict: {task: {model: n_samples}}
    """
    from metaeval.harness.results import LMEvalResults

    summary: dict[str, dict[str, int]] = {}

    for run_dir in find_runs(base_dir):
        task = run_dir.parent.name
        model = run_dir.name

        try:
            results = LMEvalResults.from_json(find_latest_results(run_dir))
            n_samples = results.n_samples

            if task not in summary:
                summary[task] = {}
            summary[task][model] = n_samples
        except Exception as e:
            logger.warning(f"Failed to read {run_dir}: {e}")

    return summary

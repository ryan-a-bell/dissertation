#!/usr/bin/env python3
"""
Collect and package inference results for download/transfer.

This script aggregates results from the output directory structure into
a single package (tar.gz or zip) for easy download and processing elsewhere.

Usage:
    python collect_results.py                    # Collect all results
    python collect_results.py --task sysengbench # Filter by task
    python collect_results.py --model gemma3     # Filter by model
    python collect_results.py --format zip       # Output as ZIP instead of tar.gz
    python collect_results.py --summary          # Just print summary, don't package
"""
import argparse
import json
import os
import sys
import tarfile
import zipfile
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


def find_results(output_dir: Path, model_filter: Optional[str] = None,
                 task_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Find all results.json files in output directory."""
    results = []

    for model_dir in output_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name

        # Apply model filter
        if model_filter and model_filter.lower() not in model_name.lower():
            continue

        for task_dir in model_dir.iterdir():
            if not task_dir.is_dir():
                continue

            task_name = task_dir.name

            # Apply task filter
            if task_filter and task_filter.lower() not in task_name.lower():
                continue

            # Find results files
            result_files = list(task_dir.glob("results*.json"))
            sample_files = list(task_dir.glob("samples*.jsonl"))

            for result_file in result_files:
                try:
                    with open(result_file) as f:
                        data = json.load(f)

                    results.append({
                        "model": model_name,
                        "task": task_name,
                        "result_file": result_file,
                        "sample_files": sample_files,
                        "data": data,
                        "metrics": extract_metrics(data, task_name)
                    })
                except Exception as e:
                    print(f"[WARN] Failed to read {result_file}: {e}")

    return results


def extract_metrics(data: dict, task_name: str) -> Dict[str, float]:
    """Extract key metrics from results data."""
    metrics = {}

    # Navigate to results section
    results_section = data.get("results", {})

    for task, task_metrics in results_section.items():
        if isinstance(task_metrics, dict):
            for metric_name, value in task_metrics.items():
                if isinstance(value, (int, float)):
                    key = f"{task}_{metric_name}" if task != task_name else metric_name
                    metrics[key] = value

    return metrics


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print summary of collected results."""
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Group by task
    by_task = {}
    for r in results:
        task = r["task"]
        if task not in by_task:
            by_task[task] = []
        by_task[task].append(r)

    for task, task_results in sorted(by_task.items()):
        print(f"\n{task}:")
        print("-" * 50)

        # Find common metric
        metric_key = None
        for r in task_results:
            if r["metrics"]:
                # Prefer exact_match or acc
                for key in ["exact_match", "acc", "accuracy"]:
                    if key in r["metrics"]:
                        metric_key = key
                        break
                if metric_key:
                    break

        if metric_key:
            # Sort by metric value
            task_results.sort(key=lambda x: x["metrics"].get(metric_key, 0), reverse=True)

            for r in task_results:
                value = r["metrics"].get(metric_key, "N/A")
                if isinstance(value, float):
                    value = f"{value:.4f}"
                print(f"  {r['model']:<40} {metric_key}: {value}")
        else:
            for r in task_results:
                print(f"  {r['model']}")

    print(f"\nTotal: {len(results)} result files")


def create_summary_csv(results: List[Dict[str, Any]], output_path: Path) -> None:
    """Create summary CSV with all results."""
    if not results:
        return

    # Collect all metric keys
    all_metrics = set()
    for r in results:
        all_metrics.update(r["metrics"].keys())

    all_metrics = sorted(all_metrics)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(["model", "task"] + list(all_metrics))

        # Data rows
        for r in results:
            row = [r["model"], r["task"]]
            for metric in all_metrics:
                value = r["metrics"].get(metric, "")
                row.append(value)
            writer.writerow(row)


def create_package(results: List[Dict[str, Any]], output_path: Path,
                   format: str = "tar.gz") -> None:
    """Create archive package with all results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"lm_eval_results_{timestamp}"

    if format == "zip":
        archive_path = output_path / f"{base_name}.zip"
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add summary CSV
            summary_path = output_path / "summary.csv"
            create_summary_csv(results, summary_path)
            zf.write(summary_path, f"{base_name}/summary.csv")
            summary_path.unlink()

            # Add all result files
            for r in results:
                # Result JSON
                arcname = f"{base_name}/{r['model']}/{r['task']}/{r['result_file'].name}"
                zf.write(r["result_file"], arcname)

                # Sample files
                for sf in r["sample_files"]:
                    arcname = f"{base_name}/{r['model']}/{r['task']}/{sf.name}"
                    zf.write(sf, arcname)
    else:
        archive_path = output_path / f"{base_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tf:
            # Add summary CSV
            summary_path = output_path / "summary.csv"
            create_summary_csv(results, summary_path)
            tf.add(summary_path, f"{base_name}/summary.csv")
            summary_path.unlink()

            # Add all result files
            for r in results:
                # Result JSON
                arcname = f"{base_name}/{r['model']}/{r['task']}/{r['result_file'].name}"
                tf.add(r["result_file"], arcname)

                # Sample files
                for sf in r["sample_files"]:
                    arcname = f"{base_name}/{r['model']}/{r['task']}/{sf.name}"
                    tf.add(sf, arcname)

    print(f"\n[OK] Created: {archive_path}")
    print(f"[INFO] Size: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")


def main():
    parser = argparse.ArgumentParser(
        description="Collect and package LM evaluation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    Collect all results
  %(prog)s --task sysengbench                 Filter by task name
  %(prog)s --model gemma                      Filter by model name
  %(prog)s --format zip                       Create ZIP instead of tar.gz
  %(prog)s --summary                          Just print summary
  %(prog)s -o /path/to/package                Specify output directory
        """
    )
    parser.add_argument(
        "-d", "--output-dir",
        type=Path,
        default=Path(os.environ.get("HOME", ".")) / "hpc_lm_eval" / "output",
        help="Results output directory (default: ~/hpc_lm_eval/output)"
    )
    parser.add_argument(
        "-o", "--package-dir",
        type=Path,
        default=None,
        help="Directory for output package (default: same as output-dir)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Filter by model name (partial match)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Filter by task name (partial match)"
    )
    parser.add_argument(
        "--format",
        choices=["tar.gz", "zip"],
        default="tar.gz",
        help="Archive format (default: tar.gz)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Just print summary, don't create package"
    )

    args = parser.parse_args()

    output_dir = args.output_dir
    package_dir = args.package_dir or output_dir

    if not output_dir.exists():
        print(f"[ERROR] Output directory not found: {output_dir}")
        sys.exit(1)

    print(f"[INFO] Scanning: {output_dir}")
    if args.model:
        print(f"[INFO] Model filter: {args.model}")
    if args.task:
        print(f"[INFO] Task filter: {args.task}")

    results = find_results(output_dir, args.model, args.task)

    if not results:
        print("[WARN] No results found")
        sys.exit(0)

    print(f"[INFO] Found {len(results)} result files")

    print_summary(results)

    if not args.summary:
        create_package(results, package_dir, args.format)


if __name__ == "__main__":
    main()

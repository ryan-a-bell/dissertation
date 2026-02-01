"""Main CLI entry point for metaeval."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from metaeval.core.config import Config
from metaeval.core.logging import setup_logging, get_logger

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="metaeval",
        description="Meta-evaluation toolkit for LLM evaluation methods",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download benchmark datasets",
    )
    download_parser.add_argument(
        "dataset",
        help="Dataset identifier (e.g., ryan-a-bell/SysEngBench)",
    )
    download_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("data"),
        help="Output directory",
    )
    download_parser.add_argument(
        "--split",
        default="test",
        help="Dataset split to download",
    )

    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert MCQ to OSQ format",
    )
    convert_parser.add_argument(
        "input",
        type=Path,
        help="Input MCQ file (CSV)",
    )
    convert_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output OSQ file",
    )
    convert_parser.add_argument(
        "--model",
        default="gpt-4o",
        help="Model for conversion",
    )
    convert_parser.add_argument(
        "--threshold",
        type=int,
        default=7,
        help="Suitability threshold (1-10)",
    )
    convert_parser.add_argument(
        "--prompt",
        default="standard",
        help="Conversion prompt name (use 'metaeval prompts convert' to list)",
    )
    convert_parser.add_argument(
        "--classification-prompt",
        default="classification",
        help="Classification prompt name",
    )

    # Variants command
    variants_parser = subparsers.add_parser(
        "variants",
        help="Generate position variants",
    )
    variants_parser.add_argument(
        "input",
        type=Path,
        help="Input MCQ file (CSV)",
    )
    variants_parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("variants"),
        help="Output directory",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run analysis on results",
    )
    analyze_parser.add_argument(
        "type",
        choices=["bias", "compare", "all"],
        help="Type of analysis",
    )
    analyze_parser.add_argument(
        "input",
        type=Path,
        help="Input results directory or file",
    )
    analyze_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("analysis"),
        help="Output directory",
    )
    analyze_parser.add_argument(
        "--format",
        choices=["markdown", "latex", "json"],
        default="markdown",
        help="Output format",
    )
    analyze_parser.add_argument(
        "--judged",
        type=Path,
        help="Path to judged OSQ results (for compare analysis)",
    )

    # Judge command
    judge_parser = subparsers.add_parser(
        "judge",
        help="Run LLM-as-a-Judge evaluation",
    )
    judge_parser.add_argument(
        "input",
        type=Path,
        help="Input file with responses to judge",
    )
    judge_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output file for judgments",
    )
    judge_parser.add_argument(
        "--model",
        help="Judge model (default depends on provider)",
    )
    judge_parser.add_argument(
        "--provider",
        choices=["ollama", "openai", "anthropic", "openrouter"],
        default="ollama",
        help="Model provider",
    )
    judge_parser.add_argument(
        "--prompt",
        default="multi_dimensional",
        help="Judge prompt name (use 'metaeval prompts judge' to list)",
    )
    judge_parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Generation temperature (default: 0.0)",
    )
    judge_parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Maximum tokens to generate (default: 2048)",
    )
    judge_parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start fresh, ignoring any existing output file",
    )
    judge_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable response caching",
    )

    # Prompts command
    prompts_parser = subparsers.add_parser(
        "prompts",
        help="List or show available prompts",
    )
    prompts_parser.add_argument(
        "category",
        nargs="?",
        choices=["judge", "convert"],
        help="Category to list (omit for all)",
    )
    prompts_parser.add_argument(
        "--show",
        metavar="NAME",
        help="Show full prompt template by name",
    )
    prompts_parser.add_argument(
        "--path",
        type=Path,
        help="Add custom prompts directory",
    )

    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate analysis report",
    )
    report_parser.add_argument(
        "input",
        type=Path,
        help="Input analysis results",
    )
    report_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("report.md"),
        help="Output report file",
    )
    report_parser.add_argument(
        "--title",
        default="Meta-Evaluation Analysis Report",
        help="Report title",
    )

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show or manage configuration",
    )
    config_parser.add_argument(
        "action",
        nargs="?",
        choices=["show", "init", "path"],
        default="show",
        help="Action: show (display config), init (create config file), path (show config path)",
    )
    config_parser.add_argument(
        "--output",
        type=Path,
        help="Output path for init (default: ~/.metaeval/config.yaml)",
    )

    # Eval command (help/documentation only)
    eval_parser = subparsers.add_parser(
        "eval",
        help="Run model evaluation (shows lm-eval usage)",
    )
    eval_parser.add_argument(
        "--example",
        choices=["mcq", "osq", "bias"],
        help="Show example command for specific use case",
    )

    # Results command
    results_parser = subparsers.add_parser(
        "results",
        help="List and inspect lm-eval results",
    )
    results_parser.add_argument(
        "action",
        nargs="?",
        choices=["list", "show", "summary"],
        default="list",
        help="Action: list (show all runs), show (details for one run), summary (aggregate stats)",
    )
    results_parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("output"),
        help="Path to lm-eval output directory (default: ./output)",
    )
    results_parser.add_argument(
        "--task",
        help="Filter by task name (e.g., 'sysengbench-a', 'osq')",
    )
    results_parser.add_argument(
        "--model",
        help="Filter by model name",
    )
    results_parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    return parser


def cmd_download(args: argparse.Namespace) -> int:
    """Handle download command."""
    from metaeval.benchmark.download import download_benchmark

    logger.info(f"Downloading {args.dataset}...")

    try:
        df = download_benchmark(args.dataset, split=args.split)

        args.output.mkdir(parents=True, exist_ok=True)
        output_path = args.output / f"{args.dataset.replace('/', '_')}.csv"
        df.to_csv(output_path, index=False)

        logger.info(f"Saved {len(df)} questions to {output_path}")
        return 0

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return 1


def cmd_convert(args: argparse.Namespace) -> int:
    """Handle convert command."""
    import os
    import pandas as pd
    from metaeval.benchmark.convert import MCQToOSQConverter, conversions_to_dataframe

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable required")
        return 1

    logger.info(f"Converting {args.input} using prompt '{args.prompt}'...")

    try:
        df = pd.read_csv(args.input)

        converter = MCQToOSQConverter(
            api_key=api_key,
            model=args.model,
            confidence_threshold=args.threshold,
            classification_prompt=args.classification_prompt,
            conversion_prompt=args.prompt,
        )

        conversions, _ = converter.batch_convert(df)

        output_path = args.output or args.input.with_suffix(".osq.csv")
        result_df = conversions_to_dataframe(conversions)
        result_df.to_csv(output_path, index=False)

        logger.info(f"Converted {len(conversions)} questions to {output_path}")
        return 0

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return 1


def cmd_variants(args: argparse.Namespace) -> int:
    """Handle variants command."""
    import pandas as pd
    from metaeval.benchmark.variants import create_position_variants, save_variants

    logger.info(f"Generating variants for {args.input}...")

    try:
        df = pd.read_csv(args.input)
        variants = create_position_variants(df)
        paths = save_variants(variants, args.output_dir, prefix=args.input.stem)

        logger.info(f"Generated {len(variants)} variants: {list(paths.values())}")
        return 0

    except Exception as e:
        logger.error(f"Variant generation failed: {e}")
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Handle analyze command."""
    import json
    import pandas as pd

    logger.info(f"Running {args.type} analysis on {args.input}...")

    try:
        args.output.mkdir(parents=True, exist_ok=True)

        if args.type == "bias":
            from metaeval.bias.detection import PositionBiasAnalyzer

            # Check if input is lm-eval output directory or CSV
            if args.input.is_dir():
                # Parse lm-eval output directory
                from metaeval.harness import LMEvalParser

                logger.info("Detected lm-eval output directory, parsing results...")
                results_by_model = LMEvalParser.collect_mcq_by_variant(args.input)

                if not results_by_model:
                    logger.error("No MCQ results found. Need variants A, B, C, D.")
                    return 1

                # Validate variant coverage per model
                validation_errors = _validate_variant_coverage(results_by_model)
                if validation_errors["errors"]:
                    for err in validation_errors["errors"]:
                        logger.error(err)
                    print("\n" + "=" * 80)
                    print("INSUFFICIENT DATA FOR BIAS ANALYSIS")
                    print("=" * 80)
                    print("\nPosition bias analysis requires at least 2 variants (A, B, C, or D).")
                    print("Ideally, run all 4 variants for each model.\n")
                    print("To generate variants:")
                    print("  metaeval variants data/benchmark.csv -o variants/\n")
                    print("Then run lm-eval on each variant:")
                    print("  lm_eval --tasks sysengbench-a.yaml,sysengbench-b.yaml,...")
                    print("=" * 80)
                    return 1

                if validation_errors["warnings"]:
                    print("\n" + "-" * 80)
                    print("WARNING: Suboptimal variant coverage")
                    print("-" * 80)
                    for warn in validation_errors["warnings"]:
                        print(f"  {warn}")
                    print("\nFor best results, run all 4 variants (A, B, C, D) for each model.")
                    print("Proceeding with available data...")
                    print("-" * 80 + "\n")

                # Convert to DataFrame expected by PositionBiasAnalyzer
                rows = []
                for model, variants in results_by_model.items():
                    for variant, mcq_results in variants.items():
                        for r in mcq_results:
                            rows.append({
                                "model": model,
                                "variant": variant,
                                "question_id": r.question_id,
                                "is_correct": int(r.is_correct),
                            })
                df = pd.DataFrame(rows)
                logger.info(f"Loaded {len(df)} results from {len(results_by_model)} models")
            else:
                # Load from CSV
                df = pd.read_csv(args.input)

            analyzer = PositionBiasAnalyzer(df)
            reports = analyzer.analyze_all_models()

            # Print summary table first (always useful)
            _print_bias_summary_table(reports)

            # Save results
            results = {m: _serialize_report(r.to_dict()) for m, r in reports.items()}

            if args.format == "json":
                with open(args.output / "bias_results.json", "w") as f:
                    json.dump(results, f, indent=2, default=str)
            elif args.format == "markdown":
                try:
                    from metaeval.report.markdown import generate_summary_report
                    report = generate_summary_report(bias_reports=reports)
                    with open(args.output / "bias_report.md", "w") as f:
                        f.write(report)
                except ImportError as e:
                    logger.warning(f"Markdown generation skipped: {e}")

        elif args.type == "compare":
            from metaeval.compare.analysis import FormatComparator

            # Check if input is lm-eval output directory
            if args.input.is_dir():
                # Look for judged results to compare with MCQ
                judged_dir = args.output / "judged"  # Default location
                if hasattr(args, 'judged') and args.judged:
                    judged_dir = args.judged

                if not judged_dir.exists():
                    logger.error(
                        "MCQ vs OSQ comparison requires judged OSQ results.\n"
                        "First run: metaeval judge ./output/sysengbench-osq/<model>/\n"
                        "Then run: metaeval analyze compare ./output/ --judged ./judged/"
                    )
                    return 1

                df = _build_comparison_dataframe(args.input, judged_dir)
            else:
                df = pd.read_csv(args.input)

            if df.empty:
                logger.error("No aligned MCQ/OSQ data found")
                return 1

            comparator = FormatComparator(df)
            reports = comparator.analyze_all_models()

            # Print summary table
            _print_comparison_summary_table(reports)

            results = {m: _serialize_report(r.to_dict()) for m, r in reports.items()}

            if args.format == "json":
                with open(args.output / "compare_results.json", "w") as f:
                    json.dump(results, f, indent=2, default=str)
            elif args.format == "markdown":
                try:
                    from metaeval.report.markdown import generate_summary_report
                    report = generate_summary_report(comparison_reports=reports)
                    with open(args.output / "compare_report.md", "w") as f:
                        f.write(report)
                except ImportError as e:
                    logger.warning(f"Markdown generation skipped: {e}")

        logger.info(f"Analysis complete. Results saved to {args.output}")
        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _validate_variant_coverage(
    results_by_model: dict[str, dict[str, list]]
) -> dict[str, list[str]]:
    """
    Validate that models have sufficient variant coverage for bias analysis.

    Args:
        results_by_model: Dict of {model: {variant: [results]}}

    Returns:
        Dict with "errors" and "warnings" lists
    """
    errors = []
    warnings = []
    expected_variants = {"A", "B", "C", "D"}

    for model, variants in results_by_model.items():
        found_variants = set(variants.keys())
        n_variants = len(found_variants)
        missing = expected_variants - found_variants

        if n_variants < 2:
            errors.append(
                f"{model}: Only {n_variants} variant(s) found ({', '.join(sorted(found_variants))}). "
                f"Need at least 2 for bias analysis."
            )
        elif n_variants < 4:
            warnings.append(
                f"{model}: {n_variants}/4 variants ({', '.join(sorted(found_variants))}). "
                f"Missing: {', '.join(sorted(missing))}"
            )

    return {"errors": errors, "warnings": warnings}


def _serialize_report(obj):
    """Recursively convert numpy types to Python types for JSON serialization."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _serialize_report(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_report(v) for v in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _print_bias_summary_table(reports: dict) -> None:
    """Print a summary table of bias analysis results."""
    print("\n" + "=" * 100)
    print("POSITION BIAS SUMMARY")
    print("=" * 100)
    print(f"{'Model':<30} {'Overall':>8} {'A':>7} {'B':>7} {'C':>7} {'D':>7} {'Spread':>7} {'Bias?':>6}")
    print("-" * 100)

    # Sort by overall accuracy descending
    sorted_models = sorted(
        reports.items(),
        key=lambda x: x[1].overall_accuracy,
        reverse=True
    )

    for model, report in sorted_models:
        acc = report.accuracy_by_position
        spread = max(acc.values()) - min(acc.values())
        bias = "YES" if report.has_significant_bias else "no"

        print(
            f"{model:<30} "
            f"{report.overall_accuracy:>7.1%} "
            f"{acc.get('A', 0):>6.1%} "
            f"{acc.get('B', 0):>6.1%} "
            f"{acc.get('C', 0):>6.1%} "
            f"{acc.get('D', 0):>6.1%} "
            f"{spread:>6.1%} "
            f"{bias:>6}"
        )

    print("-" * 100)
    biased_count = sum(1 for r in reports.values() if r.has_significant_bias)
    print(f"Models with significant bias: {biased_count}/{len(reports)}")
    print("=" * 100)


def _build_comparison_dataframe(mcq_dir: Path, judged_dir: Path) -> "pd.DataFrame":
    """
    Build aligned MCQ/OSQ comparison DataFrame from lm-eval outputs and judged results.

    Args:
        mcq_dir: Base lm-eval output directory with MCQ results
        judged_dir: Directory containing judged OSQ results (*.judged.jsonl)

    Returns:
        DataFrame with columns: model, question_id, mcq_score, osq_score
    """
    import json
    import pandas as pd
    from metaeval.harness import LMEvalParser

    logger.info(f"Building comparison DataFrame from {mcq_dir} and {judged_dir}")

    # Collect MCQ results by model - average across position variants
    mcq_results = LMEvalParser.collect_mcq_by_variant(mcq_dir)

    if not mcq_results:
        logger.warning("No MCQ results found")
        return pd.DataFrame()

    # Build MCQ scores DataFrame (average across variants per question)
    mcq_rows = []
    for model, variants in mcq_results.items():
        # Aggregate by question across variants
        question_scores: dict[int, list[int]] = {}
        for variant, results in variants.items():
            for r in results:
                if r.question_id not in question_scores:
                    question_scores[r.question_id] = []
                question_scores[r.question_id].append(1 if r.is_correct else 0)

        # Average across variants
        for qid, scores in question_scores.items():
            mcq_rows.append({
                "model": model,
                "question_id": qid,
                "mcq_score": sum(scores) / len(scores),
            })

    mcq_df = pd.DataFrame(mcq_rows)
    logger.info(f"Loaded {len(mcq_df)} MCQ results from {len(mcq_results)} models")

    # Load judged OSQ results
    osq_rows = []
    judged_files = list(judged_dir.glob("*.judged.jsonl")) + list(judged_dir.glob("judged.jsonl"))

    if not judged_files:
        # Also check subdirectories (model-specific judged files)
        judged_files = list(judged_dir.glob("**/judged.jsonl"))

    for judged_file in judged_files:
        logger.info(f"Loading judged results from {judged_file}")
        with open(judged_file) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    # Extract model from path or item
                    model = item.get("model", judged_file.parent.name)
                    qid = item.get("question_id", item.get("doc_id"))
                    score = item.get("total_score", item.get("score", 0))

                    if qid is not None:
                        osq_rows.append({
                            "model": model,
                            "question_id": qid,
                            "osq_score": float(score),
                        })
                except json.JSONDecodeError:
                    continue

    if not osq_rows:
        logger.warning(f"No judged OSQ results found in {judged_dir}")
        return pd.DataFrame()

    osq_df = pd.DataFrame(osq_rows)
    logger.info(f"Loaded {len(osq_df)} OSQ judgments")

    # Normalize model names (lm-eval sanitizes with __)
    def normalize_model(name: str) -> str:
        return name.replace("__", ":").replace(":", "__")

    mcq_df["model_normalized"] = mcq_df["model"].apply(normalize_model)
    osq_df["model_normalized"] = osq_df["model"].apply(normalize_model)

    # Merge on normalized model and question_id
    merged = mcq_df.merge(
        osq_df,
        left_on=["model_normalized", "question_id"],
        right_on=["model_normalized", "question_id"],
        how="inner",
        suffixes=("", "_osq")
    )

    if merged.empty:
        # Try merging without model normalization
        logger.info("Normalized merge empty, trying direct merge...")
        merged = mcq_df.merge(
            osq_df,
            on=["model", "question_id"],
            how="inner",
        )

    if merged.empty:
        logger.warning("No aligned MCQ/OSQ data found after merge")
        logger.info(f"MCQ models: {mcq_df['model'].unique().tolist()}")
        logger.info(f"OSQ models: {osq_df['model'].unique().tolist()}")
        return pd.DataFrame()

    # Use the original model name from MCQ
    result = merged[["model", "question_id", "mcq_score", "osq_score"]].copy()
    logger.info(f"Built comparison DataFrame with {len(result)} aligned question-model pairs")

    return result


def _print_comparison_summary_table(reports: dict) -> None:
    """Print a summary table of format comparison results."""
    print("\n" + "=" * 110)
    print("MCQ vs OSQ COMPARISON SUMMARY")
    print("=" * 110)
    print(
        f"{'Model':<30} "
        f"{'MCQ':>8} "
        f"{'OSQ':>8} "
        f"{'Diff':>8} "
        f"{'Pearson':>9} "
        f"{'Spearman':>9} "
        f"{'Effect':>9} "
        f"{'N':>6}"
    )
    print("-" * 110)

    # Sort by MCQ accuracy descending
    sorted_models = sorted(
        reports.items(),
        key=lambda x: x[1].mcq_accuracy,
        reverse=True
    )

    for model, report in sorted_models:
        pearson = report.correlations.get("pearson")
        spearman = report.correlations.get("spearman")
        cohens = report.effect_sizes.get("cohens_d")

        pearson_str = f"{pearson.coefficient:.3f}" if pearson else "N/A"
        spearman_str = f"{spearman.coefficient:.3f}" if spearman else "N/A"
        effect_str = f"{cohens.value:.3f}" if cohens else "N/A"
        diff = report.mcq_accuracy - report.osq_normalized

        print(
            f"{model:<30} "
            f"{report.mcq_accuracy:>7.1%} "
            f"{report.osq_normalized:>7.1%} "
            f"{diff:>+7.1%} "
            f"{pearson_str:>9} "
            f"{spearman_str:>9} "
            f"{effect_str:>9} "
            f"{report.n_questions:>6}"
        )

    print("-" * 110)

    # Summary statistics
    avg_mcq = sum(r.mcq_accuracy for r in reports.values()) / len(reports)
    avg_osq = sum(r.osq_normalized for r in reports.values()) / len(reports)
    print(f"Average across {len(reports)} models: MCQ={avg_mcq:.1%}, OSQ={avg_osq:.1%}, Diff={avg_mcq-avg_osq:+.1%}")
    print("=" * 110)


def cmd_judge(args: argparse.Namespace) -> int:
    """Handle judge command."""
    import json
    from metaeval.judges import create_judge, get_default_model, JudgeSettings

    # Get model (use default if not specified)
    model = args.model or get_default_model(args.provider)

    # Check for resume
    resume = not args.no_resume
    enable_cache = not args.no_cache

    try:
        # Check if input is lm-eval output directory or file
        if args.input.is_dir():
            # Parse lm-eval OSQ output directory
            from metaeval.harness import LMEvalParser

            logger.info("Detected lm-eval output directory, parsing OSQ results...")
            parser = LMEvalParser(args.input)
            osq_results = parser.to_osq_results()

            if not osq_results:
                logger.error("No OSQ results found in directory")
                return 1

            # Convert to format expected by judge
            items = [
                {
                    "question_id": r.question_id,
                    "question": r.question,
                    "expected_answer": r.expected_answer,
                    "response": r.model_response,
                    "rubric": r.rubric,
                    "model": r.model,
                }
                for r in osq_results
            ]

            # Determine output path based on input directory
            output_path = args.output or (args.input / "judged.jsonl")
            evaluated_model = osq_results[0].model if osq_results else "unknown"
            logger.info(f"Loaded {len(items)} OSQ responses from model: {evaluated_model}")
        else:
            # Load from file
            with open(args.input) as f:
                if args.input.suffix == ".jsonl":
                    items = [json.loads(line) for line in f if line.strip()]
                else:
                    items = json.load(f)

            # Determine output path
            output_path = args.output or args.input.with_suffix(".judged.jsonl")

    except Exception as e:
        logger.error(f"Failed to load input: {e}")
        return 1

    logger.info(
        f"Running LLM-as-a-Judge on {args.input}\n"
        f"  Provider: {args.provider}\n"
        f"  Model: {model}\n"
        f"  Prompt: {args.prompt}\n"
        f"  Temperature: {args.temperature}\n"
        f"  Output: {output_path}\n"
        f"  Resume: {resume}\n"
        f"  Cache: {enable_cache}\n"
        f"  Items: {len(items)}"
    )

    try:

        # Create judge with settings
        settings = JudgeSettings(
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            prompt_style=args.prompt,
        )

        judge = create_judge(
            args.provider,
            model,
            settings=settings,
            enable_cache=enable_cache,
        )

        # Run batch with checkpointing
        results = judge.batch_judge(
            items,
            output_path=output_path,
            resume=resume,
        )

        # Log cache stats
        cache_stats = judge.get_cache_stats()
        if cache_stats["hits"] > 0 or cache_stats["misses"] > 0:
            logger.info(
                f"Cache stats: {cache_stats['hits']} hits, "
                f"{cache_stats['misses']} misses "
                f"({cache_stats['hit_rate']:.1%} hit rate)"
            )

        logger.info(f"Judged {len(results)} items. Results saved to {output_path}")
        return 0

    except Exception as e:
        logger.error(f"Judging failed: {e}")
        return 1


def cmd_prompts(args: argparse.Namespace) -> int:
    """Handle prompts command."""
    from metaeval.prompts import get_registry, get_prompt, add_prompt_path

    # Add custom path if provided
    if args.path:
        add_prompt_path(args.path)
        logger.info(f"Added prompt path: {args.path}")

    registry = get_registry()

    # Show specific prompt
    if args.show:
        category = args.category or "judge"
        prompt = get_prompt(args.show, category)
        if prompt is None:
            # Try the other category
            other = "convert" if category == "judge" else "judge"
            prompt = get_prompt(args.show, other)
            if prompt:
                category = other

        if prompt is None:
            logger.error(f"Prompt '{args.show}' not found")
            return 1

        print(f"\n{'='*60}")
        print(f"Name: {prompt.name}")
        print(f"Category: {prompt.category}")
        print(f"Version: {prompt.version}")
        print(f"Description: {prompt.description.strip()}")
        print(f"Variables: {', '.join(prompt.variables)}")
        print(f"{'='*60}")
        print("\nTemplate:")
        print("-" * 40)
        print(prompt.template)
        print("-" * 40)
        return 0

    # List prompts
    prompts = registry.list(args.category)

    if not prompts:
        logger.info("No prompts found. Add custom prompts with --path")
        return 0

    print("\nAvailable Prompts:")
    print("=" * 60)

    # Group by category
    by_category: dict[str, list] = {}
    for p in prompts:
        if p.category not in by_category:
            by_category[p.category] = []
        by_category[p.category].append(p)

    for category, cat_prompts in sorted(by_category.items()):
        print(f"\n[{category.upper()}]")
        for p in sorted(cat_prompts, key=lambda x: x.name):
            desc = p.description.split("\n")[0][:50] if p.description else ""
            print(f"  {p.name:<25} {desc}")

    print("\nUse --show NAME to view full prompt template")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Handle report command."""
    import json
    from metaeval.report.markdown import MarkdownReportGenerator

    logger.info(f"Generating report from {args.input}...")

    try:
        with open(args.input) as f:
            data = json.load(f)

        report = MarkdownReportGenerator(title=args.title)

        # Add sections based on data content
        for key, value in data.items():
            if isinstance(value, dict):
                import pandas as pd
                df = pd.DataFrame([value])
                report.add_table(df, title=key.replace("_", " ").title())
            else:
                report.add_section(key.replace("_", " ").title(), str(value))

        report.save(args.output)
        logger.info(f"Report saved to {args.output}")
        return 0

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return 1


def cmd_eval(args: argparse.Namespace) -> int:
    """Handle eval command - show lm-eval usage documentation."""
    examples = {
        "mcq": '''# Evaluate model on MCQ benchmark
lm_eval \\
  --model local-chat-completions \\
  --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \\
  --tasks ./sysengbench.yaml \\
  --output_path ./output \\
  --log_samples \\
  --batch_size auto''',

        "osq": '''# Evaluate model on OSQ (open-style) benchmark
lm_eval \\
  --model local-chat-completions \\
  --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \\
  --tasks ./sysengbench-osq.yaml \\
  --output_path ./output \\
  --log_samples \\
  --batch_size auto''',

        "bias": '''# Evaluate all position variants for bias analysis
lm_eval \\
  --model local-chat-completions \\
  --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \\
  --tasks ./sysengbench-a.yaml,./sysengbench-b.yaml,./sysengbench-c.yaml,./sysengbench-d.yaml \\
  --output_path ./output \\
  --log_samples \\
  --batch_size auto''',
    }

    print("""
metaeval does not wrap lm-eval for running evaluations.
Run lm-eval directly, then use metaeval to analyze results.

WORKFLOW
========
1. Run evaluation with lm-eval (see examples below)
2. View results: metaeval results list ./output/
3. Analyze:
   - Bias analysis:  metaeval analyze bias ./output/
   - Judge OSQ:      metaeval judge ./output/sysengbench-osq/model/

INSTALLATION
============
pip install lm-eval

DOCUMENTATION
=============
https://github.com/EleutherAI/lm-evaluation-harness
""")

    if args.example:
        print(f"\nEXAMPLE: {args.example.upper()}")
        print("=" * 50)
        print(examples[args.example])
    else:
        print("QUICK START (MCQ)")
        print("=" * 50)
        print(examples["mcq"])
        print("\nUse --example [mcq|osq|bias] for more examples.")

    return 0


def cmd_results(args: argparse.Namespace) -> int:
    """Handle results command - list and inspect lm-eval outputs."""
    import json
    from metaeval.harness import LMEvalParser, find_runs
    from metaeval.harness.discovery import list_models, list_tasks

    output_dir = args.path

    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        print(f"\nNo results found at {output_dir}")
        print("Run lm-eval first, or specify path: metaeval results list /path/to/output/")
        return 1

    if args.action == "list":
        runs = find_runs(output_dir, task_filter=args.task, model_filter=args.model)

        if not runs:
            print(f"No lm-eval runs found in {output_dir}")
            if args.task or args.model:
                print(f"  (filtered by task={args.task}, model={args.model})")
            return 0

        # Collect run info
        run_data = []
        for run_dir in runs:
            try:
                parser = LMEvalParser(run_dir)
                results = parser.results
                run_data.append({
                    "task": results.task_name,
                    "model": results.model_name_sanitized,
                    "accuracy": results.accuracy,
                    "n_samples": results.n_samples,
                    "variant": results.variant,
                    "path": str(run_dir),
                })
            except Exception as e:
                logger.warning(f"Failed to parse {run_dir}: {e}")

        if args.format == "json":
            print(json.dumps(run_data, indent=2))
        elif args.format == "csv":
            print("task,model,accuracy,n_samples,variant,path")
            for r in run_data:
                acc = f"{r['accuracy']:.4f}" if r['accuracy'] else "N/A"
                print(f"{r['task']},{r['model']},{acc},{r['n_samples']},{r['variant']},{r['path']}")
        else:  # table
            print(f"\nlm-eval Results in {output_dir}")
            print("=" * 90)
            print(f"{'Task':<20} {'Model':<25} {'Accuracy':>10} {'Samples':>8} {'Variant':>8}")
            print("-" * 90)
            for r in run_data:
                acc = f"{r['accuracy']:.2%}" if r['accuracy'] else "N/A"
                print(f"{r['task']:<20} {r['model']:<25} {acc:>10} {r['n_samples']:>8} {r['variant']:>8}")
            print("-" * 90)
            print(f"Total: {len(run_data)} runs")

    elif args.action == "summary":
        tasks = list_tasks(output_dir)
        models = list_models(output_dir)

        print(f"\nSummary of {output_dir}")
        print("=" * 50)
        print(f"Tasks:  {len(tasks)}")
        for t in tasks:
            print(f"  - {t}")
        print(f"\nModels: {len(models)}")
        for m in models:
            print(f"  - {m}")

    elif args.action == "show":
        # Show details for a specific run (first matching)
        runs = find_runs(output_dir, task_filter=args.task, model_filter=args.model)
        if not runs:
            print("No matching runs found")
            return 1

        run_dir = runs[0]
        parser = LMEvalParser(run_dir)
        run = parser.parse()

        print(f"\nRun Details: {run_dir}")
        print("=" * 60)
        print(f"Task:       {run.task}")
        print(f"Model:      {run.model}")
        print(f"Format:     {run.format}")
        print(f"Variant:    {run.variant or 'N/A'}")
        print(f"Accuracy:   {run.accuracy:.2%}" if run.accuracy else "Accuracy:   N/A")
        print(f"Samples:    {len(run.samples)}")
        print(f"Eval Time:  {run.results.eval_time_seconds:.1f}s")
        print(f"lm-eval:    {run.results.lm_eval_version}")

        if run.format == "osq" and run.samples:
            print(f"\nRubric:     {'Yes' if run.samples[0].to_osq_result(run.model).rubric else 'No'}")

    return 0


def cmd_config(args: argparse.Namespace) -> int:
    """Handle config command."""
    from metaeval.core.config import get_config, get_config_path, generate_default_config

    if args.action == "path":
        print(get_config_path())
        return 0

    elif args.action == "init":
        output_path = args.output or get_config_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        config_content = generate_default_config()
        with open(output_path, "w") as f:
            f.write(config_content)

        logger.info(f"Created config file at {output_path}")
        return 0

    else:  # show
        config = get_config()
        print("\nCurrent Configuration:")
        print("=" * 50)
        print(f"\n[Judge Settings]")
        print(f"  temperature: {config.judge.temperature}")
        print(f"  max_tokens: {config.judge.max_tokens}")
        print(f"  timeout: {config.judge.timeout}")
        print(f"  default_prompt: {config.judge.default_prompt}")
        print(f"  default_provider: {config.judge.default_provider}")

        print(f"\n[Stats Settings]")
        print(f"  alpha: {config.stats.alpha}")
        print(f"  bootstrap_iterations: {config.stats.bootstrap_iterations}")
        print(f"  confidence_level: {config.stats.confidence_level}")
        print(f"  random_seed: {config.stats.random_seed}")

        print(f"\n[Ollama Settings]")
        print(f"  host: {config.ollama.host}")
        print(f"  port: {config.ollama.port}")
        print(f"  default_model: {config.ollama.default_model}")
        print(f"  auto_pull: {config.ollama.auto_pull}")

        print(f"\n[Paths]")
        print(f"  data_dir: {config.paths.data_dir}")
        print(f"  cache_dir: {config.paths.cache_dir}")
        print(f"  output_dir: {config.paths.output_dir}")

        return 0


def app(args: list[str] | None = None) -> int:
    """Run the CLI application."""
    parser = create_parser()
    parsed = parser.parse_args(args)

    # Set up logging
    import logging
    level = logging.DEBUG if parsed.verbose else logging.INFO
    setup_logging(level=level)

    # Route to command handler
    handlers = {
        "download": cmd_download,
        "convert": cmd_convert,
        "variants": cmd_variants,
        "analyze": cmd_analyze,
        "judge": cmd_judge,
        "prompts": cmd_prompts,
        "report": cmd_report,
        "config": cmd_config,
        "eval": cmd_eval,
        "results": cmd_results,
    }

    if parsed.command is None:
        parser.print_help()
        return 0

    handler = handlers.get(parsed.command)
    if handler:
        return handler(parsed)
    else:
        parser.print_help()
        return 1


def main() -> None:
    """Main entry point."""
    sys.exit(app())


if __name__ == "__main__":
    main()

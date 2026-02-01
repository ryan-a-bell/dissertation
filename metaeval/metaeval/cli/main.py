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

            df = pd.read_csv(args.input)
            analyzer = PositionBiasAnalyzer(df)
            reports = analyzer.analyze_all_models()

            # Save results
            results = {m: r.to_dict() for m, r in reports.items()}

            if args.format == "json":
                with open(args.output / "bias_results.json", "w") as f:
                    json.dump(results, f, indent=2)
            elif args.format == "markdown":
                from metaeval.report.markdown import generate_summary_report
                report = generate_summary_report(bias_reports=reports)
                with open(args.output / "bias_report.md", "w") as f:
                    f.write(report)

        elif args.type == "compare":
            from metaeval.compare.analysis import FormatComparator

            df = pd.read_csv(args.input)
            comparator = FormatComparator(df)
            reports = comparator.analyze_all_models()

            results = {m: r.to_dict() for m, r in reports.items()}

            if args.format == "json":
                with open(args.output / "compare_results.json", "w") as f:
                    json.dump(results, f, indent=2)
            elif args.format == "markdown":
                from metaeval.report.markdown import generate_summary_report
                report = generate_summary_report(comparison_reports=reports)
                with open(args.output / "compare_report.md", "w") as f:
                    f.write(report)

        logger.info(f"Analysis complete. Results saved to {args.output}")
        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


def cmd_judge(args: argparse.Namespace) -> int:
    """Handle judge command."""
    import json
    from metaeval.judges import create_judge, get_default_model, JudgeSettings

    # Get model (use default if not specified)
    model = args.model or get_default_model(args.provider)

    # Determine output path
    output_path = args.output or args.input.with_suffix(".judged.jsonl")

    # Check for resume
    resume = not args.no_resume
    enable_cache = not args.no_cache

    logger.info(
        f"Running LLM-as-a-Judge on {args.input}\n"
        f"  Provider: {args.provider}\n"
        f"  Model: {model}\n"
        f"  Prompt: {args.prompt}\n"
        f"  Temperature: {args.temperature}\n"
        f"  Output: {output_path}\n"
        f"  Resume: {resume}\n"
        f"  Cache: {enable_cache}"
    )

    try:
        # Load input
        with open(args.input) as f:
            if args.input.suffix == ".jsonl":
                items = [json.loads(line) for line in f if line.strip()]
            else:
                items = json.load(f)

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

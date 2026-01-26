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
        default="llama3.1:8b",
        help="Judge model",
    )
    judge_parser.add_argument(
        "--provider",
        choices=["local", "openai", "anthropic"],
        default="local",
        help="Model provider",
    )
    judge_parser.add_argument(
        "--prompt",
        default="multi_dimensional",
        help="Judge prompt name (use 'metaeval prompts judge' to list)",
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

    logger.info(f"Running LLM-as-a-Judge on {args.input} using prompt '{args.prompt}'...")

    try:
        # Load input
        with open(args.input) as f:
            if args.input.suffix == ".jsonl":
                items = [json.loads(line) for line in f if line.strip()]
            else:
                items = json.load(f)

        if args.provider == "local":
            from metaeval.inference.local import OllamaJudge
            judge = OllamaJudge(model=args.model, prompt_style=args.prompt)
        else:
            # API-based judging would go here
            logger.error(f"Provider {args.provider} not yet implemented for judging")
            return 1

        results = judge.batch_judge(items)

        # Save results
        output_path = args.output or args.input.with_suffix(".judged.jsonl")
        with open(output_path, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")

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

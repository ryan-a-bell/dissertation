"""lm-eval output directory parser."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Literal

from metaeval.core.logging import get_logger
from metaeval.harness.results import LMEvalResults
from metaeval.harness.samples import LMEvalSample
from metaeval.parsers.mcq import MCQResult
from metaeval.parsers.osq import OSQResult

logger = get_logger(__name__)


@dataclass
class ParsedRun:
    """Parsed lm-eval run with results and samples."""

    results: LMEvalResults
    samples: list[LMEvalSample]
    task: str
    model: str
    format: Literal["mcq", "osq"]
    output_dir: Path | None = None

    @property
    def accuracy(self) -> float | None:
        """Get accuracy from results."""
        return self.results.accuracy

    @property
    def n_samples(self) -> int:
        """Get number of samples."""
        return len(self.samples)

    @property
    def variant(self) -> str:
        """Get position variant (A, B, C, D) for MCQ tasks."""
        return self.results.variant


class LMEvalParser:
    """
    Parse lm-eval output directories into metaeval types.

    Handles the output structure from lm-eval:
        output_dir/
            results_*.json (or results.json)
            samples_*.jsonl

    Example:
        parser = LMEvalParser("/path/to/output/sysengbench-a/llama3.3__70b/")
        mcq_results = parser.to_mcq_results()

        # For multiple runs:
        for run in LMEvalParser.parse_all("/path/to/output/"):
            print(f"{run.model}: {run.accuracy}")
    """

    def __init__(self, output_dir: Path | str):
        """
        Initialize parser with output directory.

        Args:
            output_dir: Path to lm-eval model output directory
                        (e.g., output/sysengbench-a/llama3.3__70b/)
        """
        self.output_dir = Path(output_dir)
        self._results: LMEvalResults | None = None
        self._samples: list[LMEvalSample] | None = None

    def _find_results_json(self) -> Path:
        """Find the results.json file in the output directory."""
        # Try timestamped results first
        results_files = list(self.output_dir.glob("results_*.json"))
        if results_files:
            # Return most recent
            return max(results_files, key=lambda p: p.stat().st_mtime)

        # Fall back to plain results.json
        plain = self.output_dir / "results.json"
        if plain.exists():
            return plain

        raise FileNotFoundError(f"No results.json found in {self.output_dir}")

    def _find_samples_jsonl(self) -> Path:
        """Find the samples.jsonl file in the output directory."""
        samples_files = list(self.output_dir.glob("samples_*.jsonl"))
        if samples_files:
            # Return most recent
            return max(samples_files, key=lambda p: p.stat().st_mtime)

        raise FileNotFoundError(f"No samples.jsonl found in {self.output_dir}")

    def _read_jsonl(self, path: Path) -> Iterator[dict]:
        """Read JSONL file line by line."""
        with open(path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    @property
    def results(self) -> LMEvalResults:
        """Get parsed results (cached)."""
        if self._results is None:
            results_path = self._find_results_json()
            self._results = LMEvalResults.from_json(results_path)
            logger.debug(f"Loaded results from {results_path}")
        return self._results

    @property
    def samples(self) -> list[LMEvalSample]:
        """Get parsed samples (cached)."""
        if self._samples is None:
            samples_path = self._find_samples_jsonl()
            self._samples = [
                LMEvalSample.from_json(line)
                for line in self._read_jsonl(samples_path)
            ]
            logger.debug(f"Loaded {len(self._samples)} samples from {samples_path}")
        return self._samples

    def _detect_format(self) -> Literal["mcq", "osq"]:
        """Detect MCQ vs OSQ from samples or task name."""
        # Check task name first
        if self.results.is_osq:
            return "osq"
        if self.results.is_mcq:
            return "mcq"

        # Fall back to sample inspection
        if self.samples:
            if self.samples[0].is_osq:
                return "osq"
        return "mcq"

    def parse(self) -> ParsedRun:
        """
        Parse results.json and samples.jsonl from output directory.

        Returns:
            ParsedRun with results and samples
        """
        return ParsedRun(
            results=self.results,
            samples=self.samples,
            task=self.results.task_name,
            model=self.results.model_name,
            format=self._detect_format(),
            output_dir=self.output_dir,
        )

    def to_mcq_results(self) -> list[MCQResult]:
        """
        Convert to metaeval MCQResult objects for bias analysis.

        Returns:
            List of MCQResult objects
        """
        run = self.parse()
        variant = run.variant
        model = run.model

        return [
            sample.to_mcq_result(model=model, variant=variant)
            for sample in run.samples
        ]

    def to_osq_results(self) -> list[OSQResult]:
        """
        Convert to metaeval OSQResult objects for judging.

        Returns:
            List of OSQResult objects
        """
        run = self.parse()
        model = run.model

        return [
            sample.to_osq_result(model=model)
            for sample in run.samples
        ]

    @classmethod
    def parse_all(
        cls,
        base_dir: Path | str,
        task_filter: str | None = None,
        model_filter: str | None = None,
    ) -> Iterator[ParsedRun]:
        """
        Parse all lm-eval output directories under a base directory.

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

        Yields:
            ParsedRun for each valid output directory
        """
        base_dir = Path(base_dir)

        for task_dir in sorted(base_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            if task_filter and task_filter not in task_dir.name:
                continue

            for model_dir in sorted(task_dir.iterdir()):
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
                    try:
                        parser = cls(model_dir)
                        yield parser.parse()
                    except Exception as e:
                        logger.warning(f"Failed to parse {model_dir}: {e}")

    @classmethod
    def collect_mcq_by_variant(
        cls,
        base_dir: Path | str,
        model_filter: str | None = None,
    ) -> dict[str, dict[str, list[MCQResult]]]:
        """
        Collect MCQ results organized by model and variant.

        Useful for position bias analysis across variants A, B, C, D.

        Args:
            base_dir: Base output directory
            model_filter: Only include models containing this string

        Returns:
            Nested dict: {model: {variant: [MCQResult, ...]}}
        """
        results: dict[str, dict[str, list[MCQResult]]] = {}

        for run in cls.parse_all(base_dir, model_filter=model_filter):
            if run.format != "mcq":
                continue

            model = run.model
            variant = run.variant or "A"

            if model not in results:
                results[model] = {}

            parser = cls(run.output_dir)
            results[model][variant] = parser.to_mcq_results()
            logger.info(f"Loaded {len(results[model][variant])} MCQ results for {model} variant {variant}")

        return results

    @classmethod
    def collect_osq(
        cls,
        base_dir: Path | str,
        model_filter: str | None = None,
    ) -> dict[str, list[OSQResult]]:
        """
        Collect OSQ results organized by model.

        Args:
            base_dir: Base output directory
            model_filter: Only include models containing this string

        Returns:
            Dict: {model: [OSQResult, ...]}
        """
        results: dict[str, list[OSQResult]] = {}

        for run in cls.parse_all(base_dir, task_filter="osq", model_filter=model_filter):
            if run.format != "osq":
                continue

            model = run.model
            parser = cls(run.output_dir)
            results[model] = parser.to_osq_results()
            logger.info(f"Loaded {len(results[model])} OSQ results for {model}")

        return results

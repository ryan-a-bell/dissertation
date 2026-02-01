"""
lm-eval harness output parsing module.

This module provides utilities for parsing lm-eval output files
(results.json and samples.jsonl) into metaeval types for analysis.

Example usage:
    from metaeval.harness import LMEvalParser

    parser = LMEvalParser("/path/to/output/sysengbench-a/llama3.3__70b/")
    mcq_results = parser.to_mcq_results()

    # Or for OSQ:
    parser = LMEvalParser("/path/to/output/sysengbench-osq/llama3.3__70b/")
    osq_results = parser.to_osq_results()
"""

from metaeval.harness.parser import LMEvalParser, ParsedRun
from metaeval.harness.results import LMEvalResults
from metaeval.harness.samples import LMEvalSample
from metaeval.harness.discovery import find_runs, find_latest_results

__all__ = [
    "LMEvalParser",
    "ParsedRun",
    "LMEvalResults",
    "LMEvalSample",
    "find_runs",
    "find_latest_results",
]

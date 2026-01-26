"""
metaeval - Meta-evaluation toolkit for LLM evaluation methods.

A Python library for meta-evaluating LLM benchmarks. Detect position bias in MCQs,
convert questions to open-ended format, run consensus LLM judging, and statistically
compare evaluation methods.
"""

__version__ = "0.1.0"

from metaeval import benchmark, bias, compare, judge, inference, report
from metaeval.core.config import Config
from metaeval.core.types import (
    MCQQuestion,
    OSQQuestion,
    GradingRubric,
    JudgmentResult,
    BiasResult,
    ComparisonResult,
)

__all__ = [
    "__version__",
    "benchmark",
    "bias",
    "compare",
    "judge",
    "inference",
    "report",
    "Config",
    "MCQQuestion",
    "OSQQuestion",
    "GradingRubric",
    "JudgmentResult",
    "BiasResult",
    "ComparisonResult",
]

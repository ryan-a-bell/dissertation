"""Benchmark preparation and transformation module."""

from metaeval.benchmark.download import (
    download_benchmark,
    load_benchmark,
    explode_categories,
    get_benchmark_stats,
)
from metaeval.benchmark.convert import MCQToOSQConverter, ConversionResult
from metaeval.benchmark.variants import (
    create_position_variants,
    rotate_choices,
    get_variant_stats,
)
from metaeval.benchmark.rubrics import (
    create_rubric,
    validate_rubric,
    parse_rubric_response,
)
from metaeval.benchmark.tasks import (
    generate_task_yaml,
    generate_mcq_task,
    generate_osq_task,
)
from metaeval.benchmark.schemas import (
    MCQQuestionSchema,
    OSQQuestionSchema,
    BenchmarkDataset,
)

__all__ = [
    # download
    "download_benchmark",
    "load_benchmark",
    "explode_categories",
    "get_benchmark_stats",
    # convert
    "MCQToOSQConverter",
    "ConversionResult",
    # variants
    "create_position_variants",
    "rotate_choices",
    "get_variant_stats",
    # rubrics
    "create_rubric",
    "validate_rubric",
    "parse_rubric_response",
    # tasks
    "generate_task_yaml",
    "generate_mcq_task",
    "generate_osq_task",
    # schemas
    "MCQQuestionSchema",
    "OSQQuestionSchema",
    "BenchmarkDataset",
]

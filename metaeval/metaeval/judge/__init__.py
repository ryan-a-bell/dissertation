"""LLM-as-a-Judge evaluation module."""

from metaeval.judge.prompts import (
    build_judge_prompt,
    BINARY_PROMPT,
    RUBRIC_PROMPT,
    MULTI_DIMENSIONAL_PROMPT,
    CHAIN_OF_THOUGHT_PROMPT,
)
from metaeval.judge.rubrics import (
    MultiDimensionalRubric,
    RubricDimension,
    create_default_rubric,
    validate_dimension_scores,
)
from metaeval.judge.scorer import (
    JudgeScorer,
    parse_judgment,
    extract_scores,
    extract_justification,
)
from metaeval.judge.consensus import (
    ConsensusScorer,
    majority_vote,
    mean_aggregation,
    median_aggregation,
)
from metaeval.judge.agreement import (
    cohens_kappa,
    pairwise_agreement,
)

# Note: fleiss_kappa, krippendorff_alpha, and intraclass_correlation
# remain available via direct import from metaeval.judge.agreement
# for advanced use or future versions.

__all__ = [
    # Prompts
    "build_judge_prompt",
    "BINARY_PROMPT",
    "RUBRIC_PROMPT",
    "MULTI_DIMENSIONAL_PROMPT",
    "CHAIN_OF_THOUGHT_PROMPT",
    # Rubrics
    "MultiDimensionalRubric",
    "RubricDimension",
    "create_default_rubric",
    "validate_dimension_scores",
    # Scorer
    "JudgeScorer",
    "parse_judgment",
    "extract_scores",
    "extract_justification",
    # Consensus
    "ConsensusScorer",
    "majority_vote",
    "mean_aggregation",
    "median_aggregation",
    # Agreement (aligned with dissertation methodology)
    "cohens_kappa",
    "pairwise_agreement",
]

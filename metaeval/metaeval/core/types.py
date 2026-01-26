"""Common type definitions for metaeval."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BloomsLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""

    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


@dataclass
class MCQQuestion:
    """Multiple-choice question data structure."""

    question_id: int
    question: str
    choices: dict[str, str]  # A, B, C, D -> choice text
    answer: str  # Correct answer letter
    justification: str
    incose_category: str
    tags: str = ""
    blooms_level: BloomsLevel | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "justification": self.justification,
            "incose_category": self.incose_category,
            "tags": self.tags,
            "blooms_level": self.blooms_level.value if self.blooms_level else None,
        }


@dataclass
class GradingRubric:
    """Grading rubric for open-style questions."""

    full_credit: str
    partial_credit: str
    no_credit: str
    blooms_level: BloomsLevel | None = None
    blooms_justification: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "full_credit": self.full_credit,
            "partial_credit": self.partial_credit,
            "no_credit": self.no_credit,
            "blooms_level": self.blooms_level.value if self.blooms_level else None,
            "blooms_justification": self.blooms_justification,
        }


@dataclass
class OSQQuestion:
    """Open-style question data structure."""

    question_id: int
    prompt: str
    expected_answer: str
    rubric: GradingRubric
    original_mcq: MCQQuestion | None = None
    incose_category: str = ""
    tags: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "prompt": self.prompt,
            "expected_answer": self.expected_answer,
            "rubric": self.rubric.to_dict(),
            "original_mcq": self.original_mcq.to_dict() if self.original_mcq else None,
            "incose_category": self.incose_category,
            "tags": self.tags,
        }


@dataclass
class DimensionScores:
    """Multi-dimensional rubric scores (5 dimensions, 20 points each)."""

    technical_accuracy: int  # 0-20
    conceptual_understanding: int  # 0-20
    completeness: int  # 0-20
    clarity_organization: int  # 0-20
    professional_relevance: int  # 0-20

    @property
    def total(self) -> int:
        """Total score out of 100."""
        return (
            self.technical_accuracy
            + self.conceptual_understanding
            + self.completeness
            + self.clarity_organization
            + self.professional_relevance
        )

    @property
    def percentage(self) -> float:
        """Score as percentage."""
        return self.total / 100.0

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "technical_accuracy": self.technical_accuracy,
            "conceptual_understanding": self.conceptual_understanding,
            "completeness": self.completeness,
            "clarity_organization": self.clarity_organization,
            "professional_relevance": self.professional_relevance,
            "total": self.total,
        }


@dataclass
class JudgmentResult:
    """Result from LLM-as-a-Judge evaluation."""

    question_id: int
    model_response: str
    judge_model: str
    scores: DimensionScores
    justification: str = ""
    raw_response: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "question_id": self.question_id,
            "model_response": self.model_response,
            "judge_model": self.judge_model,
            "scores": self.scores.to_dict(),
            "justification": self.justification,
        }


@dataclass
class TestResult:
    """Result from a statistical test."""

    test_name: str
    statistic: float
    p_value: float
    significant: bool
    alpha: float = 0.05
    additional_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "significant": self.significant,
            "alpha": self.alpha,
            **self.additional_info,
        }


@dataclass
class EffectSize:
    """Effect size measurement with interpretation."""

    measure: str  # e.g., "cramers_v", "cohens_d"
    value: float
    interpretation: str  # "small", "medium", "large"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "measure": self.measure,
            "value": self.value,
            "interpretation": self.interpretation,
        }


@dataclass
class BiasResult:
    """Result from position bias analysis."""

    model: str
    accuracy_by_position: dict[str, float]
    test_results: list[TestResult]
    effect_sizes: list[EffectSize]
    has_significant_bias: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "accuracy_by_position": self.accuracy_by_position,
            "test_results": [t.to_dict() for t in self.test_results],
            "effect_sizes": [e.to_dict() for e in self.effect_sizes],
            "has_significant_bias": self.has_significant_bias,
        }


@dataclass
class CorrelationResult:
    """Result from correlation analysis."""

    method: str  # "pearson" or "spearman"
    coefficient: float
    p_value: float
    n: int
    significant: bool
    alpha: float = 0.05

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method": self.method,
            "coefficient": self.coefficient,
            "p_value": self.p_value,
            "n": self.n,
            "significant": self.significant,
            "alpha": self.alpha,
        }


@dataclass
class BootstrapCI:
    """Bootstrap confidence interval."""

    statistic: str
    point_estimate: float
    ci_lower: float
    ci_upper: float
    confidence_level: float = 0.95
    n_iterations: int = 10000

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "statistic": self.statistic,
            "point_estimate": self.point_estimate,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "confidence_level": self.confidence_level,
            "n_iterations": self.n_iterations,
        }


@dataclass
class ComparisonResult:
    """Result from MCQ vs OSQ format comparison."""

    model: str
    mcq_accuracy: float
    osq_score: float
    correlation: CorrelationResult | None
    paired_test: TestResult | None
    effect_size: EffectSize | None
    bootstrap_ci: BootstrapCI | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "mcq_accuracy": self.mcq_accuracy,
            "osq_score": self.osq_score,
            "correlation": self.correlation.to_dict() if self.correlation else None,
            "paired_test": self.paired_test.to_dict() if self.paired_test else None,
            "effect_size": self.effect_size.to_dict() if self.effect_size else None,
            "bootstrap_ci": self.bootstrap_ci.to_dict() if self.bootstrap_ci else None,
        }

"""Multi-dimensional rubric definitions for LLM judging."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RubricDimension:
    """A single dimension of evaluation."""

    name: str
    description: str
    max_score: int = 20
    weight: float = 1.0
    criteria: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "max_score": self.max_score,
            "weight": self.weight,
            "criteria": self.criteria,
        }


# Default dimensions for systems engineering evaluation
DEFAULT_DIMENSIONS = [
    RubricDimension(
        name="technical_accuracy",
        description="Correctness of facts, principles, terminology, and technical details",
        max_score=20,
        criteria={
            "excellent": "All technical information is accurate and precise (18-20)",
            "good": "Minor technical errors that don't affect core understanding (14-17)",
            "adequate": "Some technical errors but core concepts are correct (10-13)",
            "poor": "Significant technical errors affecting understanding (5-9)",
            "failing": "Fundamental technical misunderstandings (0-4)",
        },
    ),
    RubricDimension(
        name="conceptual_understanding",
        description="Depth of understanding of systems engineering concepts and their relationships",
        max_score=20,
        criteria={
            "excellent": "Demonstrates deep understanding and can explain relationships (18-20)",
            "good": "Shows solid understanding with minor gaps (14-17)",
            "adequate": "Basic understanding demonstrated (10-13)",
            "poor": "Superficial or incomplete understanding (5-9)",
            "failing": "No demonstrated understanding (0-4)",
        },
    ),
    RubricDimension(
        name="completeness",
        description="Coverage of all required elements and aspects of the question",
        max_score=20,
        criteria={
            "excellent": "Addresses all aspects thoroughly (18-20)",
            "good": "Addresses most aspects with minor omissions (14-17)",
            "adequate": "Addresses core aspects, some omissions (10-13)",
            "poor": "Significant omissions (5-9)",
            "failing": "Major aspects not addressed (0-4)",
        },
    ),
    RubricDimension(
        name="clarity_organization",
        description="Quality of communication, logical structure, and presentation",
        max_score=20,
        criteria={
            "excellent": "Exceptionally clear, well-organized, easy to follow (18-20)",
            "good": "Clear and organized with minor issues (14-17)",
            "adequate": "Generally clear but could be better organized (10-13)",
            "poor": "Difficult to follow or poorly organized (5-9)",
            "failing": "Incoherent or incomprehensible (0-4)",
        },
    ),
    RubricDimension(
        name="professional_relevance",
        description="Real-world applicability and professional context",
        max_score=20,
        criteria={
            "excellent": "Strong connection to professional practice (18-20)",
            "good": "Good practical relevance (14-17)",
            "adequate": "Some practical relevance shown (10-13)",
            "poor": "Limited practical relevance (5-9)",
            "failing": "No connection to practice (0-4)",
        },
    ),
]


@dataclass
class MultiDimensionalRubric:
    """Multi-dimensional grading rubric."""

    dimensions: list[RubricDimension] = field(default_factory=lambda: DEFAULT_DIMENSIONS.copy())
    total_max_score: int = 100

    def __post_init__(self):
        """Validate total max score."""
        calculated_max = sum(d.max_score for d in self.dimensions)
        if calculated_max != self.total_max_score:
            self.total_max_score = calculated_max

    def get_dimension(self, name: str) -> RubricDimension | None:
        """Get a dimension by name."""
        for dim in self.dimensions:
            if dim.name == name:
                return dim
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimensions": [d.to_dict() for d in self.dimensions],
            "total_max_score": self.total_max_score,
        }

    def to_prompt_text(self) -> str:
        """Format rubric for inclusion in prompts."""
        lines = []
        for dim in self.dimensions:
            lines.append(f"**{dim.name.replace('_', ' ').title()}** (0-{dim.max_score})")
            lines.append(f"  {dim.description}")
            for level, desc in dim.criteria.items():
                lines.append(f"  - {level.title()}: {desc}")
            lines.append("")
        return "\n".join(lines)


def create_default_rubric() -> MultiDimensionalRubric:
    """Create the default multi-dimensional rubric."""
    return MultiDimensionalRubric()


def validate_dimension_scores(
    scores: dict[str, int],
    rubric: MultiDimensionalRubric | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate dimension scores against a rubric.

    Args:
        scores: Dictionary of dimension name to score
        rubric: Rubric to validate against (uses default if None)

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    if rubric is None:
        rubric = create_default_rubric()

    errors = []

    # Check all dimensions are present
    expected_dims = {d.name for d in rubric.dimensions}
    provided_dims = set(scores.keys())

    missing = expected_dims - provided_dims
    if missing:
        errors.append(f"Missing dimensions: {missing}")

    extra = provided_dims - expected_dims
    if extra:
        errors.append(f"Unexpected dimensions: {extra}")

    # Check score ranges
    for dim in rubric.dimensions:
        if dim.name in scores:
            score = scores[dim.name]
            if not isinstance(score, (int, float)):
                errors.append(f"{dim.name}: score must be numeric, got {type(score)}")
            elif score < 0:
                errors.append(f"{dim.name}: score cannot be negative ({score})")
            elif score > dim.max_score:
                errors.append(f"{dim.name}: score exceeds maximum ({score} > {dim.max_score})")

    return len(errors) == 0, errors


def calculate_total_score(
    scores: dict[str, int],
    rubric: MultiDimensionalRubric | None = None,
) -> int:
    """
    Calculate total score from dimension scores.

    Args:
        scores: Dictionary of dimension name to score
        rubric: Rubric for weighted calculation

    Returns:
        Total score
    """
    if rubric is None:
        return sum(scores.values())

    total = 0
    for dim in rubric.dimensions:
        if dim.name in scores:
            total += scores[dim.name] * dim.weight

    return int(total)


def score_to_grade(score: int, total: int = 100) -> str:
    """
    Convert numeric score to letter grade.

    Args:
        score: Numeric score
        total: Maximum possible score

    Returns:
        Letter grade
    """
    percentage = (score / total) * 100

    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


def score_to_credit(score: int, total: int = 100) -> str:
    """
    Convert numeric score to credit level.

    Args:
        score: Numeric score
        total: Maximum possible score

    Returns:
        Credit level (full, partial, none)
    """
    percentage = (score / total) * 100

    if percentage >= 80:
        return "full"
    elif percentage >= 40:
        return "partial"
    else:
        return "none"

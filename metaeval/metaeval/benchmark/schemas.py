"""Pydantic schemas for benchmark data validation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class MCQQuestionSchema(BaseModel):
    """Schema for validating MCQ questions."""

    question_id: int = Field(..., description="Unique question identifier")
    question: str = Field(..., min_length=1, description="Question text")
    choice_a: str = Field(..., description="Choice A text")
    choice_b: str = Field(..., description="Choice B text")
    choice_c: str = Field(..., description="Choice C text")
    choice_d: str = Field(..., description="Choice D text")
    answer: str = Field(..., pattern=r"^[A-D]$", description="Correct answer letter")
    justification: str = Field(default="", description="Answer justification")
    incose_category: str = Field(default="", description="INCOSE handbook category")
    tags: str = Field(default="", description="Additional tags")

    @property
    def choices(self) -> dict[str, str]:
        """Get choices as a dictionary."""
        return {
            "A": self.choice_a,
            "B": self.choice_b,
            "C": self.choice_c,
            "D": self.choice_d,
        }

    def format_as_prompt(self, include_answer: bool = False) -> str:
        """Format question as a prompt string."""
        prompt = f"{self.question}\n\n"
        prompt += f"A) {self.choice_a}\n"
        prompt += f"B) {self.choice_b}\n"
        prompt += f"C) {self.choice_c}\n"
        prompt += f"D) {self.choice_d}\n"
        if include_answer:
            prompt += f"\nAnswer: {self.answer}"
        return prompt

    model_config = {"extra": "allow"}


class GradingRubricSchema(BaseModel):
    """Schema for grading rubrics."""

    full_credit: str = Field(..., description="Criteria for full credit")
    partial_credit: str = Field(..., description="Criteria for partial credit")
    no_credit: str = Field(..., description="Criteria for no credit")
    blooms_level: str | None = Field(None, description="Bloom's taxonomy level")
    blooms_justification: str = Field(default="", description="Bloom's level justification")


class OSQQuestionSchema(BaseModel):
    """Schema for validating OSQ questions."""

    question_id: int = Field(..., description="Unique question identifier")
    osq_prompt: str = Field(..., min_length=1, description="Open-style question prompt")
    expected_answer: str = Field(..., description="Expected answer")
    rubric: GradingRubricSchema = Field(..., description="Grading rubric")
    original_question: str = Field(default="", description="Original MCQ question")
    original_answer: str = Field(default="", description="Original MCQ answer")
    incose_category: str = Field(default="", description="INCOSE handbook category")
    tags: str = Field(default="", description="Additional tags")
    conversion_score: int | None = Field(None, ge=1, le=10, description="Conversion suitability")

    def format_as_prompt(self) -> str:
        """Format question as a prompt string."""
        return self.osq_prompt

    model_config = {"extra": "allow"}


class BenchmarkDataset(BaseModel):
    """Schema for a complete benchmark dataset."""

    name: str = Field(..., description="Dataset name")
    version: str = Field(default="1.0.0", description="Dataset version")
    source: str = Field(default="", description="Dataset source (e.g., HuggingFace ID)")
    description: str = Field(default="", description="Dataset description")
    questions: list[MCQQuestionSchema | OSQQuestionSchema] = Field(
        default_factory=list, description="List of questions"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def num_questions(self) -> int:
        """Get number of questions."""
        return len(self.questions)

    @property
    def categories(self) -> list[str]:
        """Get unique categories."""
        cats = set()
        for q in self.questions:
            if hasattr(q, "incose_category") and q.incose_category:
                cats.add(q.incose_category)
        return sorted(cats)

    def filter_by_category(self, category: str) -> "BenchmarkDataset":
        """Filter questions by category."""
        filtered = [
            q for q in self.questions
            if hasattr(q, "incose_category") and q.incose_category == category
        ]
        return BenchmarkDataset(
            name=f"{self.name}_{category}",
            version=self.version,
            source=self.source,
            description=f"{self.description} (filtered: {category})",
            questions=filtered,
            metadata={**self.metadata, "filter": category},
        )

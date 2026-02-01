"""lm-eval samples.jsonl parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from metaeval.parsers.mcq import MCQResult
from metaeval.parsers.osq import OSQResult


@dataclass
class LMEvalSample:
    """
    Single sample from lm-eval samples.jsonl.

    Represents one question/response pair from an lm-eval run.
    Can be converted to MCQResult or OSQResult for metaeval analysis.
    """

    doc_id: int
    doc: dict[str, Any]
    target: str
    resps: list[Any] = field(default_factory=list)
    filtered_resps: list[Any] = field(default_factory=list)
    exact_match: float | None = None
    doc_hash: str = ""
    prompt_hash: str = ""

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "LMEvalSample":
        """
        Parse a single JSONL line from lm-eval samples output.

        Args:
            data: Dictionary from one line of samples.jsonl

        Returns:
            LMEvalSample instance
        """
        return cls(
            doc_id=data.get("doc_id", 0),
            doc=data.get("doc", {}),
            target=str(data.get("target", "")),
            resps=data.get("resps", []),
            filtered_resps=data.get("filtered_resps", []),
            exact_match=data.get("exact_match"),
            doc_hash=data.get("doc_hash", ""),
            prompt_hash=data.get("prompt_hash", ""),
        )

    @property
    def question_id(self) -> int:
        """Get question ID from doc or fall back to doc_id."""
        return self.doc.get("Question ID", self.doc_id)

    @property
    def is_correct(self) -> bool:
        """Check if model response was correct."""
        return self.exact_match == 1.0

    @property
    def model_answer(self) -> str:
        """Get model's answer from filtered_resps."""
        if self.filtered_resps:
            resp = self.filtered_resps[0]
            if isinstance(resp, str):
                return resp
            elif isinstance(resp, list) and resp:
                return str(resp[0])
        return ""

    @property
    def model_response(self) -> str:
        """Get full model response from resps (for OSQ)."""
        if self.resps:
            resp = self.resps[0]
            if isinstance(resp, list) and resp:
                return str(resp[0])
            elif isinstance(resp, str):
                return resp
        return ""

    def to_mcq_result(self, model: str, variant: str = "") -> MCQResult:
        """
        Convert to metaeval MCQResult.

        Args:
            model: Model name
            variant: Benchmark variant (A, B, C, D)

        Returns:
            MCQResult instance
        """
        return MCQResult(
            question_id=self.question_id,
            question=self.doc.get("question", ""),
            choices={
                "A": self.doc.get("choiceA", self.doc.get("choice_a", "")),
                "B": self.doc.get("choiceB", self.doc.get("choice_b", "")),
                "C": self.doc.get("choiceC", self.doc.get("choice_c", "")),
                "D": self.doc.get("choiceD", self.doc.get("choice_d", "")),
            },
            correct_answer=self.doc.get("answer", self.target),
            model_answer=self.model_answer,
            is_correct=self.is_correct,
            model=model,
            benchmark_variant=variant,
            raw_response=self.model_response,
        )

    def to_osq_result(self, model: str) -> OSQResult:
        """
        Convert to metaeval OSQResult.

        Args:
            model: Model name

        Returns:
            OSQResult instance
        """
        # Build rubric from doc fields
        rubric = None
        if any(k in self.doc for k in ["full_credit_criteria", "full_credit"]):
            rubric = {
                "full_credit": self.doc.get("full_credit_criteria", self.doc.get("full_credit", "")),
                "partial_credit": self.doc.get("partial_credit_criteria", self.doc.get("partial_credit", "")),
                "no_credit": self.doc.get("no_credit_criteria", self.doc.get("no_credit", "")),
            }

        return OSQResult(
            question_id=self.question_id,
            question=self.doc.get("osq_prompt", self.doc.get("question", "")),
            expected_answer=self.doc.get("expected_answer", self.target),
            model_response=self.model_response,
            model=model,
            rubric=rubric,
            raw_response=self.model_response,
        )

    @property
    def is_osq(self) -> bool:
        """Check if this sample is from an OSQ task."""
        return "osq_prompt" in self.doc or "expected_answer" in self.doc

    @property
    def is_mcq(self) -> bool:
        """Check if this sample is from an MCQ task."""
        return "choiceA" in self.doc or "choice_a" in self.doc

    @property
    def incose_category(self) -> str:
        """Get INCOSE category from doc."""
        return self.doc.get("INCOSE Handbook Category", "")

    @property
    def tags(self) -> str:
        """Get tags from doc."""
        return self.doc.get("Tags", "")

    @property
    def blooms_level(self) -> str:
        """Get Bloom's level from doc."""
        return self.doc.get("blooms_level", "")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "question_id": self.question_id,
            "target": self.target,
            "model_answer": self.model_answer,
            "is_correct": self.is_correct,
            "incose_category": self.incose_category,
            "tags": self.tags,
            "blooms_level": self.blooms_level,
        }

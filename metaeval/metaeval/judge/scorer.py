"""Score parsing and extraction from LLM judge responses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from metaeval.core.types import DimensionScores, JudgmentResult
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedJudgment:
    """Parsed judgment from LLM response."""

    scores: DimensionScores | None
    total_score: int
    justification: str
    credit_level: str  # "full", "partial", "none"
    raw_response: str
    parse_success: bool
    parse_errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scores": self.scores.to_dict() if self.scores else None,
            "total_score": self.total_score,
            "justification": self.justification,
            "credit_level": self.credit_level,
            "parse_success": self.parse_success,
            "parse_errors": self.parse_errors,
        }


class JudgeScorer:
    """Parse and extract scores from LLM judge responses."""

    def __init__(
        self,
        dimension_names: list[str] | None = None,
        max_score_per_dimension: int = 20,
        total_max_score: int = 100,
    ):
        """
        Initialize the scorer.

        Args:
            dimension_names: Names of scoring dimensions
            max_score_per_dimension: Maximum score per dimension
            total_max_score: Maximum total score
        """
        self.dimension_names = dimension_names or [
            "technical_accuracy",
            "conceptual_understanding",
            "completeness",
            "clarity_organization",
            "professional_relevance",
        ]
        self.max_per_dim = max_score_per_dimension
        self.total_max = total_max_score

    def parse(self, response: str) -> ParsedJudgment:
        """
        Parse a judge response to extract scores.

        Args:
            response: Raw LLM judge response

        Returns:
            ParsedJudgment with extracted scores
        """
        errors = []

        # Try JSON parsing first
        scores, json_errors = self._parse_json(response)
        if json_errors:
            errors.extend(json_errors)

        # Fall back to regex parsing
        if scores is None:
            scores, regex_errors = self._parse_regex(response)
            if regex_errors:
                errors.extend(regex_errors)

        # Extract justification
        justification = extract_justification(response)

        # Calculate total
        if scores:
            total_score = scores.total
        else:
            total_score = self._extract_total_fallback(response)

        # Determine credit level
        credit_level = self._determine_credit(total_score)

        return ParsedJudgment(
            scores=scores,
            total_score=total_score,
            justification=justification,
            credit_level=credit_level,
            raw_response=response,
            parse_success=scores is not None,
            parse_errors=errors,
        )

    def _parse_json(self, response: str) -> tuple[DimensionScores | None, list[str]]:
        """Try to parse scores from JSON in response."""
        errors = []

        # Find JSON object
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if not json_match:
            errors.append("No JSON object found in response")
            return None, errors

        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            errors.append(f"JSON parse error: {e}")
            return None, errors

        # Extract dimension scores
        dim_scores = {}
        for dim in self.dimension_names:
            if dim in data:
                try:
                    score = int(data[dim])
                    dim_scores[dim] = min(self.max_per_dim, max(0, score))
                except (ValueError, TypeError):
                    errors.append(f"Invalid score for {dim}: {data[dim]}")

        if len(dim_scores) == len(self.dimension_names):
            return DimensionScores(**dim_scores), errors

        errors.append(f"Missing dimensions: {set(self.dimension_names) - set(dim_scores.keys())}")
        return None, errors

    def _parse_regex(self, response: str) -> tuple[DimensionScores | None, list[str]]:
        """Try to parse scores using regex patterns."""
        errors = []
        dim_scores = {}

        patterns = {
            "technical_accuracy": r"technical\s*accuracy[:\s]*(\d+)",
            "conceptual_understanding": r"conceptual\s*understanding[:\s]*(\d+)",
            "completeness": r"completeness[:\s]*(\d+)",
            "clarity_organization": r"clarity[^:]*[:\s]*(\d+)",
            "professional_relevance": r"professional\s*relevance[:\s]*(\d+)",
        }

        response_lower = response.lower()

        for dim, pattern in patterns.items():
            match = re.search(pattern, response_lower)
            if match:
                try:
                    score = int(match.group(1))
                    dim_scores[dim] = min(self.max_per_dim, max(0, score))
                except ValueError:
                    errors.append(f"Could not parse score for {dim}")

        if len(dim_scores) == len(self.dimension_names):
            return DimensionScores(**dim_scores), errors

        if dim_scores:
            errors.append(f"Only found {len(dim_scores)}/{len(self.dimension_names)} dimensions")

        return None, errors

    def _extract_total_fallback(self, response: str) -> int:
        """Extract total score when dimension parsing fails."""
        patterns = [
            r"total[_\s]*score[:\s]*(\d+)",
            r"total[:\s]*(\d+)\s*/?\s*100",
            r"score[:\s]*(\d+)\s*/?\s*100",
            r"(\d+)\s*/\s*100",
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return min(100, max(0, int(match.group(1))))

        return 0

    def _determine_credit(self, total_score: int) -> str:
        """Determine credit level from total score."""
        percentage = total_score / self.total_max

        if percentage >= 0.8:
            return "full"
        elif percentage >= 0.4:
            return "partial"
        else:
            return "none"


def parse_judgment(response: str) -> ParsedJudgment:
    """
    Convenience function to parse a judge response.

    Args:
        response: Raw LLM judge response

    Returns:
        ParsedJudgment
    """
    scorer = JudgeScorer()
    return scorer.parse(response)


def extract_scores(response: str) -> dict[str, int] | None:
    """
    Extract dimension scores from response.

    Args:
        response: Raw LLM judge response

    Returns:
        Dictionary of dimension scores or None
    """
    judgment = parse_judgment(response)
    if judgment.scores:
        return judgment.scores.to_dict()
    return None


def extract_justification(response: str) -> str:
    """
    Extract justification text from response.

    Args:
        response: Raw LLM judge response

    Returns:
        Justification string
    """
    # Try JSON extraction
    try:
        json_match = re.search(r"\{[^{}]*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if "justification" in data:
                return data["justification"]
            if "reasoning" in data:
                return data["reasoning"]
    except json.JSONDecodeError:
        pass

    # Try pattern matching
    patterns = [
        r"justification[:\s]*[\"']?(.+?)[\"']?\s*(?:\}|$)",
        r"reasoning[:\s]*[\"']?(.+?)[\"']?\s*(?:\}|$)",
        r"explanation[:\s]*[\"']?(.+?)[\"']?\s*(?:\}|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

    return ""


def create_judgment_result(
    question_id: int,
    model_response: str,
    judge_model: str,
    parsed: ParsedJudgment,
) -> JudgmentResult:
    """
    Create a JudgmentResult from parsed judgment.

    Args:
        question_id: Question identifier
        model_response: Original model response being judged
        judge_model: Name of the judge model
        parsed: Parsed judgment

    Returns:
        JudgmentResult
    """
    return JudgmentResult(
        question_id=question_id,
        model_response=model_response,
        judge_model=judge_model,
        scores=parsed.scores or DimensionScores(0, 0, 0, 0, 0),
        justification=parsed.justification,
        raw_response=parsed.raw_response,
    )

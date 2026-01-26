"""Rubric creation and validation utilities."""

from __future__ import annotations

import json
import re
from typing import Any

from metaeval.core.types import GradingRubric, BloomsLevel
from metaeval.core.logging import get_logger

logger = get_logger(__name__)


# Default rubric templates by Bloom's level
RUBRIC_TEMPLATES = {
    BloomsLevel.REMEMBER: {
        "full_credit": "Correctly identifies the key term/concept with accurate definition",
        "partial_credit": "Partially correct identification with minor errors or incomplete definition",
        "no_credit": "Incorrect identification or no response",
    },
    BloomsLevel.UNDERSTAND: {
        "full_credit": "Demonstrates clear understanding of the concept with accurate explanation",
        "partial_credit": "Shows basic understanding but explanation lacks depth or has minor errors",
        "no_credit": "Demonstrates no understanding or provides incorrect explanation",
    },
    BloomsLevel.APPLY: {
        "full_credit": "Correctly applies the concept to the given scenario with appropriate reasoning",
        "partial_credit": "Applies concept but with incomplete reasoning or minor application errors",
        "no_credit": "Fails to apply concept correctly or provides irrelevant response",
    },
    BloomsLevel.ANALYZE: {
        "full_credit": "Provides thorough analysis with clear identification of relationships and components",
        "partial_credit": "Provides partial analysis missing key relationships or components",
        "no_credit": "Fails to analyze or provides superficial/incorrect analysis",
    },
    BloomsLevel.EVALUATE: {
        "full_credit": "Provides well-reasoned evaluation with clear criteria and justified conclusions",
        "partial_credit": "Provides evaluation but with unclear criteria or weak justification",
        "no_credit": "Fails to evaluate or provides unsupported judgments",
    },
    BloomsLevel.CREATE: {
        "full_credit": "Creates novel, appropriate solution that fully addresses requirements",
        "partial_credit": "Creates solution that partially addresses requirements or lacks originality",
        "no_credit": "Fails to create appropriate solution or simply restates existing information",
    },
}


def create_rubric(
    blooms_level: BloomsLevel | str | None = None,
    full_credit: str | None = None,
    partial_credit: str | None = None,
    no_credit: str | None = None,
    blooms_justification: str = "",
) -> GradingRubric:
    """
    Create a grading rubric.

    If specific criteria are not provided, uses templates based on Bloom's level.

    Args:
        blooms_level: Bloom's taxonomy level
        full_credit: Custom full credit criteria
        partial_credit: Custom partial credit criteria
        no_credit: Custom no credit criteria
        blooms_justification: Justification for Bloom's classification

    Returns:
        GradingRubric instance
    """
    # Convert string to BloomsLevel if needed
    if isinstance(blooms_level, str):
        try:
            blooms_level = BloomsLevel(blooms_level)
        except ValueError:
            logger.warning(f"Invalid Bloom's level: {blooms_level}, using None")
            blooms_level = None

    # Get template if available
    template = RUBRIC_TEMPLATES.get(blooms_level, {}) if blooms_level else {}

    return GradingRubric(
        full_credit=full_credit or template.get("full_credit", ""),
        partial_credit=partial_credit or template.get("partial_credit", ""),
        no_credit=no_credit or template.get("no_credit", ""),
        blooms_level=blooms_level,
        blooms_justification=blooms_justification,
    )


def validate_rubric(rubric: GradingRubric) -> tuple[bool, list[str]]:
    """
    Validate a grading rubric.

    Args:
        rubric: GradingRubric to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    if not rubric.full_credit or len(rubric.full_credit.strip()) < 10:
        errors.append("Full credit criteria is missing or too short")

    if not rubric.partial_credit or len(rubric.partial_credit.strip()) < 10:
        errors.append("Partial credit criteria is missing or too short")

    if not rubric.no_credit or len(rubric.no_credit.strip()) < 10:
        errors.append("No credit criteria is missing or too short")

    # Check for potential issues
    if rubric.full_credit and rubric.partial_credit:
        if rubric.full_credit.lower() == rubric.partial_credit.lower():
            errors.append("Full credit and partial credit criteria are identical")

    return len(errors) == 0, errors


def parse_rubric_response(response: str) -> GradingRubric | None:
    """
    Parse a rubric from an LLM response.

    Attempts to extract rubric information from various formats
    including JSON and structured text.

    Args:
        response: LLM response text

    Returns:
        GradingRubric if parsing succeeds, None otherwise
    """
    # Try JSON parsing first
    try:
        # Find JSON object in response
        json_match = re.search(r"\{[^{}]*\"rubric\"[^{}]*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            rubric_data = data.get("rubric", data)
            return GradingRubric(
                full_credit=rubric_data.get("full_credit", ""),
                partial_credit=rubric_data.get("partial_credit", ""),
                no_credit=rubric_data.get("no_credit", ""),
            )
    except json.JSONDecodeError:
        pass

    # Try structured text parsing
    full_match = re.search(r"full\s*credit[:\s]*(.+?)(?=partial|no\s*credit|$)", response, re.I | re.DOTALL)
    partial_match = re.search(r"partial\s*credit[:\s]*(.+?)(?=no\s*credit|full|$)", response, re.I | re.DOTALL)
    no_match = re.search(r"no\s*credit[:\s]*(.+?)(?=partial|full|$)", response, re.I | re.DOTALL)

    if full_match or partial_match or no_match:
        return GradingRubric(
            full_credit=full_match.group(1).strip() if full_match else "",
            partial_credit=partial_match.group(1).strip() if partial_match else "",
            no_credit=no_match.group(1).strip() if no_match else "",
        )

    logger.warning("Could not parse rubric from response")
    return None


def rubric_to_prompt(rubric: GradingRubric) -> str:
    """
    Format a rubric as a prompt section for LLM judging.

    Args:
        rubric: GradingRubric to format

    Returns:
        Formatted rubric string
    """
    prompt = "Grading Rubric:\n"
    prompt += f"- Full Credit: {rubric.full_credit}\n"
    prompt += f"- Partial Credit: {rubric.partial_credit}\n"
    prompt += f"- No Credit: {rubric.no_credit}\n"

    if rubric.blooms_level:
        prompt += f"\nCognitive Level: {rubric.blooms_level.value}"
        if rubric.blooms_justification:
            prompt += f" ({rubric.blooms_justification})"

    return prompt

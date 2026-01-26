"""Judge prompt templates for LLM-as-a-Judge evaluation."""

from __future__ import annotations

from typing import Literal

from metaeval.core.types import GradingRubric
from metaeval.prompts import get_prompt, list_prompts, get_registry


def format_rubric(rubric: GradingRubric | dict | None) -> str:
    """Format a rubric for inclusion in prompts."""
    if rubric is None:
        return "No specific rubric provided. Use your expertise to evaluate."

    if isinstance(rubric, dict):
        full = rubric.get("full_credit", "")
        partial = rubric.get("partial_credit", "")
        no = rubric.get("no_credit", "")
    else:
        full = rubric.full_credit
        partial = rubric.partial_credit
        no = rubric.no_credit

    lines = []
    if full:
        lines.append(f"- Full Credit: {full}")
    if partial:
        lines.append(f"- Partial Credit: {partial}")
    if no:
        lines.append(f"- No Credit: {no}")

    return "\n".join(lines) if lines else "No specific rubric provided."


def get_available_judge_prompts() -> list[str]:
    """
    Get list of available judge prompt names.

    Returns:
        List of prompt names that can be used with build_judge_prompt
    """
    return list_prompts("judge")


def build_judge_prompt(
    question: str,
    expected_answer: str,
    response: str,
    rubric: GradingRubric | dict | None = None,
    prompt_style: str = "multi_dimensional",
) -> str:
    """
    Build a judge prompt from components.

    Args:
        question: The question being evaluated
        expected_answer: The expected/model answer
        response: The student/model response to evaluate
        rubric: Optional grading rubric
        prompt_style: Style of prompt to use (from registry)

    Returns:
        Formatted prompt string

    Raises:
        ValueError: If prompt_style is not found in registry
    """
    # Get prompt from registry
    prompt_template = get_prompt(prompt_style, "judge")

    if prompt_template is None:
        available = get_available_judge_prompts()
        raise ValueError(
            f"Unknown prompt style: {prompt_style}. "
            f"Available: {available}"
        )

    rubric_text = format_rubric(rubric)

    # Build kwargs based on template variables
    kwargs = {
        "question": question,
        "expected_answer": expected_answer,
        "response": response,
        "rubric": rubric_text,
    }

    # Handle rubric-specific prompt that needs individual fields
    if "full_credit" in prompt_template.variables:
        if isinstance(rubric, dict):
            kwargs["full_credit"] = rubric.get("full_credit", "Demonstrates full understanding")
            kwargs["partial_credit"] = rubric.get("partial_credit", "Demonstrates partial understanding")
            kwargs["no_credit"] = rubric.get("no_credit", "Does not demonstrate understanding")
        elif rubric:
            kwargs["full_credit"] = rubric.full_credit or "Demonstrates full understanding"
            kwargs["partial_credit"] = rubric.partial_credit or "Demonstrates partial understanding"
            kwargs["no_credit"] = rubric.no_credit or "Does not demonstrate understanding"
        else:
            kwargs["full_credit"] = "Demonstrates full understanding"
            kwargs["partial_credit"] = "Demonstrates partial understanding"
            kwargs["no_credit"] = "Does not demonstrate understanding"

    return prompt_template.format(**kwargs)


def build_system_prompt(
    domain: str = "systems engineering",
    strictness: Literal["lenient", "moderate", "strict"] = "moderate",
) -> str:
    """
    Build a system prompt for the judge.

    Args:
        domain: Domain of expertise
        strictness: How strict the evaluation should be

    Returns:
        System prompt string
    """
    strictness_guidance = {
        "lenient": "Be generous in interpretation. Give credit for partial understanding and alternative valid approaches.",
        "moderate": "Balance rigor with fairness. Recognize valid alternative approaches but expect key concepts.",
        "strict": "Apply rigorous standards. Expect precise terminology and comprehensive coverage.",
    }

    return f"""You are an expert evaluator specializing in {domain} education and assessment.

Your role is to fairly and consistently evaluate student responses to technical questions.

Evaluation Guidelines:
- {strictness_guidance[strictness]}
- Focus on conceptual understanding, not just keyword matching
- Consider alternative valid approaches to answering
- Provide constructive feedback that could help improve understanding
- Be consistent in your scoring across similar responses

Always provide clear justification for your scores."""


# Legacy compatibility: Keep the old string constants for backwards compatibility
# These are now loaded from YAML files via the registry

def _get_legacy_prompt(name: str) -> str:
    """Get a prompt template string for legacy compatibility."""
    prompt = get_prompt(name, "judge")
    return prompt.template if prompt else ""


# Lazy-loaded legacy constants
class _LegacyPrompts:
    """Lazy loader for legacy prompt constants."""

    _cache: dict[str, str] = {}

    @classmethod
    def get(cls, name: str) -> str:
        if name not in cls._cache:
            cls._cache[name] = _get_legacy_prompt(name)
        return cls._cache[name]


# For backwards compatibility, expose as module-level attributes
def __getattr__(name: str) -> str:
    """Module-level attribute access for legacy prompt constants."""
    legacy_map = {
        "BINARY_PROMPT": "binary",
        "RUBRIC_PROMPT": "rubric",
        "MULTI_DIMENSIONAL_PROMPT": "multi_dimensional",
        "CHAIN_OF_THOUGHT_PROMPT": "chain_of_thought",
    }

    if name in legacy_map:
        return _LegacyPrompts.get(legacy_map[name])

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

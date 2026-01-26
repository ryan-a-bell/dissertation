"""Judge prompt templates for LLM-as-a-Judge evaluation."""

from __future__ import annotations

from typing import Literal

from metaeval.core.types import GradingRubric


# Binary correct/incorrect prompt
BINARY_PROMPT = """You are an expert evaluator for systems engineering questions. Evaluate whether the student's response is correct or incorrect.

Question: {question}

Expected Answer: {expected_answer}

Student Response: {response}

Evaluate the response and provide your judgment.

Respond in JSON format:
{{"judgment": "correct" or "incorrect", "justification": "<brief explanation>"}}"""


# Rubric-based (full/partial/no credit) prompt
RUBRIC_PROMPT = """You are an expert evaluator for systems engineering questions. Evaluate the student's response using the provided grading rubric.

Question: {question}

Expected Answer: {expected_answer}

Grading Rubric:
- Full Credit: {full_credit}
- Partial Credit: {partial_credit}
- No Credit: {no_credit}

Student Response: {response}

Evaluate the response according to the rubric.

Respond in JSON format:
{{"credit": "full", "partial", or "none", "score": <0-100>, "justification": "<explanation of grade>"}}"""


# Multi-dimensional scoring prompt (Lin & Chen 2023 style)
MULTI_DIMENSIONAL_PROMPT = """You are an expert evaluator for systems engineering education. Evaluate the student's response across five dimensions, scoring each from 0-20 points for a total of 100 points.

Question: {question}

Expected Answer: {expected_answer}

Grading Rubric:
{rubric}

Student Response: {response}

Evaluate the response across these five dimensions:

1. **Technical Accuracy (0-20)**: Correctness of facts, principles, terminology, and technical details.
2. **Conceptual Understanding (0-20)**: Depth of understanding of systems engineering concepts and their relationships.
3. **Completeness (0-20)**: Coverage of all required elements and aspects of the question.
4. **Clarity & Organization (0-20)**: Quality of communication, logical structure, and presentation.
5. **Professional Relevance (0-20)**: Real-world applicability and professional context.

Respond in JSON format:
{{
    "technical_accuracy": <0-20>,
    "conceptual_understanding": <0-20>,
    "completeness": <0-20>,
    "clarity_organization": <0-20>,
    "professional_relevance": <0-20>,
    "total_score": <0-100>,
    "justification": "<detailed explanation for each dimension>"
}}"""


# Chain-of-thought prompt
CHAIN_OF_THOUGHT_PROMPT = """You are an expert evaluator for systems engineering questions. Evaluate the student's response using careful step-by-step reasoning.

Question: {question}

Expected Answer: {expected_answer}

Grading Rubric:
{rubric}

Student Response: {response}

Please evaluate this response step by step:

1. First, identify the key concepts that should be addressed
2. Compare the student's response to the expected answer
3. Identify what is correct, partially correct, or missing
4. Consider the depth of understanding demonstrated
5. Assign scores for each dimension (0-20 each):
   - Technical Accuracy
   - Conceptual Understanding
   - Completeness
   - Clarity & Organization
   - Professional Relevance

Show your reasoning, then provide your final scores in JSON format:
{{
    "reasoning": "<step-by-step analysis>",
    "technical_accuracy": <0-20>,
    "conceptual_understanding": <0-20>,
    "completeness": <0-20>,
    "clarity_organization": <0-20>,
    "professional_relevance": <0-20>,
    "total_score": <0-100>,
    "justification": "<summary justification>"
}}"""


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


def build_judge_prompt(
    question: str,
    expected_answer: str,
    response: str,
    rubric: GradingRubric | dict | None = None,
    prompt_style: Literal["binary", "rubric", "multi_dimensional", "chain_of_thought"] = "multi_dimensional",
) -> str:
    """
    Build a judge prompt from components.

    Args:
        question: The question being evaluated
        expected_answer: The expected/model answer
        response: The student/model response to evaluate
        rubric: Optional grading rubric
        prompt_style: Style of prompt to use

    Returns:
        Formatted prompt string
    """
    rubric_text = format_rubric(rubric)

    if prompt_style == "binary":
        return BINARY_PROMPT.format(
            question=question,
            expected_answer=expected_answer,
            response=response,
        )

    elif prompt_style == "rubric":
        if isinstance(rubric, dict):
            full = rubric.get("full_credit", "Demonstrates full understanding")
            partial = rubric.get("partial_credit", "Demonstrates partial understanding")
            no = rubric.get("no_credit", "Does not demonstrate understanding")
        elif rubric:
            full = rubric.full_credit or "Demonstrates full understanding"
            partial = rubric.partial_credit or "Demonstrates partial understanding"
            no = rubric.no_credit or "Does not demonstrate understanding"
        else:
            full = "Demonstrates full understanding"
            partial = "Demonstrates partial understanding"
            no = "Does not demonstrate understanding"

        return RUBRIC_PROMPT.format(
            question=question,
            expected_answer=expected_answer,
            response=response,
            full_credit=full,
            partial_credit=partial,
            no_credit=no,
        )

    elif prompt_style == "multi_dimensional":
        return MULTI_DIMENSIONAL_PROMPT.format(
            question=question,
            expected_answer=expected_answer,
            response=response,
            rubric=rubric_text,
        )

    elif prompt_style == "chain_of_thought":
        return CHAIN_OF_THOUGHT_PROMPT.format(
            question=question,
            expected_answer=expected_answer,
            response=response,
            rubric=rubric_text,
        )

    else:
        raise ValueError(f"Unknown prompt style: {prompt_style}")


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

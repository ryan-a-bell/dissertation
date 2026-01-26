"""MCQ to OSQ conversion utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

from metaeval.core.logging import get_logger
from metaeval.core.types import GradingRubric, BloomsLevel

logger = get_logger(__name__)


CLASSIFICATION_PROMPT = """You are an expert in educational assessment and question design. Your task is to evaluate whether a multiple-choice question (MCQ) is suitable for conversion to an open-style question (OSQ).

Evaluate the following MCQ and provide:
1. A suitability score from 1-10 (where 10 is highly suitable for conversion)
2. A brief justification for your score

Criteria for high suitability:
- Question tests understanding, application, or analysis (not just recall)
- Answer requires explanation or reasoning
- Distractors are plausible and educational
- Question is not purely definitional or factual lookup

MCQ to evaluate:
Question: {question}
A) {choice_a}
B) {choice_b}
C) {choice_c}
D) {choice_d}
Correct Answer: {answer}
Justification: {justification}

Respond in JSON format:
{{"score": <1-10>, "justification": "<brief explanation>"}}"""


CONVERSION_PROMPT = """You are an expert in educational assessment for systems engineering. Convert the following multiple-choice question (MCQ) into an open-style question (OSQ) that tests the same knowledge but requires a written response.

Original MCQ:
Question: {question}
A) {choice_a}
B) {choice_b}
C) {choice_c}
D) {choice_d}
Correct Answer: {answer}
Justification: {justification}

Create:
1. An open-ended question that tests the same concept
2. A model answer (expected response)
3. A grading rubric with criteria for full credit, partial credit, and no credit
4. Bloom's taxonomy classification (Remember, Understand, Apply, Analyze, Evaluate, Create)

Respond in JSON format:
{{
    "osq_prompt": "<open-ended question>",
    "expected_answer": "<model answer>",
    "rubric": {{
        "full_credit": "<criteria for full credit>",
        "partial_credit": "<criteria for partial credit>",
        "no_credit": "<criteria for no credit>"
    }},
    "blooms_level": "<Bloom's level>",
    "blooms_justification": "<brief justification for Bloom's classification>"
}}"""


@dataclass
class ClassificationResult:
    """Result from suitability classification."""

    question_id: int
    score: int
    justification: str
    suitable: bool


@dataclass
class ConversionResult:
    """Result from MCQ to OSQ conversion."""

    question_id: int
    osq_prompt: str
    expected_answer: str
    rubric: GradingRubric
    blooms_level: BloomsLevel | None
    original_question: str
    original_answer: str
    conversion_score: int | None = None


class MCQToOSQConverter:
    """Convert MCQ questions to open-style questions using LLM."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: str | None = None,
        confidence_threshold: int = 7,
        temperature: float = 0.0,
    ):
        """
        Initialize the converter.

        Args:
            api_key: API key for the LLM provider
            model: Model to use for conversion
            base_url: Optional base URL for API (e.g., OpenRouter)
            confidence_threshold: Minimum score for conversion (1-10)
            temperature: Temperature for generation
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.temperature = temperature

    def _call_llm(self, prompt: str) -> dict[str, Any]:
        """Make an LLM API call and parse JSON response."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    def classify_suitability(
        self,
        question: str,
        choices: dict[str, str],
        answer: str,
        justification: str = "",
        question_id: int = 0,
    ) -> ClassificationResult:
        """
        Classify whether an MCQ is suitable for conversion.

        Args:
            question: Question text
            choices: Dictionary of choices (A, B, C, D)
            answer: Correct answer letter
            justification: Answer justification
            question_id: Question identifier

        Returns:
            ClassificationResult with score and justification
        """
        prompt = CLASSIFICATION_PROMPT.format(
            question=question,
            choice_a=choices.get("A", ""),
            choice_b=choices.get("B", ""),
            choice_c=choices.get("C", ""),
            choice_d=choices.get("D", ""),
            answer=answer,
            justification=justification,
        )

        result = self._call_llm(prompt)

        score = int(result.get("score", 0))
        return ClassificationResult(
            question_id=question_id,
            score=score,
            justification=result.get("justification", ""),
            suitable=score >= self.confidence_threshold,
        )

    def convert(
        self,
        question: str,
        choices: dict[str, str],
        answer: str,
        justification: str = "",
        question_id: int = 0,
        conversion_score: int | None = None,
    ) -> ConversionResult:
        """
        Convert an MCQ to OSQ format.

        Args:
            question: Question text
            choices: Dictionary of choices (A, B, C, D)
            answer: Correct answer letter
            justification: Answer justification
            question_id: Question identifier
            conversion_score: Pre-computed suitability score

        Returns:
            ConversionResult with OSQ prompt, answer, and rubric
        """
        prompt = CONVERSION_PROMPT.format(
            question=question,
            choice_a=choices.get("A", ""),
            choice_b=choices.get("B", ""),
            choice_c=choices.get("C", ""),
            choice_d=choices.get("D", ""),
            answer=answer,
            justification=justification,
        )

        result = self._call_llm(prompt)

        # Parse Bloom's level
        blooms_str = result.get("blooms_level", "")
        try:
            blooms_level = BloomsLevel(blooms_str)
        except ValueError:
            blooms_level = None

        # Parse rubric
        rubric_data = result.get("rubric", {})
        rubric = GradingRubric(
            full_credit=rubric_data.get("full_credit", ""),
            partial_credit=rubric_data.get("partial_credit", ""),
            no_credit=rubric_data.get("no_credit", ""),
            blooms_level=blooms_level,
            blooms_justification=result.get("blooms_justification", ""),
        )

        return ConversionResult(
            question_id=question_id,
            osq_prompt=result.get("osq_prompt", ""),
            expected_answer=result.get("expected_answer", ""),
            rubric=rubric,
            blooms_level=blooms_level,
            original_question=question,
            original_answer=f"{answer}) {choices.get(answer, '')}",
            conversion_score=conversion_score,
        )

    def batch_convert(
        self,
        df: pd.DataFrame,
        classify_first: bool = True,
        question_col: str = "question",
        answer_col: str = "answer",
        justification_col: str = "justification",
        progress: bool = True,
    ) -> tuple[list[ConversionResult], list[ClassificationResult]]:
        """
        Convert a batch of MCQ questions to OSQ format.

        Args:
            df: DataFrame with MCQ questions
            classify_first: Whether to classify suitability before converting
            question_col: Column name for question text
            answer_col: Column name for answer
            justification_col: Column name for justification
            progress: Whether to show progress bar

        Returns:
            Tuple of (conversion results, classification results)
        """
        conversions: list[ConversionResult] = []
        classifications: list[ClassificationResult] = []

        iterator = tqdm(df.iterrows(), total=len(df), disable=not progress)

        for idx, row in iterator:
            question_id = row.get("question_id", idx)
            question = row[question_col]
            answer = row[answer_col]
            justification = row.get(justification_col, "")

            # Get choices
            choices = {}
            for letter in ["A", "B", "C", "D"]:
                col = f"choice_{letter.lower()}"
                if col in row:
                    choices[letter] = row[col]

            conversion_score = None

            # Classify first if requested
            if classify_first:
                classification = self.classify_suitability(
                    question=question,
                    choices=choices,
                    answer=answer,
                    justification=justification,
                    question_id=question_id,
                )
                classifications.append(classification)

                if not classification.suitable:
                    continue

                conversion_score = classification.score

            # Convert to OSQ
            conversion = self.convert(
                question=question,
                choices=choices,
                answer=answer,
                justification=justification,
                question_id=question_id,
                conversion_score=conversion_score,
            )
            conversions.append(conversion)

        logger.info(
            f"Converted {len(conversions)} questions "
            f"({len(conversions)/len(df)*100:.1f}% conversion rate)"
        )

        return conversions, classifications


def conversions_to_dataframe(conversions: list[ConversionResult]) -> pd.DataFrame:
    """Convert a list of ConversionResults to a DataFrame."""
    records = []
    for c in conversions:
        records.append({
            "question_id": c.question_id,
            "osq_prompt": c.osq_prompt,
            "expected_answer": c.expected_answer,
            "full_credit": c.rubric.full_credit,
            "partial_credit": c.rubric.partial_credit,
            "no_credit": c.rubric.no_credit,
            "blooms_level": c.blooms_level.value if c.blooms_level else None,
            "blooms_justification": c.rubric.blooms_justification,
            "original_question": c.original_question,
            "original_answer": c.original_answer,
            "conversion_score": c.conversion_score,
        })
    return pd.DataFrame(records)

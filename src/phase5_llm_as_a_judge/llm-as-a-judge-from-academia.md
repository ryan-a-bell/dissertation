# === LLM Judge Prompts for OSQ Response Evaluation ===
# Three academic-grounded approaches for evaluating model responses to open-ended systems engineering questions

Summary of the Three LLM Judge Prompts:

Judge V1: Multi-Dimensional Reference-Based Evaluation
Academic Foundation: Lin & Chen (2023) LLM-Eval
Key Features:
- 5 SE-specific dimensions: Technical accuracy, conceptual understanding, completeness, clarity, professional relevance
- Reference-guided assessment using expected answers
- Structured scoring (0-10 scale per dimension)
- Domain expertise integration for systems engineering
- Best Use Cases: Comprehensive assessment of single responses, detailed feedback generation, rubric-based grading

Judge V2: Chain-of-Thought Reference-Guided Evaluation
Academic Foundation: Zheng et al. (2023) MT-Bench CoT + Liu et al. (2023) G-Eval
Key Features:
- 5-step systematic analysis process
- Expert reasoning demonstration before evaluation
- Bloom's taxonomy integration for cognitive level assessment
- Transparent evaluation process with step-by-step justification
- Best Use Cases: Deep analysis requiring expert reasoning, educational feedback, complex SE concept assessment

Judge V3: Pairwise Comparative Evaluation
Academic Foundation: Zheng et al. (2023) MT-Bench + Dubois et al. (2024) AlpacaEval
Key Features:
- Bias mitigation strategies (position, length bias prevention)
- Head-to-head comparison format
- Structured comparative analysis across multiple criteria
- Clear verdict system with confidence ratings
- Best Use Cases: Model ranking, benchmark evaluation, A/B testing of different models

Academic Validation:
Each prompt incorporates validated methodologies from peer-reviewed research:
- LLM-Eval: 93-98% correlation with human judgments
- MT-Bench: >80% agreement with expert human preferences
- AlpacaEval: High Spearman correlation (ρ≈0.93–0.98) with crowd preferences
- G-Eval: Improved alignment with human ratings through structured reasoning

All three prompts are domain-adapted for systems engineering with professional standards alignment and SE-specific evaluation criteria, ready for rigorous academic evaluation of your OSQ benchmark!

# -----------------------------
# PROMPT 1: Multi-Dimensional Reference-Based Evaluation
# Inspired by Lin & Chen (2023) LLM-Eval with Systems Engineering domain adaptation
# -----------------------------

JUDGE_PROMPT_V1_MULTIDIMENSIONAL = """You are an expert systems engineering educator evaluating student responses to open-ended questions. 

EVALUATION SCHEMA:
Rate the response on each dimension using a 0-10 scale where:
- 0-2: Inadequate (major errors, missing core concepts)
- 3-4: Below expectations (some understanding, significant gaps)
- 5-6: Meets expectations (adequate understanding, minor issues)
- 7-8: Exceeds expectations (strong understanding, well-articulated)
- 9-10: Exceptional (comprehensive, precise, professional-level)

DIMENSIONS TO EVALUATE:

1. TECHNICAL ACCURACY (0-10): Correctness of systems engineering concepts, terminology, and facts
2. CONCEPTUAL UNDERSTANDING (0-10): Depth of comprehension of underlying SE principles
3. COMPLETENESS (0-10): Coverage of key elements expected in the answer
4. CLARITY & ORGANIZATION (0-10): Logical structure and clear communication
5. PROFESSIONAL RELEVANCE (0-10): Connection to real-world SE practice and standards

QUESTION CONTEXT:
Original Question: {osq_question}
Expected Answer: {expected_answer}
Bloom's Level: {blooms_level}
SE Domain: {se_domain}

STUDENT RESPONSE TO EVALUATE:
{student_response}

INSTRUCTIONS:
1. Compare the student response against the expected answer and evaluation criteria
2. Consider the Bloom's taxonomy level when setting expectations
3. Account for the specific SE domain and professional standards
4. Provide brief justification for each dimension score
5. Output your evaluation in the specified JSON format

OUTPUT FORMAT (strict JSON):
{
  "technical_accuracy": {
    "score": <0-10>,
    "justification": "<1-2 sentences explaining the score>"
  },
  "conceptual_understanding": {
    "score": <0-10>, 
    "justification": "<1-2 sentences explaining the score>"
  },
  "completeness": {
    "score": <0-10>,
    "justification": "<1-2 sentences explaining the score>"
  },
  "clarity_organization": {
    "score": <0-10>,
    "justification": "<1-2 sentences explaining the score>"
  },
  "professional_relevance": {
    "score": <0-10>,
    "justification": "<1-2 sentences explaining the score>"
  },
  "overall_score": <average of all dimension scores>,
  "overall_assessment": "<holistic evaluation summary>",
  "key_strengths": "<main strengths identified>",
  "improvement_areas": "<specific areas for improvement>"
}
"""

# -----------------------------
# PROMPT 2: Chain-of-Thought Reference-Guided Evaluation  
# Inspired by Zheng et al. (2023) MT-Bench CoT approach with G-Eval (Liu et al., 2023) structured reasoning
# -----------------------------

JUDGE_PROMPT_V2_COT_REFERENCE = """You are an impartial expert systems engineering evaluator. You will assess a model's response to an open-ended systems engineering question using systematic chain-of-thought reasoning.

EVALUATION PROCESS:
1. First, independently analyze the question and formulate your own expert answer
2. Compare the expected reference answer with your analysis  
3. Evaluate the model's response against both your analysis and the reference
4. Provide step-by-step reasoning for your assessment
5. Assign a final score using the provided rubric

QUESTION AND CONTEXT:
Question: {osq_question}
Expected Reference Answer: {expected_answer}
Assessment Rubric:
- Full Credit Criteria: {full_credit_criteria}
- Partial Credit Criteria: {partial_credit_criteria}  
- No Credit Criteria: {no_credit_criteria}
Bloom's Taxonomy Level: {blooms_level}

MODEL RESPONSE TO EVALUATE:
{model_response}

STEP-BY-STEP ANALYSIS:

Step 1 - Independent Expert Analysis:
First, provide your own expert answer to the question, demonstrating the expected level of understanding for the given Bloom's taxonomy level.

Step 2 - Reference Answer Comparison:
Compare your expert analysis with the provided reference answer. Note any differences or additional insights.

Step 3 - Model Response Assessment:
Systematically evaluate the model's response by addressing:
a) Technical accuracy of systems engineering concepts
b) Completeness relative to expected answer scope
c) Appropriateness for the specified Bloom's level
d) Clarity and professional communication quality

Step 4 - Rubric Application:
Apply the provided rubric criteria to determine which category (full/partial/no credit) best fits the response.

Step 5 - Final Scoring:
Based on your analysis, assign a score and provide clear justification.

OUTPUT FORMAT (strict JSON):
{
  "step1_expert_analysis": "<your independent expert answer>",
  "step2_reference_comparison": "<comparison with reference answer>", 
  "step3_model_assessment": {
    "technical_accuracy": "<assessment of SE concept correctness>",
    "completeness": "<assessment of answer completeness>",
    "blooms_appropriateness": "<assessment of cognitive level match>",
    "clarity_quality": "<assessment of communication quality>"
  },
  "step4_rubric_application": "<which rubric category applies and why>",
  "step5_final_score": <numeric score 0-100>,
  "final_justification": "<comprehensive reasoning for the score>",
  "credit_category": "<full_credit|partial_credit|no_credit>"
}
"""

# -----------------------------
# PROMPT 3: Pairwise Comparative Evaluation
# Inspired by Zheng et al. (2023) MT-Bench and Dubois et al. (2024) AlpacaEval pairwise comparison
# -----------------------------

JUDGE_PROMPT_V3_PAIRWISE = """You are an expert systems engineering educator conducting a comparative evaluation of two model responses to the same open-ended question.

EVALUATION CRITERIA:
As an impartial judge, evaluate which response better demonstrates:
1. Technical accuracy in systems engineering concepts and terminology
2. Depth of understanding appropriate for the specified Bloom's taxonomy level  
3. Completeness in addressing the question requirements
4. Professional clarity and organization
5. Practical relevance to systems engineering practice

Avoid position bias - the order of responses does not indicate quality. Do not let response length alone influence your judgment. Focus on the substance and quality of the systems engineering content.

QUESTION CONTEXT:
Original Question: {osq_question}
Expected Answer: {expected_answer}
Bloom's Level: {blooms_level}
SE Assessment Focus: {se_focus_area}

RESPONSE A:
{response_a}

RESPONSE B:  
{response_b}

EVALUATION INSTRUCTIONS:
1. Begin by analyzing each response's technical accuracy and SE concept mastery
2. Assess how well each addresses the cognitive demands of the specified Bloom's level
3. Compare completeness relative to the expected answer scope
4. Evaluate professional communication quality and organization
5. Consider practical applicability to systems engineering work
6. Provide your comparative analysis and reasoning
7. Conclude with a clear verdict

Be as objective as possible. Consider that both responses may have strengths and weaknesses - your job is to determine which better fulfills the learning objectives for this systems engineering assessment.

OUTPUT FORMAT (strict JSON):
{
  "comparative_analysis": {
    "technical_accuracy": "<which response is more technically accurate and why>",
    "bloom_level_alignment": "<which response better matches the cognitive demands>", 
    "completeness": "<which response more completely addresses the question>",
    "professional_quality": "<which response demonstrates better SE communication>",
    "practical_relevance": "<which response is more applicable to SE practice>"
  },
  "response_a_strengths": "<key strengths of Response A>",
  "response_a_weaknesses": "<key weaknesses of Response A>", 
  "response_b_strengths": "<key strengths of Response B>",
  "response_b_weaknesses": "<key weaknesses of Response B>",
  "detailed_reasoning": "<comprehensive comparison justification>",
  "verdict": "[[A]]|[[B]]|[[TIE]]",
  "confidence": "<high|medium|low>",
  "margin": "<how close was the comparison?>"
}
"""

# -----------------------------
# Usage Functions for Each Prompt Variant
# -----------------------------

def evaluate_with_multidimensional_judge(osq_question, expected_answer, blooms_level, se_domain, student_response):
    """
    Use multi-dimensional evaluation (Prompt V1)
    Based on Lin & Chen (2023) LLM-Eval approach
    """
    prompt = JUDGE_PROMPT_V1_MULTIDIMENSIONAL.format(
        osq_question=osq_question,
        expected_answer=expected_answer, 
        blooms_level=blooms_level,
        se_domain=se_domain,
        student_response=student_response
    )
    return chat_json(prompt, temperature=0.1, max_tokens=1200)

def evaluate_with_cot_judge(osq_question, expected_answer, full_credit_criteria, 
                           partial_credit_criteria, no_credit_criteria, blooms_level, model_response):
    """
    Use chain-of-thought reference-guided evaluation (Prompt V2)
    Based on Zheng et al. (2023) MT-Bench CoT + G-Eval structured reasoning
    """
    prompt = JUDGE_PROMPT_V2_COT_REFERENCE.format(
        osq_question=osq_question,
        expected_answer=expected_answer,
        full_credit_criteria=full_credit_criteria,
        partial_credit_criteria=partial_credit_criteria, 
        no_credit_criteria=no_credit_criteria,
        blooms_level=blooms_level,
        model_response=model_response
    )
    return chat_json(prompt, temperature=0.1, max_tokens=1500)

def evaluate_with_pairwise_judge(osq_question, expected_answer, blooms_level, 
                                se_focus_area, response_a, response_b):
    """
    Use pairwise comparative evaluation (Prompt V3)
    Based on Zheng et al. (2023) MT-Bench + Dubois et al. (2024) AlpacaEval
    """
    prompt = JUDGE_PROMPT_V3_PAIRWISE.format(
        osq_question=osq_question,
        expected_answer=expected_answer,
        blooms_level=blooms_level,
        se_focus_area=se_focus_area,
        response_a=response_a,
        response_b=response_b
    )
    return chat_json(prompt, temperature=0.1, max_tokens=1400)

# -----------------------------
# Academic References and Validation Notes
# -----------------------------

"""
ACADEMIC FOUNDATION:

Prompt V1 (Multi-Dimensional):
- Based on Lin & Chen (2023) LLM-Eval unified multi-dimensional evaluation
- Incorporates domain-specific criteria for systems engineering
- Uses structured JSON output for reliable parsing
- Validated approach: LLM-Eval showed high correlation with human expert ratings

Prompt V2 (Chain-of-Thought):  
- Inspired by Zheng et al. (2023) MT-Bench CoT reasoning approach
- Incorporates G-Eval (Liu et al., 2023) step-by-step evaluation methodology
- Uses reference-guided assessment for improved accuracy
- Validated approach: CoT prompts improved evaluation quality on complex reasoning tasks

Prompt V3 (Pairwise):
- Based on Zheng et al. (2023) MT-Bench pairwise comparison framework
- Incorporates AlpacaEval (Dubois et al., 2024) bias mitigation strategies  
- Uses randomizable response ordering for fair comparison
- Validated approach: Pairwise evaluation achieved >80% agreement with human preferences

All prompts incorporate:
- Domain expertise in systems engineering education
- Bloom's taxonomy integration for cognitive assessment
- Bias mitigation strategies from academic literature
- Structured output formats for reliable evaluation parsing
"""
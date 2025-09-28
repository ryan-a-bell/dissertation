# === Polished MCQ→OSQ Prompt Variants ===
# Four alternative prompt strategies for improved classification and conversion

# -----------------------------
# VARIANT 1: Multi-Step Classification with Examples
# -----------------------------
CLASSIFIER_PROMPT_V1 = """You are an expert in educational assessment converting multiple-choice questions (MCQ) to open-ended short-answer questions (OSQ).

CONVERSION SUITABILITY SCORING (1-10 scale):

EXCELLENT CANDIDATES (9-10):
- Definitional questions: "What is the definition of systems engineering?"
- Mathematical problems: "Calculate the failure rate given 5 failures in 1000 hours"
- Process identification: "What are the five stages of risk management?"
- Clear factual recall with canonical answers

GOOD CANDIDATES (7-8):
- Conceptual understanding: "Explain the purpose of reliability block diagrams"
- Application scenarios: "How would you handle a high-risk technical component?"
- Compare/contrast with clear distinctions: "What distinguishes qualitative from quantitative risk analysis?"
- Minor context dependency, but core concept remains assessable

MARGINAL CANDIDATES (5-6):
- Some option dependency but convertible: "Which risk handling strategy is most appropriate for..."
- Requires significant rewording but concept is valid
- May need additional context to eliminate ambiguity

POOR CANDIDATES (3-4):
- Heavy reliance on option elimination: "All of the following are true EXCEPT..."
- Vague concepts that depend on seeing specific alternatives
- Ambiguous without multiple choice context

UNSUITABLE (1-2):
- Pure elimination-based: "Which of the following is NOT..."
- No standalone assessment possible
- Relies entirely on comparing given options

EVALUATION QUESTION:
{question}

Consider: Can this assess the intended learning objective without showing multiple choice options?

Return STRICT JSON:
{
  "suitability_score": <integer 1-10>,
  "justification": "<2-3 sentences explaining score with reference to criteria above>"
}
"""

# -----------------------------
# VARIANT 2: Chain-of-Thought Classification
# -----------------------------
CLASSIFIER_PROMPT_V2 = """You are an expert evaluating whether a multiple-choice question can be converted to an open-ended format. Use systematic analysis:

STEP 1 - CONCEPT INDEPENDENCE:
Can the core learning objective be assessed without showing answer choices?
Consider: Does the question test knowledge vs. elimination skills?

STEP 2 - ANSWER CANONICALITY:
Is there a definitive, expected answer?
Types: Definition, calculation, process steps, factual recall, reasoned explanation

STEP 3 - AMBIGUITY ASSESSMENT:
Would removing options create confusion about what's being asked?
Consider: Question clarity, scope definition, context sufficiency

STEP 4 - CONVERSION FEASIBILITY:
Can this be restated as a clear, focused open-ended question?
Consider: Length constraints, assessment validity, grading objectivity

ANALYZE THIS MCQ:
Question: {question}
Choices: {choices}
Correct Answer: {correct_choice}

Provide step-by-step analysis, then assign final suitability score (1-10).

Return STRICT JSON:
{
  "step1_independence": "<analysis of concept independence>",
  "step2_canonicality": "<analysis of answer definitiveness>", 
  "step3_ambiguity": "<analysis of potential confusion>",
  "step4_feasibility": "<analysis of conversion possibility>",
  "suitability_score": <integer 1-10>,
  "justification": "<final reasoning synthesis>"
}
"""

# -----------------------------
# VARIANT 3: Context-Aware Conversion
# -----------------------------
CONVERTER_PROMPT_V3 = """Convert this MCQ to an open-ended short-answer question using classification insights.

CLASSIFICATION CONTEXT:
- Suitability Score: {suitability_score}/10
- Reasoning: {classification_justification}

CONVERSION STRATEGY (adapt based on suitability score):

HIGH SUITABILITY (8-10):
- Minimal modification needed
- Direct removal of "which of the following" language
- Preserve core question structure

MODERATE SUITABILITY (7-8):
- Add context/constraints to reduce ambiguity
- Restructure for clarity without options
- May need to specify expected response format

LOWER SUITABILITY (5-6):
- Significant restructuring required
- Add substantial context to stand alone
- Focus on underlying concept, not option comparison

ORIGINAL MCQ:
Question: {question}
Choices: {choices}
Correct Answer: {correct_choice}
Explanation: {explanation}

DOMAIN: Systems Engineering

Create OSQ targeting the same learning objective with:
1. Clear, unambiguous question statement
2. Canonical expected answer
3. Detailed grading rubric (full/partial/no credit)
4. Appropriate Bloom's taxonomy classification

Return STRICT JSON:
{
  "osq_prompt": "<converted open-ended question>",
  "expected_answer": "<canonical correct response>",
  "rubric": {
    "full_credit": "<criteria and point allocation for complete answer>",
    "partial_credit": "<criteria and point allocation for incomplete but valid responses>",
    "no_credit": "<criteria for insufficient or incorrect responses>"
  },
  "blooms_level": "<Remember|Understand|Apply|Analyze|Evaluate|Create>",
  "blooms_justification": "<explanation for taxonomy level selection>",
  "conversion_notes": "<any challenges or adaptations made during conversion>"
}
"""

# -----------------------------
# VARIANT 4: Domain-Specific Systems Engineering
# -----------------------------
CLASSIFIER_PROMPT_V4 = """You are a systems engineering education expert evaluating MCQ→OSQ conversion suitability.

SYSTEMS ENGINEERING DOMAIN EXPERTISE:
- Core concepts: Risk management, reliability analysis, lifecycle processes, requirements engineering
- Methodologies: FMEA/FMECA, fault tree analysis, stakeholder analysis, verification & validation
- Applications: Aerospace, defense, complex system design and integration

DOMAIN-SPECIFIC SCORING RUBRIC:

EXCELLENT for SE (9-10):
- Technical definitions: "Define systems engineering" or "What is reliability?"
- Process methodologies: "Describe the steps in risk management planning"
- Calculation problems: "Calculate MTBF given failure rate data"
- Standard procedures: "What are the stages of the systems lifecycle?"

GOOD for SE (7-8):
- Conceptual applications: "Explain when to use fault tree analysis"
- Comparative analysis: "Compare series vs parallel reliability structures"
- Problem-solving scenarios: "How would you approach stakeholder analysis for..."
- Tool/method selection with clear criteria

MARGINAL for SE (5-6):
- Context-dependent applications: "Select the best risk handling strategy..."
- Scenario-based with multiple valid approaches
- Requires significant domain context to answer definitively

POOR for SE (3-4):
- Elimination-based SE concepts: "All are risk types EXCEPT..."
- Heavily option-dependent comparisons
- Vague scenarios without clear SE principles

UNSUITABLE for SE (1-2):
- Pure memorization of option lists
- Arbitrary distinctions not based on SE principles
- Cannot assess SE competency without multiple choices

EVALUATE THIS SYSTEMS ENGINEERING QUESTION:
{question}

Consider SE learning objectives: conceptual understanding, methodological knowledge, practical application.

Return STRICT JSON:
{
  "suitability_score": <integer 1-10>,
  "se_concept_category": "<risk_management|reliability|lifecycle|requirements|other>",
  "learning_objective": "<what SE competency this assesses>",
  "justification": "<domain-specific reasoning for score>"
}
"""

# -----------------------------
# VARIANT 4 COMPANION: Domain-Aware Conversion
# -----------------------------
CONVERTER_PROMPT_V4 = """Convert this systems engineering MCQ to OSQ format with domain expertise.

SYSTEMS ENGINEERING CONTEXT:
Question Category: {se_concept_category}
Learning Objective: {learning_objective}
Suitability: {suitability_score}/10

SE CONVERSION PRINCIPLES:
- Preserve technical terminology and precision
- Maintain alignment with SE standards (INCOSE, ISO 15288, etc.)
- Ensure assessment of SE competency, not just memorization
- Consider practical application in SE practice

ORIGINAL SE MCQ:
Question: {question}
Choices: {choices}
Correct Answer: {correct_choice}
Explanation: {explanation}

CONVERSION REQUIREMENTS:
1. Maintain SE technical accuracy and terminology
2. Create rubric reflecting SE professional competency levels
3. Map to Bloom's taxonomy appropriate for SE education
4. Ensure question assesses SE thinking, not just recall

Return STRICT JSON:
{
  "osq_prompt": "<SE-focused open-ended question>",
  "expected_answer": "<technically accurate SE response>",
  "rubric": {
    "full_credit": "<professional-level SE competency demonstrated>",
    "partial_credit": "<basic SE understanding with minor gaps>",
    "no_credit": "<insufficient SE knowledge or major errors>"
  },
  "blooms_level": "<Remember|Understand|Apply|Analyze|Evaluate|Create>",
  "blooms_justification": "<SE-specific reasoning for taxonomy level>",
  "se_standards_alignment": "<reference to relevant SE standards or practices>",
  "professional_relevance": "<how this relates to SE practice>"
}
"""

# -----------------------------
# Usage Examples for Each Variant
# -----------------------------

def use_variant_1(question):
    """Examples-based classification with clear scoring rubric"""
    prompt = CLASSIFIER_PROMPT_V1.format(question=question)
    return chat_json(prompt)

def use_variant_2(question, choices, correct_choice):
    """Chain-of-thought systematic analysis"""
    prompt = CLASSIFIER_PROMPT_V2.format(
        question=question, 
        choices=choices, 
        correct_choice=correct_choice
    )
    return chat_json(prompt)

def use_variant_3(question, choices, correct_choice, explanation, suitability_score, classification_justification):
    """Context-aware conversion using classification insights"""
    prompt = CONVERTER_PROMPT_V3.format(
        question=question,
        choices=choices,
        correct_choice=correct_choice,
        explanation=explanation,
        suitability_score=suitability_score,
        classification_justification=classification_justification
    )
    return chat_json(prompt)

def use_variant_4_classify(question):
    """Domain-specific SE classification"""
    prompt = CLASSIFIER_PROMPT_V4.format(question=question)
    return chat_json(prompt)

def use_variant_4_convert(question, choices, correct_choice, explanation, se_concept_category, learning_objective, suitability_score):
    """Domain-aware SE conversion"""
    prompt = CONVERTER_PROMPT_V4.format(
        question=question,
        choices=choices,
        correct_choice=correct_choice,
        explanation=explanation,
        se_concept_category=se_concept_category,
        learning_objective=learning_objective,
        suitability_score=suitability_score
    )
    return chat_json(prompt)
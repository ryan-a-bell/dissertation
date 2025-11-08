# Phase 5: LLM-as-a-Judge

This directory contains scripts and tools for Phase 5 of the dissertation pipeline: using LLM judges to evaluate OSQ (Open-ended Short-answer Question) responses.

## Overview

Phase 5 takes the raw OSQ responses from Phase 4 and grades them using LLM judges with academically-validated rubrics. The process includes:

1. **Processing OSQ outputs** to a standardized format
2. **LLM judging** using multiple rubric approaches
3. **Organizing results** by task/model for Phase 6 analysis

## Scripts

### `process_osq_for_judging.py`

Processes OSQ outputs from Phase 4 into a standardized format ready for LLM judging.

#### Usage

```bash
# Process all models
python src/phase5_llm_as_a_judge/process_osq_for_judging.py

# Process a specific model
python src/phase5_llm_as_a_judge/process_osq_for_judging.py --model gemma3__27b

# Custom paths
python src/phase5_llm_as_a_judge/process_osq_for_judging.py \
    --osq-output-dir path/to/osq/outputs \
    --osq-csv path/to/sysengbench_osq_filtered.csv \
    --output-dir path/to/output
```

#### Arguments

- `--osq-output-dir`: Directory containing Phase 4 OSQ outputs (default: `src/phase4_inference/downloaded_output/sysengbench-osq`)
- `--osq-csv`: Path to OSQ metadata CSV with rubrics (default: `src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv`)
- `--output-dir`: Output directory for processed files (default: `src/phase5_llm_as_a_judge/processed_osq_outputs`)
- `--model`: Process only this specific model (optional)

#### Output Format

The script generates:

1. **JSONL files** (one per model): `osq_for_judging_{model}.jsonl`
   - One JSON object per line for easy streaming
   - Each record contains:
     - Question metadata
     - Model response
     - Expected answer
     - Grading rubric (full/partial/no credit criteria)
     - Bloom's taxonomy level
     - INCOSE category

2. **JSON files** (one per model): `osq_for_judging_{model}.json`
   - Same content as JSONL but as a single JSON array
   - Convenient for loading all data at once

3. **Summary report**: `processing_summary.txt`
   - Overview of all processed models and response counts

#### Example Output Record

```json
{
  "task": "sysengbench-osq",
  "doc_id": 0,
  "question_id": 1,
  "model": "gemma3__27b",
  "question": "What best describes the concept of uncertainty...",
  "osq_prompt": "Define \"uncertainty\" in systems engineering...",
  "expected_answer": "A condition in which system outcomes...",
  "model_response": "In systems engineering, uncertainty refers to...",
  "rubric": {
    "full_credit_criteria": "3 points: The answer clearly states...",
    "partial_credit_criteria": "2 points: Mentions unpredictability...",
    "no_credit_criteria": "0 points: Describes different concepts..."
  },
  "blooms_level": "Remember",
  "incose_category": "INCOSEHandbook/Systems Engineering Overview/...",
  "tags": "Introduction to risk"
}
```

## Judging Approaches

The architecture documentation specifies four judging approaches:

### 1. Binary Correct/Incorrect

Simple yes/no judgment:
- Fast baseline assessment
- Limited nuance

### 2. Rubric-Based (from Phase 2 Conversion)

Uses the rubric generated during MCQ→OSQ conversion:
- **Full credit**: Meets all criteria
- **Partial credit**: Meets some criteria
- **No credit**: Fails key requirements

### 3. Multi-Dimensional Scoring (Lin & Chen 2023)

Five dimensions scored 0-10:
- **Technical Accuracy**: Correctness of facts, principles, terminology
- **Conceptual Understanding**: Depth of systems thinking
- **Completeness**: Coverage of required elements
- **Clarity**: Communication quality
- **Professional Relevance**: Real-world applicability

### 4. Chain-of-Thought (Zheng et al. 2023, G-Eval)

- Judge explains reasoning step-by-step
- Identifies strengths and weaknesses
- Provides final score with justification
- Higher human agreement (~85-98%)

## Directory Structure

```
phase5_llm_as_a_judge/
├── README.md                          # This file
├── process_osq_for_judging.py         # OSQ output processor
├── llm-judge.ipynb                    # Jupyter notebook for judging (to be created)
├── processed_osq_outputs/             # Processed outputs ready for judging
│   ├── model1/
│   │   ├── osq_for_judging_model1.jsonl
│   │   └── osq_for_judging_model1.json
│   ├── model2/
│   │   └── ...
│   └── processing_summary.txt
├── judged_outputs/                    # LLM judge results
│   ├── model1/
│   │   └── model1_judged.jsonl
│   └── model2/
│       └── model2_judged.jsonl
└── unused-rubrics/                    # Alternative rubric versions
    ├── llm_as_judge_rubric_1.md
    ├── llm_as_judge_rubric_2.md
    └── llm_as_judge_rubric_3.md
```

## Next Steps

After processing:

1. Review the processed outputs in `processed_osq_outputs/`
2. Run LLM judging (using `llm-judge.ipynb` or custom script)
3. Save judged results to `judged_outputs/` in the format expected by Phase 6
4. Proceed to Phase 6 analysis

## References

- Lin, Y., & Chen, H. (2023). Multi-dimensional evaluation framework for LLM-generated text.
- Zheng, L., et al. (2023). G-Eval: NLG evaluation using GPT-4 with better human alignment.

## Notes

- The script preserves all original metadata for traceability
- Output format is designed to match the MCQ evaluation structure for consistency
- All rubrics are based on academically-validated methodologies
- Temperature is set to 0.0 for deterministic judging

For more details, see the architecture documentation in `src/ARCHITECTURE_DIAGRAMS.md`.

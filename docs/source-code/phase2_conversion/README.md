# Phase 2: MCQ to OSQ Conversion

## Overview
This phase converts Multiple-Choice Questions (MCQ) to Open-Ended Short-Answer Questions (OSQ) using an LLM-based two-stage pipeline: classification to assess conversion suitability, followed by conversion with detailed rubrics and Bloom's taxonomy annotations.

## Purpose
Transform the SysEngBench MCQ dataset into an OSQ format to:
- Enable open-ended evaluation of LLM responses (avoiding MCQ-specific biases)
- Filter questions suitable for open-ended assessment
- Generate canonical expected answers and grading rubrics
- Classify questions by Bloom's taxonomy cognitive levels
- Create a high-quality OSQ benchmark for LLM evaluation

## Key Files

### Notebooks
- **`2.1_Converting_MCQ_to_OSQ.ipynb`** - Main conversion pipeline with two stages:
  1. **Classification Stage**: LLM scores each MCQ (1-10) for OSQ conversion suitability
  2. **Conversion Stage**: Converts suitable MCQs (score ≥7) to OSQ format with rubrics

### Documentation
- **`other-prompt-variants.md`** - Alternative prompt designs and variants explored during development

### Artifacts Directory (`artifacts_mcq2osq/`)
- **`sysengbench_osq.csv`** - Full output with all 1,144 questions (converted + rejected)
- **`sysengbench_osq_filtered.csv`** - Filtered dataset with only converted questions (845 questions)
- **`sysengbench_osq.jsonl`** - JSONL format of full output
- **`raw_queries/`** - Timestamped logs of all LLM prompts and responses
- **`question_jsons/`** - Individual JSON files per question (if generated)

## Configuration & Settings

### Environment Variables
- **`OPENROUTER_API_KEY`** - OpenRouter API key (required)
  - Store in `.env` file in project root
  - Used to access the GPT-5 model via OpenRouter

### Key Parameters (configured in notebook cell 2)
```python
MODEL = "openai/gpt-5"              # LLM model to use
CONFIDENCE_THRESHOLD = 7            # Minimum suitability score (1-10)
SAMPLE_N = 0                        # 0 = process all rows, >0 = sample size
MAX_TOKENS = 3000                   # Max response tokens
TEMPERATURE = 0.0                   # Deterministic responses
```

### Dependencies
```bash
pip install python-dotenv openai pandas tqdm
```

## Inputs
- **`../phase1_prep/sysengbench.csv`** - Raw MCQ dataset from Phase 1 (1,144 questions)
- `.env` file with `OPENROUTER_API_KEY`

## Outputs

### Primary Outputs
- **`artifacts_mcq2osq/sysengbench_osq_filtered.csv`** - 845 successfully converted OSQs with columns:
  - Original MCQ data (Question ID, Tags, INCOSE categories, choices, etc.)
  - Classification results (suitability_score, confidence_level, justification)
  - OSQ data (osq_prompt, expected_answer, rubric criteria, blooms_level, blooms_justification)

### Conversion Statistics
- Total questions processed: 1,144
- Questions converted: 845 (73.9%)
- Questions rejected: 299 (26.1%)
- Average suitability score: 7.53

### Output Schema
Each converted question includes:
- `osq_prompt` - Open-ended question text (MCQ artifacts removed)
- `expected_answer` - Canonical correct answer
- `full_credit_criteria` - Grading criteria for full points
- `partial_credit_criteria` - Grading criteria for partial credit
- `no_credit_criteria` - Disqualifying errors
- `blooms_level` - Bloom's taxonomy classification (Remember/Understand/Apply/Analyze/Evaluate/Create)
- `blooms_justification` - Rationale for taxonomy classification

## Usage

1. Ensure Phase 1 has been completed and `sysengbench.csv` exists
2. Set `OPENROUTER_API_KEY` in `.env` file
3. Update `CSV_IN` path in notebook cell 2 to point to your Phase 1 output
4. Configure conversion parameters (MODEL, CONFIDENCE_THRESHOLD, etc.)
5. Open `2.1_Converting_MCQ_to_OSQ.ipynb` in Jupyter
6. Run cells sequentially:
   - Setup and configuration
   - Run classifier (generates suitability scores)
   - Run converter (generates OSQ format)
   - Export to CSV/JSONL
7. Review outputs in `artifacts_mcq2osq/` directory

### Running with Sampling
For testing or cost control, set `SAMPLE_N` to process a subset:
```python
SAMPLE_N = 50  # Process only 50 random questions
```

## Conversion Rubric

### Suitability Scoring (1-10)
- **9-10 (Excellent)**: Clear canonical answer, minimal ambiguity, tight scope
- **7-8 (Good)**: Conceptual/application with crisp boundaries
- **5-6 (Marginal)**: Requires rewording, some option dependence
- **3-4 (Poor)**: Heavy option dependence, ambiguity
- **1-2 (Unsuitable)**: Cannot assess without multiple-choice options

### Conversion Rules
1. Remove all MCQ artifacts (letters, "which of the following", etc.)
2. Preserve original intent and difficulty
3. Require explicit canonical answer
4. Specify format (units, decimal places, sentence count)
5. Generate detailed grading rubric
6. Classify by Bloom's taxonomy

## Notes
- All LLM interactions are logged to timestamped files in `raw_queries/`
- JSON parsing errors are retried once with reminder prompt
- Failed conversions leave empty OSQ fields
- Visualizations included for suitability score distribution and category analysis
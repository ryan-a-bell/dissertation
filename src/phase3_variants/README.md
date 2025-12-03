# Phase 3: MCQ Golden Answer Variants

## Overview
This phase creates four variants of the SysEngBench MCQ dataset by systematically shifting the position of the correct (golden) answer to positions A, B, C, or D. This controls for position bias in LLM evaluation.

## Purpose
Generate position-controlled benchmark variants to:
- Test for position bias in LLM multiple-choice responses
- Enable controlled experiments comparing model performance across answer positions
- Support analysis of whether models exhibit preferences for certain choice positions (e.g., always choosing "A" or "C")
- Create balanced test sets where the correct answer appears equally in all positions

## Key Files

### Notebooks
- **`3.1_MCQ_Shift_Golden.ipynb`** - Implements the golden answer rotation algorithm and generates all four variants

### Generated Data Files
- **`sysengbench_a.csv`** - Variant where all correct answers are in position A (1,144 questions)
- **`sysengbench_b.csv`** - Variant where all correct answers are in position B (1,144 questions)
- **`sysengbench_c.csv`** - Variant where all correct answers are in position C (1,144 questions)
- **`sysengbench_d.csv`** - Variant where all correct answers are in position D (1,144 questions)

### Other Files
- **`.gitkeep`** - Ensures directory is tracked in git even when empty

## Configuration & Settings

### Dependencies
```bash
pip install pandas pathlib
```

### Parameters
No environment variables or API keys required. The notebook uses:
- Direct HuggingFace URL for data source: `https://huggingface.co/datasets/rabell/SysEngBench/resolve/main/test.csv`
- Automatic path resolution relative to notebook location

## Inputs
- **SysEngBench dataset** - Loaded directly from HuggingFace URL (can also use local `../phase1_prep/sysengbench.csv`)

## Outputs
Four CSV files, each containing 1,144 questions with identical content but different answer positions:

### File Structure
Each variant maintains the original schema:
- `Question ID` - Unique identifier (1-1144)
- `Tags` - Question category tags
- `INCOSE Handbook Category` - INCOSE classification
- `question` - Question text (unchanged)
- `choiceA`, `choiceB`, `choiceC`, `choiceD` - Answer choices (rotated)
- `answer` - Correct answer letter (A, B, C, or D depending on variant)
- `label` - Numeric label (0=A, 1=B, 2=C, 3=D)
- `Justification` - Explanation for correct answer

### Transformation Logic
For each question, the algorithm:
1. Identifies current correct answer position (A/B/C/D)
2. Calculates rotation needed to move it to target position
3. Rotates all four choices by the calculated shift
4. Updates `answer` field to target letter
5. Updates `label` field to corresponding index (0-3)

## Usage

1. Open `3.1_MCQ_Shift_Golden.ipynb` in Jupyter
2. Run all cells sequentially
3. The notebook will:
   - Load SysEngBench dataset from HuggingFace
   - Generate four variants (A, B, C, D)
   - Save CSV files to `src/phase3_variants/`
   - Display preview of first row from each variant
4. Verify outputs by checking that:
   - All variants have 1,144 rows
   - Each variant's first question shows correct answer in expected position

## Example Transformation

Original question (correct answer = B):
```
Question: What best describes uncertainty?
A) Process improvement...
B) Condition where outcomes are unknown... [CORRECT]
C) Cost-benefit analysis...
D) System integration...
answer: B, label: 1
```

After transformation to Variant A:
```
Question: What best describes uncertainty?
A) Condition where outcomes are unknown... [CORRECT - shifted from B]
B) Cost-benefit analysis... [shifted from C]
C) System integration... [shifted from D]
D) Process improvement... [shifted from A]
answer: A, label: 0
```

## Verification
The notebook includes a verification cell that displays the first row from each variant to confirm the rotation worked correctly. The correct answer should appear in:
- Variant A: position A (label=0)
- Variant B: position B (label=1)
- Variant C: position C (label=2)
- Variant D: position D (label=3)

## Use Cases
These variants enable research questions such as:
- Do models exhibit position bias (e.g., preferring choice A)?
- Does answer position affect model confidence scores?
- How does accuracy vary when correct answers are distributed across positions?
- Are certain question types more susceptible to position effects?
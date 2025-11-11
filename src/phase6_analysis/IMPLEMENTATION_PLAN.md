# Phase 6 Analysis - Implementation Plan

## Data Inventory Summary

### Phase 4 MCQ Data
**Location:** `src/phase4_inference/downloaded_output/`

| Variant         | gemma3__4b | gemma3__27b | Notes |
|-----------------|------------|-------------|-------|
| sysengbench     | 2 files    | 2 files     | Base variant (appears to be same as variant A) |
| sysengbench-a   | 2 files    | 2 files     | Position variant A |
| sysengbench-b   | 2 files    | 2 files     | Position variant B |
| sysengbench-c   | 2 files    | 2 files     | Position variant C |
| sysengbench-d   | 1 file     | 1 file      | Position variant D |
| sysengbench-osq | 1 file     | 1 file      | Open short questions (raw, not judged) |

**Models:** gemma3__4b, gemma3__27b
**Thinking models:** None in current dataset (DeepSeek-R1:7b, QwQ:32b mentioned but not present)

### Phase 5 Judged OSQ Data
**Location:** `src/phase5_llm_as_a_judge/sysengbench-osq-llm-judge/`

- **Models:** gemma3__4b, gemma3__27b
- **Judge:** openai_gpt-5 (single judge)
- **Files:** `samples_sysengbench-osq_<timestamp>__openai_gpt-5.jsonl`

### Data Missing Analysis
- **sysengbench vs sysengbench-a:** Need to verify if these are duplicates or different
- **Multiple timestamps:** Most variants have 2 files (different runs); need to select most recent or merge
- **Thinking models:** No thinking model data currently available (DeepSeek-R1:7b, QwQ:32b not present)

---

## Data Structure Details

### Phase 4 MCQ Sample Structure
```json
{
  "doc_id": 0,
  "doc": {
    "Question ID": 1,
    "Tags": "Introduction to risk",
    "INCOSE Handbook Category": "INCOSEHandbook/.../...",
    "question": "What best describes...",
    "choiceA": "...",
    "choiceB": "...",
    "choiceC": "...",
    "choiceD": "...",
    "answer": "A",
    "label": 0,
    "Justification": "..."
  },
  "target": "A",
  "resps": [["A"]],
  "filtered_resps": ["A"],
  "exact_match": 1.0
}
```

**Key Fields:**
- `doc["Question ID"]`: Unique question identifier (1-286)
- `doc["answer"]`: Correct answer letter (changes per variant!)
- `doc["INCOSE Handbook Category"]`: Question category
- `exact_match`: 1.0 (correct) or 0.0 (incorrect)
- `filtered_resps[0]`: Model's parsed answer

### Phase 5 Judged OSQ Sample Structure
```json
{
  "sample_id": 0,
  "phase4_row": {
    "doc_id": 0,
    "doc": {
      "Question ID": 1,
      "osq_prompt": "Define \"uncertainty\" in systems engineering...",
      "expected_answer": "...",
      "full_credit_criteria": "...",
      "partial_credit_criteria": "...",
      "no_credit_criteria": "...",
      "blooms_level": "Remember"
    },
    "resps": [["In systems engineering, ..."]],
    "filtered_resps": ["In systems engineering, ..."]
  },
  "judge": {
    "fields": {
      "technical_accuracy": {"score": 19, "justification": "..."},
      "conceptual_understanding": {"score": 19, "justification": "..."},
      "completeness": {"score": 18, "justification": "..."},
      "clarity_organization": {"score": 18, "justification": "..."},
      "professional_relevance": {"score": 20, "justification": "..."}
    },
    "total_score": 94,
    "max_score": 100,
    "percentage": 94.0
  }
}
```

**Key Fields:**
- `phase4_row.doc["Question ID"]`: Links to MCQ via Question ID
- `phase4_row.resps[0][0]`: Model's OSQ response
- `judge.fields.*`: Multi-dimensional scoring (each out of 20)
- `judge.total_score`: Sum of all field scores (out of 100)

---

## Implementation Strategy

### Design Decisions (Agreed Upon)

1. **Thinking models:** Parse but flag with `is_thinking_model` column. Most will be incomplete (2000 token cutoff). Run analyses both with/without.
2. **OSQ judging:** Single judge (openai_gpt-5) for now. Aggregate fields to total_score.
3. **Missing data:** Identify which model-variant combinations are missing. Add user-controllable `missing_data_strategy` parameter (drop/impute).
4. **Statistical tests:** α = 0.05, **no Bonferroni correction** (per user preference).

### Phase 1: Data Parsing Functions

#### 1.1 MCQ Parser
**File:** Add to `results-processing.ipynb`

```python
def parse_mcq_samples(variant_dir_path, model_name, variant_name):
    """
    Parse MCQ samples from phase 4.

    Returns: DataFrame with columns:
        - model: str
        - question_id: int
        - variant: str (a/b/c/d)
        - category: str (INCOSE category)
        - tags: str
        - correct_answer: str (A/B/C/D)
        - model_answer: str
        - is_correct: bool
        - raw_response: str (full model output)
    """
```

**Logic:**
- Use most recent timestamp file if multiple exist
- Extract `Question ID` from `doc`
- Map variant letter (a/b/c/d) based on directory name
- Parse `exact_match` for correctness
- Handle edge cases (missing fields, malformed responses)

#### 1.2 OSQ Parser
**File:** Add to `results-processing.ipynb`

```python
def parse_osq_judged_samples(judged_file_path, model_name):
    """
    Parse judged OSQ samples from phase 5.

    Returns: DataFrame with columns:
        - model: str
        - question_id: int
        - osq_prompt: str
        - expected_answer: str
        - model_response: str
        - judge_model: str (openai_gpt-5)
        - technical_accuracy: int (0-20)
        - conceptual_understanding: int (0-20)
        - completeness: int (0-20)
        - clarity_organization: int (0-20)
        - professional_relevance: int (0-20)
        - total_score: int (0-100)
        - percentage: float
        - is_correct: bool (e.g., total_score >= 70)
        - blooms_level: str
    """
```

**Logic:**
- Extract judge name from filename (`__openai_gpt-5.jsonl`)
- Parse all 5 scoring dimensions
- Calculate total_score (sum of 5 fields)
- Define `is_correct` threshold (e.g., >= 70/100 or >= 60/100, TBD)
- Link to Question ID via `phase4_row.doc["Question ID"]`

#### 1.3 Thinking Model Handler
**File:** Add to `results-processing.ipynb`

```python
def detect_thinking_model(model_name, response_text):
    """
    Identify thinking models and flag incomplete responses.

    Returns: dict with:
        - is_thinking_model: bool
        - is_truncated: bool (response ends abruptly)
        - thinking_block_present: bool (<think> tags detected)
    """
```

**Logic:**
- Check model name against known thinking models: `DeepSeek-R1:7b`, `QwQ:32b`
- Scan for `<think>` or `</think>` tags
- Detect truncation (ends mid-sentence, token count near 2000)
- Flag for exclusion analysis

---

### Phase 2: Data Alignment

#### 2.1 Question ID Standardization
- **Issue:** Position variants (a/b/c/d) shuffle answer choices
- **Solution:** Use `doc["Question ID"]` as primary key (1-286)
- **Validation:** Ensure same Question ID across variants has same question text

#### 2.2 MCQ-OSQ Alignment Function
```python
def align_mcq_osq_results(mcq_df, osq_df, missing_data_strategy='drop'):
    """
    Merge MCQ and OSQ results by question_id.

    Parameters:
        missing_data_strategy: 'drop' (remove incomplete) or 'impute' (fill NaN)

    Returns: DataFrame with columns:
        - model
        - question_id
        - category
        - tags
        - blooms_level
        - mcq_a_correct: bool
        - mcq_b_correct: bool
        - mcq_c_correct: bool
        - mcq_d_correct: bool
        - mcq_avg_correct: float (average across variants)
        - osq_total_score: int
        - osq_is_correct: bool
        - is_thinking_model: bool
    """
```

**Logic:**
- Pivot MCQ data: one row per (model, question_id) with 4 columns for variants
- Outer join MCQ with OSQ on (model, question_id)
- Handle missing: drop rows or impute with variant average

---

### Phase 3: Statistical Analyses

#### 3.1 Position Bias Analysis
**Tests:**
- Chi-square test: Uniform distribution of answers across A/B/C/D?
- ANOVA: Do accuracies differ significantly by position?
- McNemar's test: Pairwise position comparisons

**Visualizations:**
- Heatmap: models × positions (accuracy)
- Bar chart: position effect aggregated across models

#### 3.2 MCQ vs OSQ Comparison
**Tests:**
- Paired t-test: MCQ avg vs OSQ score (per model-question)
- Wilcoxon signed-rank test: Non-parametric alternative
- Bootstrap 95% CIs: Robust confidence intervals
- Cohen's d: Effect size

**Visualizations:**
- Side-by-side bar chart: MCQ vs OSQ accuracy per model
- Scatter plot: MCQ accuracy (x) vs OSQ score (y) with regression line
- Violin plots: Distribution comparison

#### 3.3 Advanced Analyses
**Question-level consistency:**
- Correlation: Do hard MCQs predict hard OSQs?
- Scatter: MCQ error rate vs OSQ error rate by question

**Category breakdown:**
- Performance by INCOSE category
- Box plots by category

**Model effects:**
- Model size impact (4b vs 27b)
- Thinking vs non-thinking (if data available)

**Statistical rigor:**
- Permutation tests for non-parametric significance
- Effect sizes (Cohen's d, Hedges' g)
- Power analysis
- No Bonferroni correction (per user preference)

---

### Phase 4: Visualization & Reporting

#### 4.1 Key Visualizations
1. **Position bias heatmap** (models × variants)
2. **MCQ vs OSQ bar chart** (side-by-side per model)
3. **MCQ vs OSQ scatter** (with regression + CI band)
4. **Distribution plots** (violin/box plots by modality)
5. **Category breakdown** (bar charts by INCOSE category)
6. **Effect size forest plot** (Cohen's d with CIs)

#### 4.2 Summary Tables
1. **Overall accuracy table** (models × modalities)
2. **Position bias results** (chi-square p-values, effect sizes)
3. **MCQ vs OSQ comparison** (mean diff, CIs, p-values, Cohen's d)
4. **Top/bottom performers** (by modality)

#### 4.3 Exports
- `master_dataframe.csv`: Aligned MCQ-OSQ data
- `statistical_results.json`: All test outputs
- `summary_report.md`: Human-readable summary

---

## Implementation Checklist

### Immediate Next Steps
- [ ] Write `parse_mcq_samples()` function
- [ ] Write `parse_osq_judged_samples()` function
- [ ] Determine correctness threshold for OSQ (e.g., >= 70/100)
- [ ] Verify sysengbench vs sysengbench-a (duplicate check)
- [ ] Select file selection strategy (most recent timestamp)
- [ ] Write `align_mcq_osq_results()` function
- [ ] Implement missing data handling (drop/impute parameter)

### Data Validation
- [ ] Confirm all Question IDs match across variants
- [ ] Check for duplicate samples (multiple runs)
- [ ] Verify judge scores sum to total_score
- [ ] Identify any missing model-variant combinations

### Analysis Implementation
- [ ] Position bias tests (chi-square, ANOVA, McNemar)
- [ ] MCQ vs OSQ tests (t-test, Wilcoxon, bootstrap CIs, Cohen's d)
- [ ] Question-level correlation analysis
- [ ] Category-specific breakdown
- [ ] Generate all visualizations

### Documentation & Export
- [ ] Generate summary statistics table
- [ ] Create all plots (save as PNG/PDF)
- [ ] Export master dataframe
- [ ] Write statistical summary report
- [ ] Document findings and interpretations

---

## File Structure

```
src/phase6_analysis/
├── results-processing.ipynb          # Main analysis notebook
├── IMPLEMENTATION_PLAN.md            # This file
└── outputs/                          # To be created
    ├── master_dataframe.csv
    ├── mcq_samples.csv
    ├── osq_samples.csv
    ├── statistical_results.json
    ├── summary_report.md
    └── figures/
        ├── position_bias_heatmap.png
        ├── mcq_vs_osq_bar.png
        ├── mcq_vs_osq_scatter.png
        ├── effect_size_forest.png
        └── category_breakdown.png
```

---

## Open Questions

1. **OSQ correctness threshold:** What score constitutes "correct"? Options:
   - >= 70/100 (70% = C grade)
   - >= 60/100 (60% = passing)
   - >= 80/100 (80% = B grade)
   - **Recommendation:** Use >= 70 as primary, sensitivity analysis with 60 and 80

2. **File selection:** When multiple timestamps exist, which to use?
   - Most recent (recommended)
   - Average across runs
   - Both (flag duplicates)

3. **sysengbench vs sysengbench-a:** Are these duplicates?
   - Need to compare Question IDs and answers
   - If duplicate, exclude `sysengbench` to avoid double-counting

4. **Thinking model analysis:** Since no data currently exists:
   - Build infrastructure but skip for now
   - Add placeholder for future integration

---

## Timeline Estimate

1. **Parsing (2-3 hours):** MCQ parser, OSQ parser, data loading
2. **Alignment (1-2 hours):** Merge function, missing data handling
3. **Analysis (3-4 hours):** Statistical tests, correlation analyses
4. **Visualization (2-3 hours):** All plots, formatting
5. **Reporting (1-2 hours):** Summary tables, markdown report

**Total: 9-14 hours** of focused implementation time

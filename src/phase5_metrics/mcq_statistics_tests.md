
# Statistical Tests for Comparing LLM Performance on MCQs

This document summarizes appropriate statistical tests for evaluating and comparing Large Language Models (LLMs) on multiple-choice question (MCQ) datasets, including both binary correctness and continuous outputs such as log probabilities.

---

## 1. Binary Outcomes (Correct / Incorrect)

### ✅ Two Models
- **Test**: **McNemar’s Test**
- **Use Case**: Paired binary outcomes (same MCQs for both LLMs).
- **Null Hypothesis**: No difference in proportions of correct answers.
- **Caveat**: If discordant pairs (only one model gets it right) are few, use the **exact binomial version**.

### ✅ Three or More Models
- **Test**: **Cochran’s Q Test**
- **Use Case**: Binary outcomes (correct/incorrect) for 3+ LLMs on the same MCQs.
- **Null Hypothesis**: All models have the same proportion of correct answers.
- **Follow-Up**: If significant, conduct pairwise McNemar tests with multiple testing correction.

---

## 2. Continuous Outcomes (e.g., Log Probabilities)

### ✅ Two Models
- **Test**: **Paired t-Test**
- **Use Case**: Log probabilities or continuous scores for same MCQs across 2 LLMs.
- **Assumptions**:
  - Differences in scores are normally distributed.
- **Alternative**: **Wilcoxon Signed-Rank Test** (if normality is violated).

### ✅ Three or More Models
- **Test**: **Repeated-Measures ANOVA**
- **Use Case**: Comparing log probabilities across 3+ LLMs for same MCQs.
- **Assumptions**:
  - Normality and sphericity (equal variances of differences).
- **Alternative**: **Friedman Test** (non-parametric).

---

## 3. Summary Table

| Data Type          | 2 Models (Paired)                       | 3+ Models (Repeated Measures)            |
|--------------------|-----------------------------------------|------------------------------------------|
| Binary Outcomes     | McNemar’s Test                         | Cochran’s Q Test                          |
| Continuous Outputs  | Paired t-Test / Wilcoxon Signed-Rank   | Repeated-Measures ANOVA / Friedman Test  |

---

## Notes
- Always validate test assumptions (e.g., normality, sphericity).
- Report **effect sizes** (e.g., Cohen’s d, percentage point differences).
- Consider **visualizations** (box plots, difference plots) alongside tests.


# Statistical Tests for Comparing LLM Performance on MCQs

This document summarizes appropriate statistical tests for evaluating and comparing Large Language Models (LLMs) on multiple-choice question (MCQ) datasets. It covers both binary correctness and continuous outputs such as log probabilities, confidence scores, or other evaluation metrics.

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

## 2. Continuous Outcomes (e.g., Log Probabilities, Confidence Scores, Evaluation Metrics)

### ✅ Two Models (Paired Data)
- **Paired t-Test**:
  - Use when the differences between paired values are approximately normally distributed.
  - Example: Log probability or confidence score per MCQ for each model.
- **Wilcoxon Signed-Rank Test**:
  - Use when data is not normally distributed or is ordinal.
  - Non-parametric alternative.

### ✅ Three or More Models (Repeated Measures)
- **Repeated-Measures ANOVA**:
  - Use when scores are continuous and meet assumptions of normality and sphericity.
  - Tests if means are significantly different across models.
- **Friedman Test**:
  - Non-parametric alternative to ANOVA.
  - Use when data violates normality assumptions or is ordinal.
  - Follow-up: Pairwise Wilcoxon tests with correction.

---

## 3. Decision Table

| **Data Type**          | **2 Models (Paired)**             | **3+ Models (Repeated Measures)**       |
|------------------------|------------------------------------|-----------------------------------------|
| Binary Outcomes         | McNemar’s Test                    | Cochran’s Q Test                        |
| Log Probabilities       | Paired t-Test / Wilcoxon          | Repeated-Measures ANOVA / Friedman     |
| Confidence Scores       | Paired t-Test / Wilcoxon          | Repeated-Measures ANOVA / Friedman     |
| Ordinal Evaluation Data | Wilcoxon Signed-Rank Test         | Friedman Test                           |

---

## 4. Assumptions and Considerations

- **Normality**: Check with Shapiro-Wilk test or Q-Q plots.
- **Sphericity** (for ANOVA): Check with Mauchly’s test.
- **Effect Size**:
  - For t-test: Cohen’s d
  - For Friedman Test: Kendall’s W
- **Multiple Comparisons**: Use Bonferroni or Holm correction during post-hoc tests.

---

## 5. Recommendations

- Use **binary tests** for right/wrong scoring evaluations.
- Use **paired tests** when the same MCQs are evaluated across models.
- Use **non-parametric alternatives** if normality is not met.
- Always pair statistical testing with **visualizations** like boxplots, violin plots, or error bars.


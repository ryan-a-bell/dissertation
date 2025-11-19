Merge this with the notebook when agents finish.

**Reasons for the statistical tests**

Statistical Test Suite:
1. Normality Testing

Shapiro-Wilk (best for small samples)
D'Agostino's K² (skewness and kurtosis)
Jarque-Bera (large sample test)
Q-Q plots to visually assess normality

2. Position Bias Analysis

Chi-Square Test - Overall independence of position and accuracy
Kruskal-Wallis H Test - Non-parametric ANOVA
Friedman Test - For repeated measures
Pairwise McNemar Tests - Between each position pair
Cramér's V - Effect size for categorical data

3. Effect Size Metrics

Cohen's d - Standardized mean difference
Glass's Δ - Uses control group SD
Hedges' g - Small sample correction
Interpretation guidelines (negligible/small/medium/large)

4. Bootstrap Analysis

10,000 resamples for robust confidence intervals
95% CI for all accuracy estimates
CI for differences (e.g., MCQ - OSQ)
Determines if differences are statistically significant

5. Power Analysis

Calculates achieved statistical power
Determines if studies are adequately powered
Calculates required sample sizes for 80% power
Identifies underpowered comparisons

6. Inter-Model Reliability

Cohen's κappa - Agreement between models
Percentage agreement calculations
Interpretation (poor/fair/moderate/substantial/perfect)

7. Regression Analysis

Logistic Regression - Identifies predictors of accuracy
Mixed Effects Models - Accounts for question difficulty
Odds ratios with interpretations
Significance of predictors (thinking model, format, position)

8. Permutation Tests

Distribution-free hypothesis testing
10,000 permutations for p-values
Visualization of null distributions
Robust to non-normal data

9. Clustering Analysis

K-means clustering of questions by difficulty
PCA visualization of question patterns
Identifies groups of similar questions
Helps understand what makes questions hard/easy

10. Bayesian Analysis (if PyMC3 installed)

Posterior distributions for model accuracy
95% and 89% credible intervals
Probability that Model A > Model B
Evidence strength interpretation

11. Response Complexity Analysis

Mann-Whitney U tests for response length differences
Correlation between response length and accuracy
Tests if correct answers are longer/shorter

12. Multiple Comparisons Correction

Bonferroni (most conservative)
Holm (step-down method)
Benjamini-Hochberg (FDR control)
Benjamini-Yekutieli (FDR under dependence)

🔍 Key Statistical Questions Answered:

Is position bias statistically significant?

Chi-square and Friedman tests confirm
Effect sizes quantify practical importance


Are differences between models real or due to chance?

Bootstrap CIs show if differences are significant
Permutation tests provide exact p-values


Do we have enough data for reliable conclusions?

Power analysis shows if sample size is adequate
Calculates how many more samples needed


Which factors predict accuracy?

Regression identifies significant predictors
Odds ratios show magnitude of effects


Are results consistent across questions?

Clustering identifies question types
Inter-rater reliability shows model agreement



📈 Interpretation Guidelines:
The notebook provides clear interpretations:
python# Effect Sizes
Cohen's d < 0.2: Negligible
0.2-0.5: Small
0.5-0.8: Medium
> 0.8: Large

**Statistical Power**
< 0.8: Underpowered (need more data)
≥ 0.8: Adequately powered

**P-values (after correction)**
< 0.001: Very strong evidence (***)
< 0.01: Strong evidence (**)
< 0.05: Moderate evidence (*)
≥ 0.05: No significant evidence
🎯 Practical Applications:

Publication-Ready Statistics - All tests needed for academic papers
Decision Support - Statistical evidence for model selection
Bias Detection - Quantifies and tests for various biases
Sample Size Planning - Determines data needs for future studies
Robust Conclusions - Multiple tests confirm findings
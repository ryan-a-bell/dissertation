# metaeval TODO

## v2.0.0 -- Additional Statistical Methods

The following methods are implemented but excluded from the current pipeline to keep
it aligned with the dissertation methodology. They remain available via direct module
imports (e.g., `from metaeval.bias.stats.tests import anova_test`) and are candidates
for inclusion in a future v2.0.0 release.

### Current Pipeline (v1.x -- Dissertation-Aligned)

| Category | Method | Module |
|----------|--------|--------|
| Position Bias Tests | Chi-square test | `bias.stats.tests` |
| | Friedman test | `bias.stats.tests` |
| Bias Effect Sizes | Cramer's V | `bias.stats.effects` |
| | Kendall's W | `bias.stats.effects` |
| Format Comparison | Wilcoxon signed-rank | `compare.stats.paired` |
| | Pearson correlation | `compare.stats.correlation` |
| | Spearman correlation | `compare.stats.correlation` |
| | Cohen's d | `compare.stats.effects` |
| | Bootstrap difference CI | `compare.stats.bootstrap` |
| | Bootstrap correlation CI | `compare.stats.bootstrap` |
| Inter-Rater Agreement | Cohen's kappa | `judge.agreement` |
| | Pairwise agreement | `judge.agreement` |

### Deferred to v2.0.0

| Category | Method | Module | Notes |
|----------|--------|--------|-------|
| Position Bias Tests | Kruskal-Wallis | `bias.stats.tests` | Superseded by Friedman for within-item design |
| | McNemar / Pairwise McNemar | `bias.stats.tests` | Pairwise position comparisons |
| | ANOVA | `bias.stats.tests` | Parametric alternative; assumptions rarely hold |
| | Shapiro-Wilk | `bias.stats.tests` | Normality test (not exported) |
| Bias Effect Sizes | Epsilon-squared | `bias.stats.effects` | Pairs with Kruskal-Wallis |
| | Eta-squared | `bias.stats.effects` | Pairs with ANOVA |
| Format Comparison | Paired t-test | `compare.stats.paired` | Parametric alternative to Wilcoxon |
| | Sign test | `compare.stats.paired` | Non-parametric paired test |
| | McNemar-Bowker | `compare.stats.paired` | Multi-category extension |
| | Hedges' g | `compare.stats.effects` | Bias-corrected Cohen's d |
| | Glass's delta | `compare.stats.effects` | Control-group-based effect size |
| | CLES / Prob. of superiority | `compare.stats.effects` | Probability of superiority |
| | Correlation matrix | `compare.stats.correlation` | Multi-variable correlation |
| | Correlation with CI | `compare.stats.correlation` | Bootstrap CI for correlations |
| | Bootstrap effect size CI | `compare.stats.bootstrap` | CI for custom effect sizes |
| Inter-Rater Agreement | Fleiss' kappa | `judge.agreement` | Multi-rater agreement |
| | Krippendorff's alpha | `judge.agreement` | Flexible agreement metric |
| | ICC | `judge.agreement` | Intraclass correlation |

### Not Yet Implemented

| Method | Used In Manuscript | Priority |
|--------|-------------------|----------|
| Linear regression (R-squared, slope) | Yes -- cross-modality analysis | High |
| Jarque-Bera (normality) | Archive only | Low |
| D'Agostino-Pearson (normality) | Archive only | Low |

# Quick Reference: Notebook Reorganization

## CELL MOVES AT A GLANCE

### Keep in Place (0-7)
Cells 0-7: Title, Setup, Data Loading - NO CHANGES

### Section 3: MCQ Analysis

**3.1 Data Exploration**
- Cell 9 → 10 (PyGWalker install)
- Cell 10 → 11 (PyGWalker usage)
- Cell 11 → 12 (DataFrame preview)

**3.2 Overall MCQ Performance** (NEW)
- Cell 18 → 14 (Table 3: Model Performance)

**3.3 Position Bias Analysis**
- Cell 13 → 16 (Filter code)
- Cell 16 → 18 (Statistical justification - MARKDOWN)
- Cell 15 → 20 (Chi-square code)
- **NEW** → 22 (Kruskal-Wallis - TO CREATE)
- **NEW** → 24 (Friedman - TO CREATE)
- Cell 22 → 26 (McNemar tests)
- Cell 20 → 28 (Cramér's V)
- Cell 33 → 30 (Heatmap viz)
- Cell 34 → 31 (Bar chart viz)
- Cell 35 → 32 (Heatmap alt)
- Cell 36 → 33 (Deviation bar)
- Cell 37 → 34 (Heatmap alt 2)

**3.4 MCQ Normality**
- Cell 24 → 36 (Normality tests)
- Cell 26 → 37 (Q-Q plot)
- Cell 41 → 38 (Q-Q comprehensive)

**3.5 MCQ Bootstrap**
- Cell 28 → 40 (Bootstrap calc)
- Cell 42 → 41 (Bootstrap viz)

### Section 4: OSQ Analysis

**4.1 OSQ Data Exploration**
- Cell 44 → 44 (Load OSQ)
- Cell 45 → 45 (Filter OSQ)
- Cell 46 → 46 (Judge/Prompt analysis)

**4.2 OSQ Score Distribution**
- Cell 47 → 48 (By judge)
- Cell 48 → 49 (By prompt)
- Cell 49 → 50 (Model perf)
- Cell 62 → 51 (Histogram KDE)
- Cell 63 → 52 (Violin)
- Cell 56 → 53 (Bloom's)
- Cell 66 → 54 (By dataset)

**4.3 OSQ Normality**
- Cell 52 → 56 (OSQ normality)

**4.4 OSQ Bootstrap** (NEW)
- **NEW** → 58 (Bootstrap CI - TO CREATE)

### Section 5: MCQ vs OSQ Comparative

**5.1 Rationale**
- Cell 57 → 61 (Rationale - MARKDOWN)

**5.2 Correlation**
- Cell 54 → 63 (Correlation analysis)

**5.3 Paired Tests**
- Cell 59 → 65 (Wilcoxon)

**5.4 Effect Sizes**
- Cell 61 → 67 (Effect sizes)

**5.5 Visualizations**
- Cell 50 → 69 (Side-by-side bar)
- Cell 53 → 70 (Scatter MCQ vs OSQ)
- Cell 69 → 71 (Scatter alt)
- Cell 67 → 72 (Confusion multiples)
- Cell 68 → 73 (Wrong answers)
- Cell 70 → 74 (Confusion all)

### Section 6: Summary Tables & Export

- Cell 29 → 76 (Table 2: Position accuracy)
- Cell 30 → 77 (Table 1: Statistical tests)
- Cell 32 → 78 (ANOVA test)
- Cell 39 → 80 (Final manifest)

## MARKDOWN CELLS TO DELETE

Delete these markdown headers (content merged into new structure):
- Cell 14: "### Chi-square test for position bias"
- Cell 17: "### ANOVA for Position Bias"
- Cell 19: "### 4.3 Cramér's V Effect Size"
- Cell 21: "### 4.4 Pairwise McNemar Tests"
- Cell 23: "### 4.5 MCQ Normality and Distributional Tests"
- Cell 25: "### 4.6 Q-Q Plot for MCQ Accuracy"
- Cell 27: "### 4.7 Bootstrap Confidence Intervals for MCQ Accuracy"
- Cell 31: "### Statistical Tables for LaTeX Export"
- Cell 38: "### Enhanced Visualizations - Plot 2: Confusion Matrix"
- Cell 40: "## 8. Output Summary and Manifest"
- Cell 43: "## 7. Diagnostic and Statistical Plots"
- Cell 51: "### 5.5 OSQ Normality Tests"
- Cell 55: "## 6. MCQ vs OSQ Comparative Analysis"
- Cell 58: "### 6.2 Wilcoxon Signed-Rank Test"
- Cell 60: "### 6.3 Effect Size Calculations"
- Cell 64: "## 5. OSQ Analysis (Conditional on Data Availability)"
- Cell 65: "### Enhanced Visualizations - Plot 3: MCQ Accuracy vs OSQ"

## NEW CODE TO WRITE

1. **Kruskal-Wallis H Test** (Cell 22)
   - Non-parametric alternative to one-way ANOVA
   - Test position bias without normality assumption
   - Export results to JSON/LaTeX

2. **Friedman Test** (Cell 24)
   - Repeated measures test (questions as subjects)
   - Compare positions accounting for question difficulty
   - Export results to JSON/LaTeX

3. **OSQ Bootstrap CI** (Cell 58)
   - Bootstrap confidence intervals for OSQ scores
   - 10,000 iterations, 95% CI
   - Similar to MCQ bootstrap (cell 28)
   - Visualization and export

## EXECUTION ORDER

1. Backup: `cp analysis.ipynb analysis.ipynb.backup`
2. Work backwards (move higher-numbered cells first)
3. Create new markdown headers
4. Move code cells
5. Delete obsolete markdown headers
6. Add new code cells
7. Verify structure
8. Test run all cells


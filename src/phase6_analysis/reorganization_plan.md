# Detailed Notebook Reorganization Plan
## Phase 6 Analysis Notebook Structure Revision

---

## PART 1: CELL-BY-CELL MAPPING (Current → New Location)

### § 1. Setup and Imports (Cells 0-4)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| 0 | 0 | MD | KEEP | Title & Introduction |
| 1 | 1 | MD | KEEP | ## 1. Setup and Imports |
| 2 | 2 | MD | RENAME | ### 1.1 Data Structure Reference |
| 3 | 3 | CODE | KEEP | Imports (pandas, numpy, scipy, matplotlib, etc.) |
| 4 | 4 | CODE | KEEP | Utility function (export_latex_table) |

### § 2. Data Loading (Cells 5-7)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| 5 | 5 | MD | KEEP | ## 2. Data Loading |
| 6 | 6 | CODE | KEEP | Define paths and load data |
| 7 | 7 | CODE | KEEP | Parse MCQ samples |

### § 3. MCQ Analysis (NEW STRUCTURE - Cells 8-42)

#### 3.1 Data Exploration (Cells 8-11)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| 8 | 8 | MD | RENAME | ## 3. MCQ Analysis |
| NEW | 9 | MD | CREATE | ### 3.1 Data Exploration |
| 9 | 10 | CODE | MOVE | PyGWalker install (commented) |
| 10 | 11 | CODE | MOVE | PyGWalker usage (commented) |
| 11 | 12 | CODE | MOVE | MCQ DataFrame preview |

#### 3.2 Overall MCQ Performance (NEW SECTION)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 13 | MD | CREATE | ### 3.2 Overall MCQ Performance |
| 18 | 14 | CODE | MOVE | Table 3: Model Performance Summary (MCQ Overall) |

#### 3.3 Position Bias Analysis (Cells 12-37)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| 12 | 15 | MD | RENAME | ### 3.3 Position Bias Analysis |
| 13 | 16 | CODE | MOVE | Filter for fixed-position variants |
| NEW | 17 | MD | CREATE | #### Statistical Test Justification |
| 16 | 18 | MD | MOVE | (Statistical Test Justification content) |

##### Chi-Square Test
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 19 | MD | CREATE | #### Chi-Square Test |
| 14 | DELETE | MD | DELETE | (Merge into new header) |
| 15 | 20 | CODE | MOVE | Chi-square test for position bias |

##### Kruskal-Wallis H Test (NEW)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 21 | MD | CREATE | #### Kruskal-Wallis H Test |
| NEW | 22 | CODE | CREATE | Kruskal-Wallis test implementation |

##### Friedman Test (NEW)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 23 | MD | CREATE | #### Friedman Test |
| NEW | 24 | CODE | CREATE | Friedman test implementation |

##### Pairwise McNemar Tests
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 25 | MD | CREATE | #### Pairwise McNemar Tests |
| 21 | DELETE | MD | DELETE | (Merge into new header) |
| 22 | 26 | CODE | MOVE | Pairwise McNemar Tests |

##### Cramér's V Effect Sizes
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 27 | MD | CREATE | #### Cramér's V Effect Sizes |
| 19 | DELETE | MD | DELETE | (Merge into new header) |
| 20 | 28 | CODE | MOVE | Cramér's V calculation |

##### Visualizations
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 29 | MD | CREATE | #### Visualizations |
| 33 | 30 | CODE | MOVE | Position bias heatmap |
| 34 | 31 | CODE | MOVE | Position bias bar chart |
| 35 | 32 | CODE | MOVE | Plot 1: Per-Position Accuracy Heatmap |
| 36 | 33 | CODE | MOVE | Plot 2: Deviation-From-Uniform Bar Plot |
| 37 | 34 | CODE | MOVE | Plot 1 alternate version |

#### 3.4 MCQ Normality & Distributional Tests
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 35 | MD | CREATE | ### 3.4 MCQ Normality & Distributional Tests |
| 23 | DELETE | MD | DELETE | (Merge into new header) |
| 24 | 36 | CODE | MOVE | Normality tests (Shapiro, Jarque-Bera, D'Agostino) |
| 25 | DELETE | MD | DELETE | (Merge into visualizations) |
| 26 | 37 | CODE | MOVE | Q-Q Plot for MCQ Accuracy |
| 41 | 38 | CODE | MOVE | Plot 13: Q-Q Plots for Normality Assessment |

#### 3.5 MCQ Bootstrap Confidence Intervals
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 39 | MD | CREATE | ### 3.5 MCQ Bootstrap Confidence Intervals |
| 27 | DELETE | MD | DELETE | (Merge into new header) |
| 28 | 40 | CODE | MOVE | Bootstrap CI calculation |
| 42 | 41 | CODE | MOVE | Plot 12: Bootstrap CI visualization |

### § 4. OSQ Analysis (Cells 43-54)

#### 4.1 OSQ Data Exploration
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 42 | MD | CREATE | ## 4. OSQ Analysis |
| 64 | DELETE | MD | DELETE | (Merge into new header) |
| NEW | 43 | MD | CREATE | ### 4.1 OSQ Data Exploration |
| 44 | 44 | CODE | MOVE | Load OSQ data and create aligned dataset |
| 45 | 45 | CODE | MOVE | Filter OSQ data by judge/prompt |
| 46 | 46 | CODE | MOVE | OSQ Judge and Prompt Analysis |

#### 4.2 OSQ Score Distribution
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 47 | MD | CREATE | ### 4.2 OSQ Score Distribution |
| 47 | 48 | CODE | MOVE | OSQ Score Distribution by Judge Model |
| 48 | 49 | CODE | MOVE | OSQ Score Distribution by Prompt |
| 49 | 50 | CODE | MOVE | Model Performance Across Different Judges |
| 62 | 51 | CODE | MOVE | Plot 6: OSQ Score Distribution Histogram with KDE |
| 63 | 52 | CODE | MOVE | Plot 5: OSQ Violin Plot |
| 56 | 53 | CODE | MOVE | Plot 7: OSQ Bloom's Level Comparison |
| 66 | 54 | CODE | MOVE | Plot 4: Violin Plots for OSQ by Dataset/Variant |

#### 4.3 OSQ Normality & Distributional Tests
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 55 | MD | CREATE | ### 4.3 OSQ Normality & Distributional Tests |
| 51 | DELETE | MD | DELETE | (Merge into new header) |
| 52 | 56 | CODE | MOVE | OSQ Normality Tests |

#### 4.4 OSQ Bootstrap Confidence Intervals (NEW)
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 57 | MD | CREATE | ### 4.4 OSQ Bootstrap Confidence Intervals |
| NEW | 58 | CODE | CREATE | Bootstrap CI for OSQ scores |

### § 5. MCQ vs OSQ Comparative Analysis (Cells 55-70)

#### 5.1 Comparative Analysis Rationale
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 59 | MD | CREATE | ## 5. MCQ vs OSQ Comparative Analysis |
| 55 | DELETE | MD | DELETE | (Merge into new header) |
| NEW | 60 | MD | CREATE | ### 5.1 Comparative Analysis Rationale |
| 57 | 61 | MD | MOVE | Statistical Rationale content |

#### 5.2 Correlation Analysis
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 62 | MD | CREATE | ### 5.2 Correlation Analysis |
| 54 | 63 | CODE | MOVE | MCQ-OSQ Correlation by Judge and Prompt |

#### 5.3 Paired Statistical Tests
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 64 | MD | CREATE | ### 5.3 Paired Statistical Tests |
| 58 | DELETE | MD | DELETE | (Merge into new header) |
| 59 | 65 | CODE | MOVE | Wilcoxon Signed-Rank Test |

#### 5.4 Effect Size Calculations
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 66 | MD | CREATE | ### 5.4 Effect Size Calculations |
| 60 | DELETE | MD | DELETE | (Merge into new header) |
| 61 | 67 | CODE | MOVE | Effect Size Calculations (Cohen's d, etc.) |

#### 5.5 Visualizations
| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 68 | MD | CREATE | ### 5.5 Visualizations |
| 65 | DELETE | MD | DELETE | (Merge into new header) |
| 38 | DELETE | MD | DELETE | (Merge into new header) |
| 50 | 69 | CODE | MOVE | Plot 9: Side-by-Side Bar Chart (MCQ vs OSQ) |
| 53 | 70 | CODE | MOVE | Plot 8: MCQ Accuracy vs OSQ Mean Score Scatter |
| 69 | 71 | CODE | MOVE | Plot 3: MCQ Accuracy vs OSQ Mean Score |
| 67 | 72 | CODE | MOVE | Plot 3: Confusion Matrix Small Multiples |
| 68 | 73 | CODE | MOVE | Plot 4: Wrong-Answer Distribution |
| 70 | 74 | CODE | MOVE | Plot 2: Confusion Matrix for All MCQs |

### § 6. Summary Tables & Export (Cells 29-40)

| Current | New | Type | Action | Content |
|---------|-----|------|--------|---------|
| NEW | 75 | MD | CREATE | ## 6. Summary Tables & Export |
| 31 | DELETE | MD | DELETE | (Merge into new header) |
| 29 | 76 | CODE | MOVE | Table 2: Position Accuracy Summary |
| 30 | 77 | CODE | MOVE | Table 1: Position Bias Statistical Tests |
| 17 | DELETE | MD | DELETE | (No longer needed) |
| 32 | 78 | CODE | MOVE | ANOVA test for position bias |
| NEW | 79 | MD | CREATE | ### Output Summary and Manifest |
| 40 | DELETE | MD | DELETE | (Merge into new header) |
| 39 | 80 | CODE | MOVE | Final Summary: List all generated outputs |

---

## PART 2: HEADERS TO RENAME

| Cell | Current Header | New Header |
|------|----------------|------------|
| 8 | ## 3. Data Exploration | ## 3. MCQ Analysis |
| 12 | ## 4. Position Bias Analysis | ### 3.3 Position Bias Analysis |
| 2 | ### 1.1 Data Structure Reference | ### 1.1 Data Structure Reference (KEEP) |

---

## PART 3: NEW HEADERS TO CREATE

| Position | Header | Level |
|----------|--------|-------|
| After cell 8 | ### 3.1 Data Exploration | h3 |
| Before cell 18 | ### 3.2 Overall MCQ Performance | h3 |
| Before moved cell 16 | #### Statistical Test Justification | h4 |
| Before cell 15 (chi-square) | #### Chi-Square Test | h4 |
| NEW section | #### Kruskal-Wallis H Test | h4 |
| NEW section | #### Friedman Test | h4 |
| Before cell 22 | #### Pairwise McNemar Tests | h4 |
| Before cell 20 | #### Cramér's V Effect Sizes | h4 |
| Before visualizations | #### Visualizations | h4 |
| NEW section | ### 3.4 MCQ Normality & Distributional Tests | h3 |
| NEW section | ### 3.5 MCQ Bootstrap Confidence Intervals | h3 |
| NEW section | ## 4. OSQ Analysis | h2 |
| NEW section | ### 4.1 OSQ Data Exploration | h3 |
| NEW section | ### 4.2 OSQ Score Distribution | h3 |
| NEW section | ### 4.3 OSQ Normality & Distributional Tests | h3 |
| NEW section | ### 4.4 OSQ Bootstrap Confidence Intervals | h3 |
| NEW section | ## 5. MCQ vs OSQ Comparative Analysis | h2 |
| NEW section | ### 5.1 Comparative Analysis Rationale | h3 |
| NEW section | ### 5.2 Correlation Analysis | h3 |
| NEW section | ### 5.3 Paired Statistical Tests | h3 |
| NEW section | ### 5.4 Effect Size Calculations | h3 |
| NEW section | ### 5.5 Visualizations | h3 |
| NEW section | ## 6. Summary Tables & Export | h2 |
| NEW section | ### Output Summary and Manifest | h3 |

---

## PART 4: CELLS TO DELETE

| Cell | Reason |
|------|--------|
| 14 | Markdown header - merge into new "#### Chi-Square Test" |
| 17 | Markdown header - merge into new section structure |
| 19 | Markdown header - merge into new "#### Cramér's V Effect Sizes" |
| 21 | Markdown header - merge into new "#### Pairwise McNemar Tests" |
| 23 | Markdown header - merge into new "### 3.4 MCQ Normality" |
| 25 | Markdown header - merge into visualizations |
| 27 | Markdown header - merge into new "### 3.5 MCQ Bootstrap" |
| 31 | Markdown header - merge into "## 6. Summary Tables & Export" |
| 38 | Markdown header - merge into "### 5.5 Visualizations" |
| 40 | Markdown header - merge into "## 6. Summary Tables & Export" |
| 43 | Markdown header - no longer needed (section reorg) |
| 51 | Markdown header - merge into new "### 4.3 OSQ Normality" |
| 55 | Markdown header - merge into new "## 5. MCQ vs OSQ" |
| 57 | Markdown header - becomes "### 5.1 Comparative Analysis" |
| 58 | Markdown header - merge into "### 5.3 Paired Statistical Tests" |
| 60 | Markdown header - merge into "### 5.4 Effect Size Calculations" |
| 64 | Markdown header - merge into new "## 4. OSQ Analysis" |
| 65 | Markdown header - merge into "### 5.5 Visualizations" |

---

## PART 5: NEW CODE CELLS TO CREATE

| Position | Purpose | Content Needed |
|----------|---------|----------------|
| After Statistical Test Justification | Kruskal-Wallis H Test | Implement Kruskal-Wallis test for position bias (non-parametric alternative to ANOVA) |
| After Kruskal-Wallis | Friedman Test | Implement Friedman test for repeated measures (treats each question as subject) |
| In OSQ section | Bootstrap CI for OSQ | Implement bootstrap confidence intervals for OSQ scores (similar to MCQ bootstrap) |

---

## PART 6: STEP-BY-STEP REORGANIZATION INSTRUCTIONS

### Phase 1: Backup
1. Create backup: `cp analysis.ipynb analysis.ipynb.backup`

### Phase 2: Create New Structure Template
1. Keep cells 0-7 as is (title, imports, data loading)
2. Rename cell 8: "## 3. MCQ Analysis"

### Phase 3: Reorganize MCQ Analysis (Section 3)
1. Create new markdown cell after cell 8: "### 3.1 Data Exploration"
2. Move cells 9-11 (PyGWalker, DataFrame preview) under 3.1
3. Create new markdown cell: "### 3.2 Overall MCQ Performance"
4. Move cell 18 (Table 3) under 3.2
5. Create new markdown cell: "### 3.3 Position Bias Analysis"
6. Move cell 13 (filter code) under 3.3
7. Create new markdown cell: "#### Statistical Test Justification"
8. Move cell 16 content under this header
9. Create subsections:
   - "#### Chi-Square Test" → move cell 15
   - "#### Kruskal-Wallis H Test" → CREATE NEW CODE
   - "#### Friedman Test" → CREATE NEW CODE
   - "#### Pairwise McNemar Tests" → move cell 22
   - "#### Cramér's V Effect Sizes" → move cell 20
   - "#### Visualizations" → move cells 33-37
10. Create "### 3.4 MCQ Normality & Distributional Tests"
    - Move cells 24, 26, 41
11. Create "### 3.5 MCQ Bootstrap Confidence Intervals"
    - Move cells 28, 42

### Phase 4: Reorganize OSQ Analysis (Section 4)
1. Create "## 4. OSQ Analysis"
2. Create "### 4.1 OSQ Data Exploration"
   - Move cells 44-46
3. Create "### 4.2 OSQ Score Distribution"
   - Move cells 47-49, 62, 63, 56, 66
4. Create "### 4.3 OSQ Normality & Distributional Tests"
   - Move cell 52
5. Create "### 4.4 OSQ Bootstrap Confidence Intervals"
   - CREATE NEW CODE

### Phase 5: Reorganize Comparative Analysis (Section 5)
1. Create "## 5. MCQ vs OSQ Comparative Analysis"
2. Create "### 5.1 Comparative Analysis Rationale"
   - Move cell 57 content
3. Create "### 5.2 Correlation Analysis"
   - Move cell 54
4. Create "### 5.3 Paired Statistical Tests"
   - Move cell 59
5. Create "### 5.4 Effect Size Calculations"
   - Move cell 61
6. Create "### 5.5 Visualizations"
   - Move cells 50, 53, 69, 67, 68, 70

### Phase 6: Create Summary Section (Section 6)
1. Create "## 6. Summary Tables & Export"
2. Move cells 29, 30, 32 (tables)
3. Create "### Output Summary and Manifest"
4. Move cell 39

### Phase 7: Delete Obsolete Cells
Delete cells: 14, 17, 19, 21, 23, 25, 27, 31, 38, 40, 43, 51, 55, 57, 58, 60, 64, 65

### Phase 8: Verification
1. Verify all code cells are present
2. Verify section numbering is correct (1-6)
3. Run all cells to ensure no broken dependencies
4. Check that visualizations generate correctly

---

## PART 7: DETAILED CELL ORDER (Final Structure)

```
0   | MD   | # Phase 6: Statistical Analysis...
1   | MD   | ## 1. Setup and Imports
2   | MD   | ### 1.1 Data Structure Reference
3   | CODE | Imports
4   | CODE | Utility functions

5   | MD   | ## 2. Data Loading
6   | CODE | Define paths
7   | CODE | Parse MCQ samples

8   | MD   | ## 3. MCQ Analysis
9   | MD   | ### 3.1 Data Exploration
10  | CODE | PyGWalker install
11  | CODE | PyGWalker usage
12  | CODE | MCQ DataFrame preview

13  | MD   | ### 3.2 Overall MCQ Performance
14  | CODE | Table 3: Model Performance Summary

15  | MD   | ### 3.3 Position Bias Analysis
16  | CODE | Filter fixed-position variants
17  | MD   | #### Statistical Test Justification
18  | MD   | [Content from old cell 16]
19  | MD   | #### Chi-Square Test
20  | CODE | Chi-square test
21  | MD   | #### Kruskal-Wallis H Test
22  | CODE | **NEW** Kruskal-Wallis implementation
23  | MD   | #### Friedman Test
24  | CODE | **NEW** Friedman implementation
25  | MD   | #### Pairwise McNemar Tests
26  | CODE | McNemar tests
27  | MD   | #### Cramér's V Effect Sizes
28  | CODE | Cramér's V
29  | MD   | #### Visualizations
30  | CODE | Heatmap
31  | CODE | Bar chart
32  | CODE | Per-position heatmap
33  | CODE | Deviation bar plot
34  | CODE | Heatmap alternate

35  | MD   | ### 3.4 MCQ Normality & Distributional Tests
36  | CODE | Normality tests
37  | CODE | Q-Q plot
38  | CODE | Q-Q plots comprehensive

39  | MD   | ### 3.5 MCQ Bootstrap Confidence Intervals
40  | CODE | Bootstrap calculation
41  | CODE | Bootstrap visualization

42  | MD   | ## 4. OSQ Analysis
43  | MD   | ### 4.1 OSQ Data Exploration
44  | CODE | Load OSQ data
45  | CODE | Filter OSQ data
46  | CODE | Judge/Prompt analysis

47  | MD   | ### 4.2 OSQ Score Distribution
48  | CODE | By judge model
49  | CODE | By prompt
50  | CODE | Model performance across judges
51  | CODE | Histogram with KDE
52  | CODE | Violin plot
53  | CODE | Bloom's level
54  | CODE | By dataset/variant

55  | MD   | ### 4.3 OSQ Normality & Distributional Tests
56  | CODE | OSQ normality tests

57  | MD   | ### 4.4 OSQ Bootstrap Confidence Intervals
58  | CODE | **NEW** OSQ bootstrap CI

59  | MD   | ## 5. MCQ vs OSQ Comparative Analysis
60  | MD   | ### 5.1 Comparative Analysis Rationale
61  | MD   | [Content from old cell 57]

62  | MD   | ### 5.2 Correlation Analysis
63  | CODE | MCQ-OSQ correlation

64  | MD   | ### 5.3 Paired Statistical Tests
65  | CODE | Wilcoxon test

66  | MD   | ### 5.4 Effect Size Calculations
67  | CODE | Effect sizes

68  | MD   | ### 5.5 Visualizations
69  | CODE | Side-by-side bar chart
70  | CODE | Scatter plot
71  | CODE | MCQ vs OSQ scatter
72  | CODE | Confusion matrix multiples
73  | CODE | Wrong-answer distribution
74  | CODE | Confusion matrix all

75  | MD   | ## 6. Summary Tables & Export
76  | CODE | Table 2: Position accuracy
77  | CODE | Table 1: Statistical tests
78  | CODE | ANOVA test
79  | MD   | ### Output Summary and Manifest
80  | CODE | Final summary
```

Total cells: 81 (71 original + 10 new - 0 deleted headers absorbed into new structure)

---

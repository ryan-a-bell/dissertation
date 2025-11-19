# Visual Structure Comparison

## CURRENT STRUCTURE (Disorganized)

```
0   Title/Intro
1   ## 1. Setup and Imports
2   ### 1.1 Data Structure Reference
3-4 CODE: Imports & utilities

5   ## 2. Data Loading
6-7 CODE: Load MCQ data

8   ## 3. Data Exploration ❌ (should be MCQ Analysis)
9-11 CODE: PyGWalker, preview

12  ## 4. Position Bias Analysis ❌ (wrong level, should be 3.3)
13  CODE: Filter variants
14  ### Chi-square test
15  CODE: Chi-square
16  #### Statistical Test Justification ❌ (wrong order)
17  ### ANOVA for Position Bias ❌ (duplicate/wrong order)
18  CODE: Table 3 - MCQ Overall ❌ (misplaced)
19  ### 4.3 Cramér's V
20  CODE: Cramér's V
21  ### 4.4 Pairwise McNemar
22  CODE: McNemar
23  ### 4.5 MCQ Normality
24  CODE: Normality
25  ### 4.6 Q-Q Plot
26  CODE: Q-Q
27  ### 4.7 Bootstrap CI
28-30 CODE: Bootstrap, tables
31  ### Statistical Tables for LaTeX ❌ (misplaced)
32  CODE: ANOVA test ❌ (should be with other stats)
33-37 CODE: Visualizations ❌ (scattered)
38  ### Enhanced Viz - Confusion Matrix ❌ (misplaced)
39  CODE: Final summary ❌ (should be at end)

40  ## 8. Output Summary ❌ (SECTION 8 BEFORE 7!)
41-42 CODE: More plots ❌ (scattered)

43  ## 7. Diagnostic Plots ❌ (SECTION 7 OUT OF ORDER!)
44-50 CODE: OSQ loading and plots ❌ (mixed)

51  ### 5.5 OSQ Normality ❌ (SECTION 5.5 BEFORE SECTION 5!)
52-54 CODE: OSQ analysis

55  ## 6. MCQ vs OSQ ❌ (SECTION 6 BEFORE 5!)
56  CODE: OSQ Bloom's ❌ (misplaced)
57  ### 6.1 Rationale
58  ### 6.2 Wilcoxon
59  CODE: Wilcoxon
60  ### 6.3 Effect Size
61-63 CODE: Effect sizes, plots

64  ## 5. OSQ Analysis ❌ (FINALLY SECTION 5!)
65  ### Enhanced Viz Plot 3 ❌ (misplaced)
66-70 CODE: Various plots ❌ (scattered)
```

## NEW STRUCTURE (Organized & Logical)

```
§ 1. SETUP AND IMPORTS (Cells 0-4)
  0   Title/Intro
  1   ## 1. Setup and Imports
  2   ### 1.1 Data Structure Reference
  3   CODE: Imports
  4   CODE: Utility functions

§ 2. DATA LOADING (Cells 5-7)
  5   ## 2. Data Loading
  6   CODE: Define paths
  7   CODE: Parse MCQ samples

§ 3. MCQ ANALYSIS (Cells 8-41)
  8   ## 3. MCQ Analysis ✅

  3.1 DATA EXPLORATION
    9   ### 3.1 Data Exploration ✅
    10  CODE: PyGWalker install
    11  CODE: PyGWalker usage
    12  CODE: DataFrame preview

  3.2 OVERALL MCQ PERFORMANCE ✅ NEW SECTION
    13  ### 3.2 Overall MCQ Performance ✅
    14  CODE: Table 3 - Model Performance Summary

  3.3 POSITION BIAS ANALYSIS
    15  ### 3.3 Position Bias Analysis ✅
    16  CODE: Filter fixed-position variants

    STATISTICAL TEST JUSTIFICATION
      17  #### Statistical Test Justification ✅
      18  MD: Justification content

    CHI-SQUARE TEST
      19  #### Chi-Square Test ✅
      20  CODE: Chi-square test

    KRUSKAL-WALLIS H TEST ✅ NEW
      21  #### Kruskal-Wallis H Test ✅
      22  CODE: Kruskal-Wallis (TO CREATE)

    FRIEDMAN TEST ✅ NEW
      23  #### Friedman Test ✅
      24  CODE: Friedman (TO CREATE)

    PAIRWISE MCNEMAR TESTS
      25  #### Pairwise McNemar Tests ✅
      26  CODE: McNemar tests

    CRAMÉR'S V EFFECT SIZES
      27  #### Cramér's V Effect Sizes ✅
      28  CODE: Cramér's V

    VISUALIZATIONS
      29  #### Visualizations ✅
      30  CODE: Heatmap
      31  CODE: Bar chart
      32  CODE: Per-position heatmap
      33  CODE: Deviation bar
      34  CODE: Heatmap alternate

  3.4 MCQ NORMALITY & DISTRIBUTIONAL TESTS
    35  ### 3.4 MCQ Normality & Distributional Tests ✅
    36  CODE: Normality tests (Shapiro, Jarque-Bera)
    37  CODE: Q-Q plot
    38  CODE: Q-Q plots comprehensive

  3.5 MCQ BOOTSTRAP CONFIDENCE INTERVALS
    39  ### 3.5 MCQ Bootstrap Confidence Intervals ✅
    40  CODE: Bootstrap calculation
    41  CODE: Bootstrap visualization

§ 4. OSQ ANALYSIS (Cells 42-58)
  42  ## 4. OSQ Analysis ✅

  4.1 OSQ DATA EXPLORATION
    43  ### 4.1 OSQ Data Exploration ✅
    44  CODE: Load OSQ data
    45  CODE: Filter OSQ data
    46  CODE: Judge/Prompt analysis

  4.2 OSQ SCORE DISTRIBUTION
    47  ### 4.2 OSQ Score Distribution ✅
    48  CODE: By judge model
    49  CODE: By prompt
    50  CODE: Model performance across judges
    51  CODE: Histogram with KDE
    52  CODE: Violin plot
    53  CODE: Bloom's level comparison
    54  CODE: By dataset/variant

  4.3 OSQ NORMALITY & DISTRIBUTIONAL TESTS
    55  ### 4.3 OSQ Normality & Distributional Tests ✅
    56  CODE: OSQ normality tests

  4.4 OSQ BOOTSTRAP CONFIDENCE INTERVALS ✅ NEW
    57  ### 4.4 OSQ Bootstrap Confidence Intervals ✅
    58  CODE: OSQ bootstrap CI (TO CREATE)

§ 5. MCQ vs OSQ COMPARATIVE ANALYSIS (Cells 59-74)
  59  ## 5. MCQ vs OSQ Comparative Analysis ✅

  5.1 COMPARATIVE ANALYSIS RATIONALE
    60  ### 5.1 Comparative Analysis Rationale ✅
    61  MD: Statistical rationale content

  5.2 CORRELATION ANALYSIS
    62  ### 5.2 Correlation Analysis ✅
    63  CODE: MCQ-OSQ correlation by judge/prompt

  5.3 PAIRED STATISTICAL TESTS
    64  ### 5.3 Paired Statistical Tests ✅
    65  CODE: Wilcoxon signed-rank test

  5.4 EFFECT SIZE CALCULATIONS
    66  ### 5.4 Effect Size Calculations ✅
    67  CODE: Cohen's d, Hedges' g, Glass's Δ

  5.5 VISUALIZATIONS
    68  ### 5.5 Visualizations ✅
    69  CODE: Side-by-side bar chart (MCQ vs OSQ)
    70  CODE: Scatter plot (MCQ accuracy vs OSQ)
    71  CODE: MCQ vs OSQ scatter (alternate)
    72  CODE: Confusion matrix small multiples
    73  CODE: Wrong-answer distribution
    74  CODE: Confusion matrix (all models)

§ 6. SUMMARY TABLES & EXPORT (Cells 75-80)
  75  ## 6. Summary Tables & Export ✅
  76  CODE: Table 2 - Position Accuracy Summary
  77  CODE: Table 1 - Position Bias Statistical Tests
  78  CODE: ANOVA test for position bias

  OUTPUT SUMMARY
    79  ### Output Summary and Manifest ✅
    80  CODE: Final summary - list all outputs
```

## KEY IMPROVEMENTS

1. **Logical Section Flow**: 1→2→3→4→5→6 (was: 1→2→3→4→8→7→6→5)
2. **Hierarchical Organization**: Clear subsections with proper nesting
3. **Grouped Related Content**: All position bias tests together, all visualizations together
4. **Complete Test Coverage**: Added Kruskal-Wallis and Friedman tests
5. **Consistent Structure**: MCQ and OSQ sections mirror each other
6. **Clear Separation**: MCQ → OSQ → Comparison → Export
7. **Better Naming**: Descriptive section headers at appropriate levels
8. **No Orphaned Cells**: Every code cell belongs to a clear section

## STATISTICS

- **Current notebook**: 71 cells, sections out of order (8→7→6→5)
- **New notebook**: 81 cells, logical flow (1→2→3→4→5→6)
- **New cells added**: 10 (7 markdown headers + 3 code implementations)
- **Cells reorganized**: 40+ cells moved to proper locations
- **Obsolete headers deleted**: 18 markdown cells merged into new structure
- **New statistical tests**: Kruskal-Wallis, Friedman, OSQ Bootstrap CI

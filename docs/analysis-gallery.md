---
title: Analysis Gallery
---

# Analysis Gallery

Key figures from the Phase 6 empirical analysis, organized by research contribution. Click any figure to view full-size.

=== "Modality Comparison"

    **Contribution 1 -- MCQ vs OSQ Evaluation Modalities**

    How do multiple-choice and open-style question formats compare when evaluating the same models on the same domain content?

    <div class="figure-gallery" markdown>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_regions.png" alt="MCQ vs OSQ Scatter with Performance Regions">
      <figcaption>MCQ vs OSQ accuracy scatter with performance regions</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/mcq_vs_osq_scatter_regions_model_avg.png" alt="MCQ vs OSQ Scatter -- Model Averaged">
      <figcaption>MCQ vs OSQ scatter -- model-averaged scores</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_by_category.png" alt="MCQ vs OSQ Scatter by INCOSE Category">
      <figcaption>MCQ vs OSQ scatter by INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_by_toplevel.png" alt="MCQ vs OSQ Scatter by Top-Level Category">
      <figcaption>MCQ vs OSQ scatter by top-level INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_osq_delta_by_incose_category.png" alt="MCQ-OSQ Delta by INCOSE Category">
      <figcaption>Performance delta (MCQ minus OSQ) by INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_osq_delta_by_incose_toplevel.png" alt="MCQ-OSQ Delta by Top-Level Category">
      <figcaption>Performance delta by top-level INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_accuracy_by_incose_category.png" alt="MCQ Accuracy by INCOSE Category">
      <figcaption>MCQ accuracy by INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_accuracy_by_incose_toplevel.png" alt="MCQ Accuracy by Top-Level Category">
      <figcaption>MCQ accuracy by top-level INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_category.png" alt="OSQ Accuracy by INCOSE Category">
      <figcaption>OSQ accuracy by INCOSE category</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_toplevel.png" alt="OSQ Accuracy by Top-Level Category">
      <figcaption>OSQ accuracy by top-level INCOSE category</figcaption>
    </figure>

    </div>

=== "Distractor Sensitivity"

    **Contribution 2 -- Robustness of MCQ Evaluation Under Distractor Variation**

    How sensitive are MCQ scores to the design and positioning of distractor answer choices?

    <div class="figure-gallery" markdown>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_position_accuracy.png" alt="MCQ Position Accuracy">
      <figcaption>MCQ accuracy by answer position</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_mcq_deviation_uniform.png" alt="MCQ Deviation from Uniform">
      <figcaption>Deviation from uniform answer distribution</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_cramers_v_position_bias.png" alt="Cramer's V Position Bias">
      <figcaption>Cramer's V statistic for position bias</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/mcq_position_heatmap.png" alt="MCQ Position Heatmap">
      <figcaption>Position selection heatmap across models</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/position_bias_bar.png" alt="Position Bias Bar Chart">
      <figcaption>Position bias bar chart</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/mcq_wrong_answer_distribution.png" alt="MCQ Wrong Answer Distribution">
      <figcaption>Wrong answer distribution across positions</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/mcq_confusion_matrix_all_models.png" alt="Confusion Matrix -- All Models">
      <figcaption>Confusion matrix -- all models</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/mcq_confusion_matrix_top_models.png" alt="Confusion Matrix -- Top Models">
      <figcaption>Confusion matrix -- top-performing models</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/mcq_bootstrap_ci.png" alt="MCQ Bootstrap Confidence Intervals">
      <figcaption>Bootstrap confidence intervals for MCQ accuracy</figcaption>
    </figure>

    </div>

=== "Consensus Judging"

    **Contribution 3 -- LLM-as-a-Judge Reliability and Consensus**

    How reliable are LLM judges when scoring open-ended responses, and do multiple judges converge?

    <div class="figure-gallery" markdown>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/mcq_vs_osq_rubric_combined_multijudge_raw.png" alt="Multi-Judge Rubric Comparison">
      <figcaption>Rubric scores across multiple LLM judges</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/osq_model_violin_openai_gpt-5-mini.png" alt="OSQ Violin -- GPT-5-mini">
      <figcaption>OSQ score distribution -- GPT-5-mini</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/osq_model_violin_gpt-oss_120b.png" alt="OSQ Violin -- GPT-OSS 120B">
      <figcaption>OSQ score distribution -- GPT-OSS 120B</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/osq_score_kde_openai_gpt-5-mini.png" alt="OSQ KDE -- GPT-5-mini">
      <figcaption>Kernel density estimate -- GPT-5-mini</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/osq_score_kde_gpt-oss_120b.png" alt="OSQ KDE -- GPT-OSS 120B">
      <figcaption>Kernel density estimate -- GPT-OSS 120B</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/osq_rubric_dimensions_all_judges.png" alt="Rubric Dimensions -- All Judges">
      <figcaption>Rubric dimension scores across all judges</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/osq_violin_scores.png" alt="OSQ Violin Scores">
      <figcaption>OSQ score violin plot -- all models</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/osq_score_histogram.png" alt="OSQ Score Histogram">
      <figcaption>OSQ score histogram</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/osq_blooms_comparison.png" alt="Bloom's Taxonomy Comparison">
      <figcaption>OSQ scores by Bloom's taxonomy level</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_category.png" alt="OSQ Bootstrap CI">
      <figcaption>OSQ accuracy by INCOSE category (judge consensus)</figcaption>
    </figure>

    </div>

=== "Token Efficiency"

    **Contribution 4 -- Cost-Aware Response Length Trade-offs**

    What is the relationship between response length, token cost, and evaluation quality?

    <div class="figure-gallery" markdown>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/pareto_efficiency_frontier.png" alt="Pareto Efficiency Frontier">
      <figcaption>Pareto efficiency frontier -- quality vs cost</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/response_tokens_by_model_and_quality_avg_judge.png" alt="Response Tokens by Model and Quality">
      <figcaption>Response tokens by model, colored by quality</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/tokenomics_length_vs_quality.png" alt="Token Length vs Quality">
      <figcaption>Response length vs quality score</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output_v3/tokenomics_length_vs_quality_sorted_worst_to_best.png" alt="Token Length vs Quality -- Sorted">
      <figcaption>Response length vs quality -- sorted worst to best</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/tokenomics_efficiency_scatter.png" alt="Tokenomics Efficiency Scatter">
      <figcaption>Token efficiency scatter plot</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/tokenomics_cost_quality.png" alt="Tokenomics Cost vs Quality">
      <figcaption>Cost vs quality trade-off</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/tokenomics_budget_heatmap.png" alt="Tokenomics Budget Heatmap">
      <figcaption>Token budget heatmap across models</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/tokenomics_distribution.png" alt="Tokenomics Distribution">
      <figcaption>Token usage distribution</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/token_quality_correlation.png" alt="Token Quality Correlation">
      <figcaption>Token count vs quality correlation</figcaption>
    </figure>

    </div>

=== "Statistical Diagnostics"

    **Supporting Analysis -- Normality and Distribution Tests**

    Statistical diagnostics validating the analytical methods used above.

    <div class="figure-gallery" markdown>

    <figure>
      <img src="source-code/phase6_analysis/output/qq_plots.png" alt="Q-Q Plots">
      <figcaption>Q-Q plots -- combined</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/qq_plot_mcq_accuracies.png" alt="Q-Q Plot -- MCQ Accuracies">
      <figcaption>Q-Q plot -- MCQ accuracies</figcaption>
    </figure>

    <figure>
      <img src="source-code/phase6_analysis/output/qq_plot_osq_scores.png" alt="Q-Q Plot -- OSQ Scores">
      <figcaption>Q-Q plot -- OSQ scores</figcaption>
    </figure>

    </div>

---
title: Analysis Gallery
---

# Analysis Gallery

Key figures from the empirical analysis, organized by research contribution. Click any figure to view full-size.

=== "Distractor Sensitivity"

    **Robustness of MCQ Evaluation Under Distractor Variation**

    How sensitive are MCQ scores to the design and positioning of distractor answer choices?

    <div class="figure-gallery" markdown>
    <div class="gallery-item" markdown>
    ![MCQ Deviation from Uniform](source-code/phase6_analysis/output_v3/fig_mcq_deviation_uniform.png)
    <figcaption>Deviation from uniform answer distribution</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Cramer's V Position Bias](source-code/phase6_analysis/output_v3/fig_cramers_v_position_bias.png)
    <figcaption>Cramer's V statistic for position bias</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ Position Heatmap](source-code/phase6_analysis/output/mcq_position_heatmap.png)
    <figcaption>Position selection heatmap across models</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ Wrong Answer Distribution](source-code/phase6_analysis/output/mcq_wrong_answer_distribution.png)
    <figcaption>Wrong answer distribution across positions</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Confusion Matrix -- All Models](source-code/phase6_analysis/output/mcq_confusion_matrix_all_models.png)
    <figcaption>Confusion matrix -- all models</figcaption>
    </div>
    </div>

=== "Consensus Judging"

    **LLM-as-a-Judge Reliability and Consensus**

    How reliable are LLM judges when scoring open-ended responses, and do multiple judges converge?

    <div class="figure-gallery" markdown>
    <div class="gallery-item" markdown>
    ![OSQ Violin -- GPT-5-mini](source-code/phase6_analysis/output_v3/osq_model_violin_openai_gpt-5-mini.png)
    <figcaption>OSQ score distribution -- GPT-5-mini</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Violin -- GPT-OSS 120B](source-code/phase6_analysis/output_v3/osq_model_violin_gpt-oss_120b.png)
    <figcaption>OSQ score distribution -- GPT-OSS 120B</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ KDE -- GPT-5-mini](source-code/phase6_analysis/output_v3/osq_score_kde_openai_gpt-5-mini.png)
    <figcaption>Kernel density estimate -- GPT-5-mini</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ KDE -- GPT-OSS 120B](source-code/phase6_analysis/output_v3/osq_score_kde_gpt-oss_120b.png)
    <figcaption>Kernel density estimate -- GPT-OSS 120B</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Rubric Dimensions -- All Judges](source-code/phase6_analysis/output/osq_rubric_dimensions_all_judges.png)
    <figcaption>Rubric dimension scores across all judges</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Violin Scores](source-code/phase6_analysis/output/osq_violin_scores.png)
    <figcaption>OSQ score violin plot -- all models</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Score Histogram](source-code/phase6_analysis/output/osq_score_histogram.png)
    <figcaption>OSQ score histogram</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Accuracy by INCOSE Category](source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_category.png)
    <figcaption>OSQ accuracy by INCOSE category (judge consensus)</figcaption>
    </div>
    </div>

=== "Modality Comparison"

    **MCQ vs OSQ Evaluation Modalities**

    How do multiple-choice and open-style question formats compare when evaluating the same models on the same domain content?

    <div class="figure-gallery" markdown>
    <div class="gallery-item" markdown>
    ![MCQ vs OSQ Scatter with Performance Regions](source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_regions.png)
    <figcaption>MCQ vs OSQ accuracy scatter with performance regions</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ vs OSQ Scatter -- Model Averaged](source-code/phase6_analysis/output_v3/mcq_vs_osq_scatter_regions_model_avg.png)
    <figcaption>MCQ vs OSQ scatter -- model-averaged scores</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ vs OSQ Scatter by INCOSE Category](source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_by_category.png)
    <figcaption>MCQ vs OSQ scatter by INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ vs OSQ Scatter by Top-Level Category](source-code/phase6_analysis/output_v3/fig_mcq_vs_osq_scatter_by_toplevel.png)
    <figcaption>MCQ vs OSQ scatter by top-level INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ-OSQ Delta by INCOSE Category](source-code/phase6_analysis/output_v3/fig_mcq_osq_delta_by_incose_category.png)
    <figcaption>Performance delta (MCQ minus OSQ) by INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ-OSQ Delta by Top-Level Category](source-code/phase6_analysis/output_v3/fig_mcq_osq_delta_by_incose_toplevel.png)
    <figcaption>Performance delta by top-level INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ Accuracy by INCOSE Category](source-code/phase6_analysis/output_v3/fig_mcq_accuracy_by_incose_category.png)
    <figcaption>MCQ accuracy by INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![MCQ Accuracy by Top-Level Category](source-code/phase6_analysis/output_v3/fig_mcq_accuracy_by_incose_toplevel.png)
    <figcaption>MCQ accuracy by top-level INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Accuracy by INCOSE Category](source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_category.png)
    <figcaption>OSQ accuracy by INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![OSQ Accuracy by Top-Level Category](source-code/phase6_analysis/output_v3/fig_osq_accuracy_by_incose_toplevel.png)
    <figcaption>OSQ accuracy by top-level INCOSE category</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Multi-Judge Rubric Comparison](source-code/phase6_analysis/output_v3/mcq_vs_osq_rubric_combined_multijudge_raw.png)
    <figcaption>Rubric scores across multiple LLM judges</figcaption>
    </div>
    </div>

=== "Token Efficiency"

    **Cost-Aware Response Length Trade-offs**

    What is the relationship between response length, token cost, and evaluation quality?

    <div class="figure-gallery" markdown>
    <div class="gallery-item" markdown>
    ![Pareto Efficiency Frontier](source-code/phase6_analysis/output_v3/pareto_efficiency_frontier.png)
    <figcaption>Pareto efficiency frontier -- quality vs cost</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Response Tokens by Model and Quality](source-code/phase6_analysis/output_v3/response_tokens_by_model_and_quality_avg_judge.png)
    <figcaption>Response tokens by model, colored by quality</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Token Length vs Quality -- Sorted](source-code/phase6_analysis/output_v3/tokenomics_length_vs_quality_sorted_worst_to_best.png)
    <figcaption>Response length vs quality -- sorted worst to best</figcaption>
    </div>
    <div class="gallery-item" markdown>
    ![Tokenomics Distribution](source-code/phase6_analysis/output/tokenomics_distribution.png)
    <figcaption>Token usage distribution</figcaption>
    </div>
    </div>

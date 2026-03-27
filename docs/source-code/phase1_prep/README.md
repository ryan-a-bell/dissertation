# Phase 1: Benchmark Preparation

## Overview
This phase downloads the SysEngBench dataset from HuggingFace, performs initial data exploration, and generates statistical analysis and visualizations of the benchmark composition.

## Purpose
Establish the foundation dataset for the dissertation research by:
- Obtaining the raw SysEngBench multiple-choice question (MCQ) dataset
- Understanding the distribution of questions across INCOSE categories
- Transforming and analyzing the benchmark structure
- Creating baseline statistics and visualizations

## Key Files

### Notebooks
- **`1.1_benchmark_download_and_analysis.ipynb`** - Main notebook that downloads SysEngBench from HuggingFace, exports to CSV, explodes INCOSE Handbook categories into separate rows, and generates distribution visualizations

### Data Files
- **`sysengbench.csv`** - Raw SysEngBench dataset exported from HuggingFace (1,144 questions)
- **`sysengbench.yaml`** - YAML configuration file for the benchmark dataset
- **`sample_employees.csv`** - Sample CSV file (appears to be test/example data)

## Configuration & Settings

### Environment Variables
- **`HF_TOKEN`** - HuggingFace API token (required)
  - Store in `.env` file in the project root
  - Required to access the `rabell/SysEngBench` dataset

### Dependencies
```bash
pip install datasets pandas matplotlib seaborn python-dotenv
```

## Inputs
- HuggingFace dataset: `rabell/SysEngBench` (test split)
- Environment: `.env` file with `HF_TOKEN`

## Outputs
- **`sysengbench.csv`** - 1,144 MCQs with 11 columns (Question ID, Tags, INCOSE Handbook Category, question, choiceA-D, answer, label, Justification)
- Statistical summaries printed to notebook output
- Visualizations:
  - Pie chart of INCOSE category distribution
  - Horizontal bar chart of sub-category distribution
  - Stacked bar chart by category

## Usage

1. Ensure `.env` file contains valid `HF_TOKEN`
2. Open `1.1_benchmark_download_and_analysis.ipynb` in Jupyter
3. Run all cells sequentially
4. Review generated CSV and visualizations

## Key Insights
- Total unique MCQs: 1,144
- Expanded to 1,210 rows when exploding multi-category questions
- Top INCOSE categories:
  - Specialty Engineering Activities (419 questions)
  - Cross-Cutting Systems Engineering Methods (276)
  - Lifecycle Stages (187)
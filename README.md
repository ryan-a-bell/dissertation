# Dissertation Repository

## Overview

This repository contains code, datasets, and documentation supporting the dissertation titled:

**"Evaluation Modality Alignment to Systems Engineering Task Types: A Methodological Study of Language Models' Domain-Specific and Task-Specific Effectiveness Using Distractor Variation and Consensus-Based Grading."**

The research systematically benchmarks Large Language Models (LLMs) using multiple evaluation modalities (Multiple-Choice Questions \[MCQ] and Open-Style Questions \[OSQ]) across Systems Engineering (SE) tasks aligned to INCOSE Handbook categories.

## Repository Structure

```
dissertation/
├── configs/               # YAML configuration files for evaluation
├── docs/                  # Project documentation (built with MkDocs)
├── figs/                  # Diagrams and figures (PlantUML and exported images)
├── src/                   # Source code organized by evaluation phases
│   ├── phase1_prep/       # Initial dataset tagging and preprocessing
│   ├── phase2_conversion/ # Conversion of MCQs to OSQs
│   ├── phase3_variants/   # Generation of distractor variant MCQs
│   ├── phase4_inference/  # Inference code for evaluating language models
│   ├── phase5_metrics/    # Calculation of evaluation metrics
│   └── phase6_tables/     # Aggregation and summary table generation
|   └── phase7_analysis/   # Analysis of the previous phases
├── .github/               # GitHub CI workflows
├── .env.template          # Template for API keys
├── environment.yml        # Conda environment specification
├── requirements.txt       # Python dependencies for venv
├── Makefile               # Automation commands
├── README.md              # Project overview (this file)
└── LICENSE                # License information
```

## Getting Started

### Environment Setup

You can use either **Conda** or Python's built-in **venv** for dependency management.

#### Using Conda

```bash
conda env create -f environment.yml
conda activate syseng-eval
```

#### Using venv

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API Keys

Copy the `.env.template` file to `.env` and populate it with your required API keys:

```bash
cp .env.template .env
```

## Documentation

Detailed documentation can be found under the `docs/` directory. Built documentation is served using MkDocs:

```bash
pip install mkdocs mkdocs-material mkdocs-jupyter
mkdocs serve
```

Then, open your browser to `http://127.0.0.1:8000` to view the documentation.

## Github Pages Website
A CI/CD pipeline is configured to host all of the documentation for this project.

The hosted information is populated from the `docs/` folder. The `docs/` folder is updated with the generate_docs.py file during the CI/CD process. The script takes all of the jupyter notebooks in the Phase folders and hosts them in addition or supplemental to the natively found documentation in the docs folder. 

## Diagrams

Diagrams (PlantUML source and exported PNGs) are maintained under the `figs/` directory. 

## Contributions

This work is in support of a PhD in Systems Engineering.

## License

This repository is provided under the [MIT License](LICENSE).

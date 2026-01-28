# metaeval

A Python library for **meta-evaluating LLM benchmarks**. Detect position bias in MCQs, convert questions to open-ended format, run consensus LLM judging, and statistically compare evaluation methods—all with publication-ready outputs.

## Features

- **Position Bias Detection**: Detect and quantify position bias in multiple-choice benchmarks using chi-square, Kruskal-Wallis, Friedman, and McNemar tests with effect size measurements (Cramér's V, Kendall's W, ε²)

- **MCQ↔OSQ Conversion**: LLM-powered pipeline to convert multiple-choice questions to open-ended format with auto-generated rubrics

- **LLM-as-a-Judge**: Multi-dimensional rubric-based scoring framework with consensus judging across multiple models

- **Format Comparison**: Statistical comparison of MCQ vs OSQ evaluation with correlations, paired tests, and bootstrap confidence intervals

- **Multi-Environment Inference**: Execute models via local Ollama, cloud APIs (OpenAI, Anthropic, Google), RunPod GPUs, or HPC clusters

- **Publication-Ready Reporting**: Generate LaTeX tables, markdown reports, and high-DPI figures

## Installation

```bash
# Basic installation
pip install metaeval

# With cloud execution support
pip install metaeval[cloud]

# With all optional dependencies
pip install metaeval[all]

# Development installation
pip install -e ".[dev]"
```

## Quick Start

### Detect Position Bias

```python
import metaeval

# Load your MCQ results (with columns: model, variant, is_correct, question_id)
import pandas as pd
results = pd.read_csv("mcq_results.csv")

# Analyze position bias
from metaeval.bias import PositionBiasAnalyzer

analyzer = PositionBiasAnalyzer(results)
report = analyzer.analyze("llama3.1-8b")

print(f"Bias detected: {report.has_significant_bias}")
print(f"Cramér's V: {report.effect_sizes['cramers_v'].value:.3f}")
```

### Convert MCQ to OSQ

```python
from metaeval.benchmark import MCQToOSQConverter

converter = MCQToOSQConverter(
    api_key="your-openai-key",
    model="gpt-4o",
    confidence_threshold=7,
)

conversions, classifications = converter.batch_convert(mcq_dataframe)
print(f"Converted {len(conversions)} questions")
```

### Compare MCQ vs OSQ Evaluation

```python
from metaeval.compare import FormatComparator

# aligned_data has: question_id, model, mcq_score (0/1), osq_score (0-100)
comparator = FormatComparator(aligned_data)
report = comparator.analyze("gemma-7b")

print(f"Correlation: r={report.correlations['spearman'].coefficient:.3f}")
print(f"Effect size: d={report.effect_sizes['cohens_d'].value:.3f}")
```

### Run LLM-as-a-Judge

```python
from metaeval.inference import LocalExecutor
from metaeval.judge import build_judge_prompt, parse_judgment

executor = LocalExecutor(model="llama3.1:8b")

prompt = build_judge_prompt(
    question="What is systems engineering?",
    expected_answer="Systems engineering is an interdisciplinary approach...",
    response="Systems engineering combines multiple disciplines...",
    prompt_style="multi_dimensional",
)

raw_judgment = executor.generate(prompt)
parsed = parse_judgment(raw_judgment)

print(f"Total score: {parsed.total_score}/100")
print(f"Scores: {parsed.scores.to_dict()}")
```

## CLI Usage

```bash
# Download a benchmark
metaeval download ryan-a-bell/SysEngBench -o data/

# Generate position variants
metaeval variants data/sysengbench.csv -o variants/

# Run position bias analysis
metaeval analyze bias results/mcq_results.csv -o analysis/ --format markdown

# Run format comparison
metaeval analyze compare results/aligned.csv -o analysis/

# Generate report
metaeval report analysis/results.json -o report.md --title "My Analysis"
```

## Module Overview

| Module | Description |
|--------|-------------|
| `benchmark` | Download, convert, and generate benchmark variants |
| `bias` | Position bias detection with `bias.stats` for statistical tests |
| `compare` | MCQ vs OSQ comparison with `compare.stats` for correlations |
| `judge` | LLM-as-a-Judge prompts, scoring, consensus, agreement metrics |
| `inference` | Model execution (local, API, RunPod, HPC) |
| `report` | LaTeX tables, markdown reports, publication figures |
| `parsers` | MCQ and OSQ result parsing utilities |

## Statistical Tests Available

### Position Bias (`metaeval.bias.stats`)
- Chi-square test for independence
- Kruskal-Wallis H-test
- Friedman test for repeated measures
- McNemar's test (pairwise)
- One-way ANOVA
- Effect sizes: Cramér's V, Kendall's W, ε²

### Format Comparison (`metaeval.compare.stats`)
- Pearson correlation
- Spearman rank correlation
- Wilcoxon signed-rank test
- Paired t-test
- Effect sizes: Cohen's d, Hedges' g, Glass's Δ
- Bootstrap confidence intervals

## Configuration

Create a `.env` file for API keys:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
HF_TOKEN=hf_...
RUNPOD_API_KEY=...
```

Or configure programmatically:

```python
from metaeval import Config

config = Config.from_env()
config.inference.temperature = 0.0
config.analysis.alpha = 0.05
config.analysis.bootstrap_iterations = 10000
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy metaeval

# Run linting
ruff check metaeval
```

## Citation

If you use metaeval in your research, please cite:

```bibtex
@software{metaeval2025,
  author = {Bell, Ryan},
  title = {metaeval: Meta-evaluation toolkit for LLM evaluation methods},
  year = {2025},
  url = {https://github.com/ryan-a-bell/dissertation}
}
```

## License

MIT License - see LICENSE file for details.

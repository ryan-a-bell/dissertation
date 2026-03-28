---
title: metaeval
---

# metaeval

A Python library for meta-evaluating LLM benchmarks. Detect position bias in MCQs, convert questions to open-ended format, run consensus LLM judging, and statistically compare evaluation methods.

**Version:** 0.1.0 | **Python:** >=3.10 | **License:** MIT

---

## Installation

```bash
pip install -e metaeval          # Core install
pip install -e "metaeval[cloud]" # Cloud providers (RunPod, SSH)
pip install -e "metaeval[all]"   # Everything (cloud, hpc, local, dev, docs)
pip install -e "metaeval[dev]"   # Dev tools (pytest, ruff, black, mypy)
```

---

## Package Architecture

```
metaeval/
├── benchmark/     # Download, convert MCQ->OSQ, generate variants
├── bias/          # Position bias detection and statistical tests
├── compare/       # MCQ vs OSQ format comparison
├── judge/         # Rubric definitions, prompts, consensus scoring
├── judges/        # Multi-provider LLM judge backends
├── inference/     # Local, API, RunPod, and HPC model execution
├── harness/       # lm-eval output parsing
├── parsers/       # MCQ and OSQ result parsing
├── prompts/       # Centralized prompt registry
├── report/        # LaTeX tables, markdown reports, figures
├── core/          # Config, types, logging, caching
└── cli/           # Command-line interface
```

---

## Core Capabilities

### Position Bias Detection

Analyze whether MCQ answer position affects model accuracy using chi-square, Kruskal-Wallis, Friedman, and McNemar tests with Cramer's V and Kendall's W effect sizes.

```python
from metaeval.bias import PositionBiasAnalyzer

analyzer = PositionBiasAnalyzer()
report = analyzer.analyze(results_dir="path/to/variant_results/")
report.summary()
```

### MCQ to OSQ Conversion

LLM-powered pipeline to convert multiple-choice questions into open-style questions with auto-generated grading rubrics.

```python
from metaeval.benchmark import MCQToOSQConverter

converter = MCQToOSQConverter(model="gpt-4o")
osq_dataset = converter.convert("sysengbench.csv", threshold=0.7)
```

### LLM-as-a-Judge

Multi-dimensional rubric-based scoring with consensus judging across multiple LLM providers.

```python
from metaeval.judges import create_judge
from metaeval.judge import ConsensusScorer

judge = create_judge("openai", model="gpt-4o")
scorer = ConsensusScorer(judges=[judge])
results = scorer.score(responses, rubric)
```

### Format Comparison

Statistical comparison of MCQ vs OSQ evaluation modalities with paired tests, correlations, and bootstrap confidence intervals.

```python
from metaeval.compare import FormatComparator

comparator = FormatComparator()
report = comparator.compare(mcq_results, osq_results)
report.summary()
```

### Multi-Environment Inference

Execute models across local (Ollama), cloud APIs (OpenAI, Anthropic, Google), RunPod GPUs, and HPC clusters.

```python
from metaeval.inference import APIExecutor

executor = APIExecutor(provider="openai", model="gpt-4o")
results = executor.run(questions)
```

### Publication-Ready Reporting

Generate LaTeX tables, markdown reports, and high-DPI figures suitable for academic publication.

```python
from metaeval.report import LaTeXTableGenerator, FigureExporter

latex = LaTeXTableGenerator()
latex.from_dataframe(df, caption="Model performance comparison")

fig_export = FigureExporter(dpi=300)
fig_export.save(fig, "output/figure.png")
```

---

## CLI Reference

The `metaeval` CLI provides access to the full pipeline:

| Command | Description |
|---------|-------------|
| `metaeval download` | Download benchmark datasets from Hugging Face |
| `metaeval convert` | Convert MCQ to OSQ format |
| `metaeval variants` | Generate position-rotated MCQ variants |
| `metaeval analyze bias` | Analyze position bias across variants |
| `metaeval analyze compare` | Compare MCQ vs OSQ evaluation formats |
| `metaeval judge` | Run LLM-as-a-Judge evaluation |
| `metaeval prompts list` | List available prompt templates |
| `metaeval report` | Generate publication-ready reports |
| `metaeval eval` | Run lm-eval harness integration |
| `metaeval results` | Parse and display lm-eval results |
| `metaeval config` | Manage configuration and API keys |

**Examples:**

```bash
# Download the SysEngBench dataset
metaeval download rabell/SysEngBench -o data/

# Generate position variants
metaeval variants data/sysengbench.csv -o data/variants/

# Analyze position bias
metaeval analyze bias data/variants/ --output results/bias/

# Compare MCQ vs OSQ formats
metaeval analyze compare --mcq results/mcq/ --osq results/osq/

# Run LLM judge evaluation
metaeval judge responses.csv openai gpt-4o --rubric rubrics/se.yaml

# Generate a report
metaeval report results/analysis.json -o report/ --format latex
```

---

## Supported Providers

| Provider | Module | Models |
|----------|--------|--------|
| OpenAI | `judges.openai` | GPT-4, GPT-4o, GPT-4o-mini |
| Anthropic | `judges.anthropic` | Claude 3.5/4 Sonnet, Claude 4 Opus |
| Ollama | `judges.ollama` | Any locally hosted model |
| OpenRouter | `judges.openrouter` | Multi-provider access |
| RunPod | `inference.runpod` | GPU cloud execution |
| HPC | `inference.hpc` | Dask-based cluster execution |

---

## Statistical Methods

metaeval implements the following statistical tests for rigorous evaluation:

**Position Bias:**
Chi-square test, Kruskal-Wallis H-test, Friedman test, McNemar test, ANOVA, with Cramer's V, Kendall's W, and epsilon-squared effect sizes.

**Format Comparison:**
Wilcoxon signed-rank test, paired t-test, Pearson and Spearman correlations, Cohen's d, Hedges' g, Glass's delta, bootstrap confidence intervals.

**Judge Agreement:**
Fleiss' kappa, Krippendorff's alpha, inter-judge correlation matrices.

---

## Development

```bash
cd metaeval
pip install -e ".[dev]"

# Run tests
pytest                     # All tests with coverage
pytest tests/test_bias     # Specific module
pytest -v                  # Verbose output

# Lint and format
ruff check metaeval        # Lint
black metaeval             # Format
mypy metaeval              # Type check (strict mode)
```

---

## Citation

```bibtex
@software{bell2025metaeval,
  title  = {metaeval: Meta-Evaluation Toolkit for LLM Benchmarks},
  author = {Bell, Ryan},
  year   = {2025},
  url    = {https://github.com/ryan-a-bell/dissertation}
}
```

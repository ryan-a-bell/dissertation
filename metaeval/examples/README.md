# Metaeval Examples

This directory contains Jupyter notebooks demonstrating metaeval functionality.

## Notebooks

| Notebook | Description |
|----------|-------------|
| [01_getting_started.ipynb](01_getting_started.ipynb) | Introduction to metaeval and basic usage |
| [02_position_bias_analysis.ipynb](02_position_bias_analysis.ipynb) | Detecting position bias in MCQ benchmarks |
| [03_mcq_to_osq_conversion.ipynb](03_mcq_to_osq_conversion.ipynb) | Converting MCQ to open-style questions |
| [04_llm_as_judge.ipynb](04_llm_as_judge.ipynb) | Using LLMs to evaluate responses |
| [05_format_comparison.ipynb](05_format_comparison.ipynb) | Comparing MCQ vs OSQ evaluation results |
| [06_configuration_guide.ipynb](06_configuration_guide.ipynb) | Configuration system guide |

## Requirements

Install metaeval and dependencies:

```bash
pip install metaeval
pip install jupyter matplotlib
```

For LLM judging:
- **Ollama** (local models): Install from https://ollama.com
- **OpenAI**: Set `OPENAI_API_KEY` environment variable
- **Anthropic**: Set `ANTHROPIC_API_KEY` environment variable
- **OpenRouter**: Set `OPENROUTER_API_KEY` environment variable

## Running Notebooks

```bash
cd examples
jupyter notebook
```

Or in VS Code:
1. Open a notebook file
2. Select Python kernel
3. Run cells

## Quick Start

```python
from metaeval.bias.detection import PositionBiasAnalyzer
from metaeval.judges import create_judge

# Analyze position bias
analyzer = PositionBiasAnalyzer(benchmark_data)
report = analyzer.analyze("model_name")
print(f"Bias detected: {report.has_significant_bias}")

# Judge responses
judge = create_judge("ollama", "llama3.1:8b")
result = judge.judge(question, expected_answer, response)
print(f"Score: {result['total_score']}")
```

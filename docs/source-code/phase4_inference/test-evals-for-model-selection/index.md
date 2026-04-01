---
title: Test Evaluations for Model Selection
---

# Test Evaluations for Model Selection

Preliminary evaluation runs used during model selection for the dissertation study. Each subdirectory contains raw `lm_eval` result JSON and sample JSONL files for a candidate model.

## Models Evaluated

| Model | Directory |
|-------|-----------|
| Anthropic Claude Sonnet 4.5 | `anthropic__claude-sonnet-4.5/` |
| Google Gemini 2.5 Pro | `google__gemini-2.5-pro/` |
| GPT-4o Mini | `gpt-4o-mini/` |
| GPT-5.1 | `gpt-5.1/` |
| OpenAI GPT-4.1 | `openai__gpt-4.1/` |
| OpenAI GPT-4o | `openai__gpt-4o/` |

## File Format

Each model directory contains:

- `results_*.json` -- Aggregate evaluation metrics from `lm_eval`
- `samples_sysengbench_*.jsonl` -- Per-question model responses and scores

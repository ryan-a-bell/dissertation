---
title: Judge Rubric Definitions
---

# OSQ LLM Judge Scored Outputs

Rubric-scored open-ended question (OSQ) outputs organized by judge model. Each subdirectory contains JSONL files with per-question judge scores across multiple judging methodologies (binary, multi-dimensional, G-Eval).

## Judge Models

| Model | Directory |
|-------|-----------|
| Anthropic Claude Sonnet 4.5 | `anthropic__claude-sonnet-4.5/` |
| Devstral 24B | `devstral__24b/` |
| Gemma 3 (1B, 4B, 12B, 27B) | `gemma3__*/` |
| Google Gemini 2.5 Flash | `google__gemini-2.5-flash/` |
| Llama 3.2 (1B, 3B) | `llama3.2__*/` |
| Llama 3.3 70B | `llama3.3__70b/` |
| Llama 4 16x17B | `llama4__16x17b/` |
| Mistral Large 123B | `mistral-large__123b/` |
| Mistral Small 3.2 24B | `mistral-small3.2__24b/` |
| Mixtral 8x22B | `mixtral__8x22b/` |
| OpenAI GPT-4.1 | `openai__gpt-4.1/` |
| Phi 3 14B / Phi 3.5 3.8B | `phi3__14b/`, `phi3.5__3.8b/` |
| Phi 4 14B / Phi 4 Mini 3.8B | `phi4__14b/`, `phi4-mini__3.8b/` |

## File Format

Each model directory contains JSONL sample files with judge-assigned scores per question, variant, and rubric methodology.

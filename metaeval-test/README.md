# Metaeval Pipeline Test

This directory contains a test setup to validate the full metaeval pipeline.

## Directory Structure

```
metaeval-test/
├── README.md              # This file
├── full_pipeline.ipynb    # Interactive notebook walking through all phases
├── data/                  # Downloaded benchmark data
├── variants/              # Generated position variants (A, B, C, D)
├── output/                # lm-eval inference results
├── judged/                # LLM-as-a-Judge results
└── analysis/              # Bias and comparison analysis results
```

## Quick Start

### Prerequisites

```bash
# Install metaeval
cd /home/user/dissertation/metaeval
pip install -e .

# Install lm-eval (for inference)
pip install lm-eval
```

### Run the Full Pipeline

```bash
cd /home/user/dissertation/metaeval-test

# 1. Download benchmark
metaeval download ryan-a-bell/SysEngBench -o data/

# 2. Generate position variants
metaeval variants data/ryan-a-bell_SysEngBench.csv -o variants/

# 3. Run inference with lm-eval (example with Ollama)
lm_eval \
  --model local-chat-completions \
  --model_args model=llama3.2:3b,base_url=http://localhost:11434/v1/chat/completions \
  --tasks ./sysengbench-a.yaml \
  --output_path output/ \
  --log_samples

# 4. View results
metaeval results list output/

# 5. Run bias analysis
metaeval analyze bias output/ -o analysis/

# 6. (Optional) Judge OSQ responses
metaeval judge output/sysengbench-osq/model/ --provider ollama -o judged/judged.jsonl

# 7. (Optional) MCQ vs OSQ comparison
metaeval analyze compare output/ --judged judged/ -o analysis/
```

## Using Existing Results

To test with existing results from the main dissertation pipeline:

```bash
# Link to existing lm-eval outputs
ln -sf /home/user/dissertation/src/phase4_inference/output ./output

# Then run analysis
metaeval analyze bias output/ -o analysis/
```

## Pipeline Phases

| Phase | Tool | Command | Notes |
|-------|------|---------|-------|
| 1. Download | metaeval | `metaeval download` | HuggingFace dataset |
| 2. Convert | metaeval | `metaeval convert` | Requires OpenAI API |
| 3. Variants | metaeval | `metaeval variants` | Creates A/B/C/D files |
| 4. Inference | lm-eval | `lm_eval --model ...` | See `metaeval eval` for docs |
| 5. Judge | metaeval | `metaeval judge` | Requires LLM API |
| 6. Analyze | metaeval | `metaeval analyze` | Bias + Compare |

## Expected Outputs

After running the full pipeline:

- `data/`: 1 CSV file (1,144 MCQ questions)
- `variants/`: 4 CSV files (A, B, C, D variants)
- `output/`: lm-eval results directories per task/model
- `judged/`: JSONL files with judge scores
- `analysis/`: JSON/Markdown analysis reports

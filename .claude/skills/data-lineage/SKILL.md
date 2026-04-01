---
name: data-lineage
description: Trace data flow across the 6-phase research pipeline. Maps input/output files between phases, flags broken links where expected inputs are missing, and shows the full data dependency graph.
allowed-tools: Read, Grep, Glob, Bash(find *), Bash(ls *), Bash(wc *)
---

# Data Lineage

Map the data flow across the 6-phase research pipeline in `src/`, showing what each phase produces and what the next phase consumes.

## Pipeline Structure

| Phase | Directory | Purpose |
|-------|-----------|---------|
| 1 | `src/phase1_prep/` | Data preparation -- produces the primary benchmark CSV |
| 2 | `src/phase2_conversion/` | MCQ-to-OSQ conversion -- produces filtered open-style questions |
| 3 | `src/phase3_variants/` | Position rotation -- produces variant CSVs (a-d) |
| 4 | `src/phase4_inference/` | Model inference -- produces JSONL output per model/variant |
| 5 | `src/phase5_llm_as_a_judge/` | LLM judging -- produces scored JSONL output |
| 6 | `src/phase6_analysis/` | Analysis -- produces figures, tables, statistical results |

### Known Key Artifacts

| File | Phase | Role |
|------|-------|------|
| `src/phase1_prep/sysengbench.csv` | 1 output | Primary benchmark (1,144 MCQs) |
| `src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv` | 2 output | Converted OSQs (845 questions) |
| `src/phase3_variants/sysengbench_[a-d].csv` | 3 output | Position-rotated MCQ variants |
| `src/phase4_inference/output/**/*.jsonl` | 4 output | Inference results (IMMUTABLE) |
| `src/phase5_llm_as_a_judge/judged_outputs/**/*` | 5 output | Judge scores (IMMUTABLE) |

## Procedure

### Step 1: Inventory each phase

For each phase directory, catalog:
- **Scripts/notebooks**: `.py`, `.ipynb`, `.sh` files (these define the processing logic)
- **Input references**: Scan scripts for file paths, `pd.read_csv()`, `open()`, `json.load()`, `glob()`, and `argparse` arguments that reference data files
- **Output files**: Data files present in the directory (`.csv`, `.jsonl`, `.json`, `.parquet`, `.pkl`)
- **Subdirectory structure**: Note `output/`, `artifacts*/`, etc.

### Step 2: Trace dependencies

For each script in phase N, determine:
- Which files from phase N-1 (or earlier) it reads
- Which files it writes/produces
- Any external data sources (URLs, API calls)

Build a directed graph: `phase_X/file_A --> phase_Y/script_B --> phase_Y/file_C`

### Step 3: Validate links

Check that every input file referenced by a phase's scripts actually exists on disk. Flag:
- **Broken links**: A script references a file that doesn't exist
- **Stale outputs**: An output file is older than the script that generates it (may need re-running)
- **Immutable violations**: Any write operations targeting `phase4_inference/output/` or `phase5_llm_as_a_judge/judged_outputs/`

### Step 4: External dependencies

Note any scripts that require:
- API keys (references to env vars like `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- External services (RunPod, OpenRouter, HuggingFace)
- Large downloads or model weights

### Step 5: Lineage summary

Produce the full lineage from raw data to final analysis outputs.

## Output Format

```
## Data Lineage Report

### Pipeline Overview
- Total phases: 6
- Total scripts: N
- Total data files: N
- Broken links: N

### Phase-by-Phase Lineage

#### Phase 1: Preparation
**Scripts**: prep_data.py, ...
**Inputs**: <external sources>
**Outputs**:
- sysengbench.csv (1,144 rows)

#### Phase 2: Conversion
**Scripts**: convert.py, ...
**Inputs**:
- phase1_prep/sysengbench.csv
**Outputs**:
- artifacts_mcq2osq/sysengbench_osq_filtered.csv (845 rows)

...

### Dependency Graph
```
phase1/sysengbench.csv
  --> phase2/convert.py --> phase2/sysengbench_osq_filtered.csv
  --> phase3/rotate.py --> phase3/sysengbench_[a-d].csv
       --> phase4/infer.py --> phase4/output/*.jsonl
            --> phase5/judge.py --> phase5/judged_outputs/*.jsonl
                 --> phase6/analyze.py --> phase6/figures/*
```

### Broken Links
- <phase>/<script>:<line> references `<path>` -- file not found

### External Dependencies
- <phase>/<script>: requires <API_KEY>, <service>

### Immutability Check
- phase4/output/: OK (no write operations detected)
- phase5/judged_outputs/: OK
```

Omit sections with zero results.

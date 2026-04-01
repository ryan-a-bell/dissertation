# CLAUDE.md

## Project Overview

This repository contains a doctoral dissertation on meta-evaluation of Large Language Models using the SysEngBench benchmark. It includes a 6-phase research pipeline, a standalone Python package (`metaeval`), a documentation site, and the LaTeX manuscript.

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/` | Research code organized in 6 phases (prep, conversion, variants, inference, judging, analysis) |
| `metaeval/` | Installable Python package for benchmark evaluation (CLI tool + library) |
| `docs/` | MkDocs documentation site source |
| `manuscript/` | Dissertation LaTeX source (`overleaf/`), presentation slides, and reviews |
| `scripts/` | Automation scripts (doc generation, downloads) |
| `viz/` | Repository visualizations and Gource outputs |

## Build and Serve Commands

Documentation is built with MkDocs Material and procedurally generated from source.

```bash
make docs          # Full build: clean, generate, mkdocs build
make docs-serve    # Generate and serve locally with hot reload
make docs-build    # Build only (no generation step)
make clean-docs    # Remove generated doc files
```

The generation step runs `scripts/generate_docs.py`, which copies `src/` into `docs/source-code/`, generates CSV preview stubs, PDF download links, publications index, and copies `README.md` to `docs/index.md`.

## Refreshing the Dissertation Timeline

The timeline on the docs landing page (`docs/index.md`) is a pre-rendered SVG from a PlantUML source file.

**Source:** `docs/assets/timeline.puml`
**Rendered:** `docs/assets/timeline.svg`

To update the timeline:

1. Edit `docs/assets/timeline.puml` with the desired changes.
2. Re-render the SVG:
   ```bash
   java -jar plantuml.jar -tsvg -o docs/assets/ docs/assets/timeline.puml
   ```
3. Commit both `timeline.puml` and `timeline.svg`.

## metaeval Package Development

The `metaeval/` directory is a standalone, installable Python package targeting Python 3.10+.

### Installation

```bash
pip install -e metaeval          # Core install
pip install -e "metaeval[dev]"   # With dev tools (pytest, ruff, black, mypy, pre-commit)
pip install -e "metaeval[all]"   # Everything (cloud, hpc, local, dev, docs)
```

### Running Tests

```bash
cd metaeval
pytest                     # All tests with coverage (preconfigured in pyproject.toml)
pytest tests/test_bias     # Specific module
pytest -v                  # Verbose output
```

Pytest is configured with `--cov=metaeval --cov-report=term-missing` by default.

### Linting and Formatting

```bash
ruff check metaeval        # Lint (rules: E, F, I, N, W, UP; line-length 100)
black metaeval             # Format
mypy metaeval              # Type check (strict mode enabled)
```

## CI/CD Pipeline

- GitHub Actions (`.github/workflows/ci.yml`) deploys documentation on push to `main`/`master`.
- The pipeline runs `scripts/generate_docs.py`, sanitizes CSVs for `mkdocs-table-reader`, then deploys via `mkdocs gh-deploy --force`.
- Docs site: `https://ryan-a-bell.github.io/dissertation/`

## Environment Variables

Required API keys are defined in `.env.template`:

- `OPENAI_API_KEY`
- `HF_TOKEN`
- `RUNPOD_API_KEY`
- `OPENROUTER_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

The `metaeval` package loads these via `python-dotenv`. Never commit `.env` files.

## Data and File Conventions

### Key Datasets

| File | Description |
|------|-------------|
| `src/phase1_prep/sysengbench.csv` | Primary benchmark: 1,144 MCQs |
| `src/phase2_conversion/artifacts_mcq2osq/sysengbench_osq_filtered.csv` | Converted OSQs: 845 questions |
| `src/phase3_variants/sysengbench_[a-d].csv` | Position-rotated MCQ variants |

### Immutable Research Artifacts

The following directories contain finalized research outputs. Treat them as read-only:

- `src/phase4_inference/output/` -- model inference results (JSONL by variant and model)
- `src/phase5_llm_as_a_judge/judged_outputs/` -- LLM judge scoring results

## Documentation Conventions

- Theme: MkDocs Material with dark/light toggle.
- Navigation is controlled by `docs/.pages.yml` via `mkdocs-awesome-pages-plugin`.
- Jupyter notebooks are embedded via `mkdocs-jupyter` with execution disabled (rendered as-is).
- CSV files are previewed inline via `mkdocs-table-reader-plugin`.
- `src/phase6_analysis/output_v3/` is the authoritative source for all analysis figures and tables. The analysis gallery (`docs/analysis-gallery.md`) references only `output_v3/` artifacts. Do not reference `output/` or `output_v2/` in the gallery.

## Commit and Branch Conventions

- Commits are signed with SSH-based GPG keys.
- `main` is the deployment branch (triggers CI).
- Feature branches use `claude/*` naming for Claude Code work.

## Manuscript

- LaTeX dissertation source: `manuscript/overleaf/`
- Reviews and feedback: `manuscript/reviews/`
- Presentation slides: `manuscript/presentation/`
- Candidate additions: `manuscript/consider-adding/`

## Things to Avoid

- Do not edit files in `docs/source-code/` -- they are regenerated by `scripts/generate_docs.py` and will be overwritten.
- Do not commit `.env` files or API keys.
- Do not modify raw data files in `src/phase4_inference/output/` or `src/phase5_llm_as_a_judge/judged_outputs/`.
- Do not enable notebook execution in the docs build -- it is disabled by design.

## Project Preferences

- Do not use emojis in code, documentation, commit messages, or any file output unless the user explicitly requests it.

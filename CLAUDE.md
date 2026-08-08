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

The generation step runs `scripts/generate_docs.py`, which copies `src/` into `docs/source-code/`, generates CSV preview stubs, PDF download links, and copies `README.md` to `docs/index.md`.

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

## Documentation System

### Navigation (.pages.yml Hierarchy)

Navigation is controlled by `mkdocs-awesome-pages-plugin`, which discovers `.pages.yml` files at each directory level. There are 8 `.pages.yml` files forming a hierarchy:

| File | Controls |
|------|----------|
| `docs/.pages.yml` | Top-level nav (Home, Key Findings, Analysis Gallery, metaeval, Source Code, Glossary) |
| `docs/source-code/.pages.yml` | Phase listing (phases 1-6) |
| `docs/source-code/phase[1-6]_*/.pages.yml` | Page ordering within each phase |

When adding a new page, update the relevant `.pages.yml` to control its position. Without an entry, pages sort alphabetically.

### Content Generation Pipeline

`scripts/generate_docs.py` transforms source content into docs pages. The full data flow:

```
src/                  --> docs/source-code/    (mirrors tree, respects .docsignore)
viz/                  --> docs/visualizations/  (video embeds, notebook refs)
README.md             --> docs/index.md         (with adjusted links)
```

Run via `make docs` or `make docs-serve`. The script handles special file types:
- **CSV files**: generates a markdown stub using `{{ read_csv() }}` syntax
- **PDF files**: generates a markdown stub with a download link
- **Notebooks**: copied as-is (rendered by mkdocs-jupyter)
- **Videos (.mp4)**: generates HTML5 embed with download link

### Preserved Files (Safe to Hand-Edit)

The generation script **preserves** certain files under `docs/source-code/` during regeneration. These survive `make docs` and are safe to edit by hand:

- `index.md` (at any level)
- `.pages.yml` (at any level)
- `modality-evaluation-pipeline.jpg`

All other files under `docs/source-code/` are overwritten on each run.

### Excluding Content with `.docsignore`

**Location:** `src/.docsignore`

This file controls which paths under `src/` are excluded from the generated `docs/source-code/` tree. It uses a simple line-based format:

- Paths are **relative to `src/`**.
- Directories use a **trailing `/`** (e.g., `phase6_analysis/archive/`).
- Files can be listed without a trailing slash.
- Lines starting with `#` are comments. Blank lines are ignored.
- Matching uses **prefix matching** (`startswith`), not glob or regex. A path is excluded if it starts with any listed pattern.

Current exclusions:

```
phase4_inference/dodhpc/
phase4_inference/test-evals-for-model-selection/
phase5_llm_as_a_judge/unused-rubrics/
phase6_analysis/archive/
phase6_analysis/output/
phase6_analysis/output_v2/
```

To exclude a new directory from the docs site, add its `src/`-relative path to this file and re-run `make docs`.

Note: `.docsignore` is separate from `.gitignore`. The generation script also respects `.gitignore` patterns (via the `pathspec` library) and always skips `__pycache__` and `.ipynb_checkpoints`.

### MkDocs Plugins and Syntax

The site uses these plugins (configured in `mkdocs.yml`):

| Plugin | Purpose | Usage |
|--------|---------|-------|
| `awesome-pages` | Navigation via `.pages.yml` | Automatic discovery |
| `mkdocs-jupyter` | Render notebooks as pages | Place `.ipynb` files in docs tree (execution disabled) |
| `table-reader` | Inline CSV display | `{{ read_csv('./file.csv') }}` in markdown |
| `glightbox` | Image lightbox gallery | Automatic on all images |
| `mkdocstrings` | Python API docs | `:::module.path` blocks (source path: `src/`) |
| `search` | Full-text search | Built-in, custom separator configured |
| `social` | Social media cards | Conditional via `CARDS` env var |

Mermaid diagrams are supported via fenced code blocks (` ```mermaid `) and rendered client-side. They are theme-aware and re-render on light/dark toggle.

### Custom Theming (CSS/JS)

Three CSS files provide layered styling:

| File | Purpose | Lines |
|------|---------|-------|
| `docs/stylesheets/extra.css` | Mermaid diagrams, figure gallery grid, hero banner, phase nav | 261 |
| `docs/stylesheets/nps_custom_css.css` | NPS brand colors (navy #003366, gold #FFD700), header/sidebar gradients, admonitions, dark mode | 431 |
| `docs/stylesheets/modern_mkdocs_css.css` | Glassmorphism theme, gradient cards, animated backgrounds (currently unused) | 577 |

JavaScript:
- `docs/assets/js/extra.js` -- Mermaid initialization with theme detection and a MutationObserver that re-renders diagrams on light/dark toggle.
- `docs/javascripts/mkdocs_theme_switcher.js` -- Multi-theme switcher widget (currently disabled in `mkdocs.yml`). Supports keyboard shortcut Ctrl+Shift+T.

### Analysis Gallery

- `src/phase6_analysis/output_v3/` is the authoritative source for all analysis figures and tables.
- The analysis gallery (`docs/analysis-gallery.md`) references only `output_v3/` artifacts.
- Do not reference `output/` or `output_v2/` in the gallery.

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

- Do not edit generated files in `docs/source-code/` -- they are overwritten by `scripts/generate_docs.py`. Only `index.md`, `.pages.yml`, and `modality-evaluation-pipeline.jpg` are preserved (see "Preserved Files" above).
- Do not commit `.env` files or API keys.
- Do not modify raw data files in `src/phase4_inference/output/` or `src/phase5_llm_as_a_judge/judged_outputs/`.
- Do not enable notebook execution in the docs build -- it is disabled by design.

## Project Preferences

- Do not use emojis in code, documentation, commit messages, or any file output unless the user explicitly requests it.

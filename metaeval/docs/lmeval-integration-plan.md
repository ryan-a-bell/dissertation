# lm-eval Integration Plan

> **Goal**: Wrap lm-eval harness within metaeval to provide a unified evaluation experience with shared data schemas, seamless result flow, and single CLI interface.

## Executive Summary

Currently, metaeval and lm-eval operate as loosely coupled systems with manual handoffs:
- metaeval generates task YAMLs
- Users manually invoke lm-eval CLI
- Users manually import results for analysis

This plan unifies them into a cohesive pipeline where `metaeval eval` handles end-to-end evaluation with automatic result ingestion.

---

## 1. Unified Data Schemas

### 1.1 Core Evaluation Types

```python
# metaeval/core/types.py (additions)

@dataclass
class EvalConfig:
    """Configuration for an evaluation run."""
    model: str                          # e.g., "ollama/llama3.1:8b", "openai/gpt-4o"
    benchmark: str                      # e.g., "sysenebench", "sysenebench-osq"
    format: Literal["mcq", "osq"]       # Question format
    variant: str | None = None          # Position variant for bias testing
    num_fewshot: int = 0
    batch_size: int | str = "auto"
    temperature: float = 0.0
    max_tokens: int = 512

    # Execution settings
    backend: Literal["lmeval", "direct"] = "lmeval"  # lmeval harness or direct API
    provider: Literal["ollama", "openai", "anthropic", "openrouter", "hpc"] = "ollama"

    def to_lmeval_args(self) -> list[str]:
        """Convert to lm-eval CLI arguments."""
        ...


@dataclass
class EvalRun:
    """A complete evaluation run with metadata and results."""
    run_id: str                         # UUID for this run
    config: EvalConfig
    status: Literal["pending", "running", "completed", "failed"]

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Results (populated after completion)
    results: EvalResults | None = None

    # Paths
    output_dir: Path | None = None
    lmeval_results_path: Path | None = None
    lmeval_samples_path: Path | None = None


@dataclass
class EvalResults:
    """Unified results from an evaluation run."""
    # Aggregate metrics
    accuracy: float | None = None       # MCQ accuracy (0-1)
    mean_score: float | None = None     # OSQ mean score (0-100)
    stderr: float | None = None

    # Per-question results
    mcq_results: list[MCQResult] = field(default_factory=list)
    osq_results: list[OSQResult] = field(default_factory=list)
    judged_results: list[JudgedResult] = field(default_factory=list)

    # Metadata from lm-eval
    n_samples: int = 0
    eval_time_seconds: float = 0.0
    model_name: str = ""

    # Raw lm-eval output (for debugging)
    raw_lmeval_results: dict | None = None


@dataclass
class ModelSpec:
    """Normalized model specification."""
    provider: str                       # ollama, openai, anthropic, openrouter
    model_id: str                       # llama3.1:8b, gpt-4o, claude-3-5-sonnet
    display_name: str                   # Human-readable name

    # Provider-specific settings
    base_url: str | None = None
    api_key_env: str | None = None

    @classmethod
    def parse(cls, spec: str) -> "ModelSpec":
        """Parse 'provider/model' format."""
        if "/" in spec:
            provider, model_id = spec.split("/", 1)
        else:
            provider, model_id = "ollama", spec
        return cls(provider=provider, model_id=model_id, display_name=spec)

    def to_lmeval_model_args(self) -> str:
        """Generate lm-eval --model_args string."""
        ...
```

### 1.2 Result Parsing Types

```python
# metaeval/harness/results.py (new file)

@dataclass
class LMEvalResultsFile:
    """Parsed lm-eval results.json structure."""
    results: dict[str, dict[str, float]]    # task -> metrics
    configs: dict[str, dict]                 # task -> config
    n_samples: dict[str, dict[str, int]]    # task -> {original, effective}
    model_source: str
    model_name: str
    total_evaluation_time_seconds: float
    git_hash: str
    date: float

    @classmethod
    def from_json(cls, path: Path) -> "LMEvalResultsFile":
        """Load from lm-eval output file."""
        ...

    def get_accuracy(self, task: str) -> float | None:
        """Extract accuracy metric for a task."""
        ...

    def get_metric(self, task: str, metric: str) -> float | None:
        """Extract any metric for a task."""
        ...


@dataclass
class LMEvalSample:
    """Single sample from lm-eval samples.jsonl."""
    doc: dict                           # Original document fields
    resps: list                         # Model responses with logprobs
    filtered_resps: list                # Post-filtering responses
    target: str | int                   # Expected answer

    # Computed fields
    question_id: int = 0
    is_correct: bool = False
    model_answer: str = ""

    @classmethod
    def from_json(cls, line: dict) -> "LMEvalSample":
        """Parse a single JSONL line."""
        ...

    def to_mcq_result(self, model: str, variant: str = "") -> MCQResult:
        """Convert to metaeval MCQResult."""
        ...

    def to_osq_result(self, model: str) -> OSQResult:
        """Convert to metaeval OSQResult."""
        ...
```

### 1.3 Schema Mapping

| lm-eval Field | metaeval Type | Notes |
|---------------|---------------|-------|
| `results.[task].acc` | `EvalResults.accuracy` | Direct mapping |
| `results.[task].acc_stderr` | `EvalResults.stderr` | Direct mapping |
| `config.model_name` | `EvalResults.model_name` | Direct mapping |
| `total_evaluation_time_seconds` | `EvalResults.eval_time_seconds` | Direct mapping |
| `samples.jsonl` lines | `MCQResult` / `OSQResult` | Via parser |
| `doc.question_id` | `*.question_id` | Universal ID |

---

## 2. Module Architecture

### 2.1 New Module: `metaeval/harness/`

```
metaeval/harness/
├── __init__.py
├── runner.py          # LMEvalRunner - orchestrates lm-eval execution
├── results.py         # Result parsing (LMEvalResultsFile, LMEvalSample)
├── models.py          # ModelSpec, model registry
├── tasks.py           # Task generation (moved from benchmark/tasks.py)
└── backends/
    ├── __init__.py
    ├── base.py        # ExecutionBackend ABC
    ├── local.py       # LocalBackend (Ollama via lm-eval)
    ├── api.py         # APIBackend (OpenAI/Anthropic via lm-eval)
    └── hpc.py         # HPCBackend (SLURM job submission)
```

### 2.2 Core Classes

```python
# metaeval/harness/runner.py

class LMEvalRunner:
    """Unified lm-eval execution wrapper."""

    def __init__(self, config: EvalConfig):
        self.config = config
        self.backend = self._get_backend()

    def run(self, progress_callback: Callable | None = None) -> EvalRun:
        """Execute evaluation and return results."""
        run = EvalRun(
            run_id=str(uuid.uuid4()),
            config=self.config,
            status="pending"
        )

        try:
            # 1. Generate task YAML if needed
            task_path = self._ensure_task_yaml()

            # 2. Execute via backend
            run.status = "running"
            run.started_at = datetime.now()

            output_dir = self.backend.execute(
                task_path=task_path,
                model_spec=ModelSpec.parse(self.config.model),
                progress_callback=progress_callback
            )

            # 3. Parse results
            run.output_dir = output_dir
            run.results = self._parse_results(output_dir)
            run.status = "completed"

        except Exception as e:
            run.status = "failed"
            run.results = EvalResults()
            raise
        finally:
            run.completed_at = datetime.now()

        return run

    def _parse_results(self, output_dir: Path) -> EvalResults:
        """Parse lm-eval output into unified results."""
        results_file = LMEvalResultsFile.from_json(output_dir / "results.json")
        samples = self._parse_samples(output_dir)

        return EvalResults(
            accuracy=results_file.get_accuracy(self.config.benchmark),
            n_samples=len(samples),
            mcq_results=[s.to_mcq_result(self.config.model) for s in samples]
                        if self.config.format == "mcq" else [],
            osq_results=[s.to_osq_result(self.config.model) for s in samples]
                        if self.config.format == "osq" else [],
            raw_lmeval_results=results_file.__dict__
        )
```

### 2.3 Backend Abstraction

```python
# metaeval/harness/backends/base.py

class ExecutionBackend(ABC):
    """Abstract backend for lm-eval execution."""

    @abstractmethod
    def execute(
        self,
        task_path: Path,
        model_spec: ModelSpec,
        progress_callback: Callable | None = None
    ) -> Path:
        """
        Execute lm-eval and return output directory.

        Args:
            task_path: Path to task YAML
            model_spec: Model specification
            progress_callback: Called with (current, total) progress

        Returns:
            Path to output directory containing results.json
        """
        pass

    @abstractmethod
    def check_availability(self) -> tuple[bool, str]:
        """Check if backend is available. Returns (available, message)."""
        pass


# metaeval/harness/backends/local.py

class LocalBackend(ExecutionBackend):
    """Execute lm-eval locally with Ollama."""

    def execute(self, task_path: Path, model_spec: ModelSpec,
                progress_callback: Callable | None = None) -> Path:
        output_dir = Path(f"output/{model_spec.model_id}/{task_path.stem}")
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "lm_eval",
            "--model", "local-chat-completions",
            "--model_args", model_spec.to_lmeval_model_args(),
            "--tasks", str(task_path),
            "--output_path", str(output_dir),
            "--log_samples",
            "--batch_size", "auto",
        ]

        # Stream output for progress
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        for line in process.stdout:
            if progress_callback and "Running" in line:
                # Parse progress from lm-eval output
                progress_callback(...)

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"lm-eval failed with code {process.returncode}")

        return output_dir
```

### 2.4 Updated Module Map

```
metaeval/
├── core/
│   ├── types.py        # + EvalConfig, EvalRun, EvalResults, ModelSpec
│   ├── config.py       # + HarnessConfig section
│   └── ...
├── harness/            # NEW - lm-eval integration
│   ├── runner.py       # LMEvalRunner
│   ├── results.py      # Result parsing
│   ├── models.py       # Model registry
│   ├── tasks.py        # Task generation (from benchmark/)
│   └── backends/       # Execution backends
├── benchmark/
│   ├── schemas.py      # Unchanged
│   ├── convert.py      # Unchanged
│   └── variants.py     # Unchanged
├── parsers/
│   ├── mcq.py          # + integration with harness results
│   └── osq.py          # + integration with harness results
├── judges/             # Unchanged
├── judge/              # Unchanged
├── bias/               # + accept EvalResults directly
├── compare/            # + accept EvalResults directly
└── cli/
    └── main.py         # + eval, results commands
```

---

## 3. CLI Commands

### 3.1 New Commands

```bash
# Core evaluation command
metaeval eval \
  --model ollama/llama3.1:8b \
  --benchmark sysenebench \
  --format mcq \
  --output ./results/

# With position variant for bias testing
metaeval eval \
  --model ollama/llama3.1:8b \
  --benchmark sysenebench \
  --format mcq \
  --variant position_b \
  --output ./results/

# OSQ with automatic judging
metaeval eval \
  --model ollama/llama3.1:8b \
  --benchmark sysenebench-osq \
  --format osq \
  --judge ollama/llama3.1:70b \
  --output ./results/

# List available models/benchmarks
metaeval models list
metaeval benchmarks list

# Check provider connectivity
metaeval providers check

# View/manage results
metaeval results list
metaeval results show <run-id>
metaeval results export <run-id> --format csv

# Import external lm-eval results
metaeval results import ./path/to/lmeval/output/

# Generate task YAML (for manual lm-eval runs)
metaeval tasks generate \
  --benchmark sysenebench \
  --format mcq \
  --output ./tasks/
```

### 3.2 CLI Structure

```python
# metaeval/cli/main.py

@app.command()
def eval(
    model: str = typer.Option(..., help="Model spec (provider/model)"),
    benchmark: str = typer.Option(..., help="Benchmark name"),
    format: str = typer.Option("mcq", help="Question format (mcq/osq)"),
    variant: str = typer.Option(None, help="Position variant"),
    judge: str = typer.Option(None, help="Judge model for OSQ"),
    output: Path = typer.Option("./output", help="Output directory"),
    backend: str = typer.Option("local", help="Execution backend"),
):
    """Run evaluation with lm-eval harness."""
    config = EvalConfig(
        model=model,
        benchmark=benchmark,
        format=format,
        variant=variant,
    )

    runner = LMEvalRunner(config)

    with Progress() as progress:
        task = progress.add_task("Evaluating...", total=100)

        def update_progress(current, total):
            progress.update(task, completed=current * 100 // total)

        run = runner.run(progress_callback=update_progress)

    # Auto-judge if OSQ
    if format == "osq" and judge:
        run.results.judged_results = _judge_results(run.results.osq_results, judge)

    # Save results
    _save_run(run, output)

    # Print summary
    console.print(f"[green]Completed![/green] Run ID: {run.run_id}")
    console.print(f"Accuracy: {run.results.accuracy:.2%}")
```

### 3.3 Seamless Analysis Flow

```bash
# Old workflow (fragmented)
python -c "from metaeval.benchmark.tasks import ..."  # Generate YAML
lm_eval --model ... --tasks ...                        # Manual execution
# Manual JSON parsing
metaeval analyze bias ./output/                        # Hope it works

# New workflow (unified)
metaeval eval --model ollama/llama3.1:8b --benchmark sysenebench --format mcq
metaeval analyze bias --last                          # Uses last run automatically
metaeval analyze compare --runs run1,run2             # Compare by run ID
```

---

## 4. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         metaeval eval                               │
│                                                                     │
│  ┌─────────────┐     ┌──────────────┐     ┌───────────────────┐   │
│  │ EvalConfig  │────▶│ LMEvalRunner │────▶│ ExecutionBackend  │   │
│  └─────────────┘     └──────────────┘     └───────────────────┘   │
│         │                    │                      │              │
│         │                    │                      ▼              │
│         │                    │            ┌─────────────────┐      │
│         │                    │            │    lm_eval      │      │
│         │                    │            │  (subprocess)   │      │
│         │                    │            └─────────────────┘      │
│         │                    │                      │              │
│         │                    ▼                      ▼              │
│         │           ┌──────────────┐     ┌─────────────────┐      │
│         │           │ ResultParser │◀────│ results.json    │      │
│         │           └──────────────┘     │ samples.jsonl   │      │
│         │                    │           └─────────────────┘      │
│         │                    ▼                                     │
│         │           ┌──────────────┐                               │
│         └──────────▶│  EvalRun     │                               │
│                     │  + Results   │                               │
│                     └──────────────┘                               │
│                            │                                       │
└────────────────────────────┼───────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      Analysis Pipeline        │
              │                              │
              │  ┌────────┐  ┌────────────┐  │
              │  │  Bias  │  │  Compare   │  │
              │  └────────┘  └────────────┘  │
              │                              │
              │  ┌────────┐  ┌────────────┐  │
              │  │ Judge  │  │  Report    │  │
              │  └────────┘  └────────────┘  │
              └──────────────────────────────┘
```

---

## 5. Implementation Phases

### Phase 1: Core Integration (Week 1-2)

**Goal**: Basic `metaeval eval` working with local Ollama

- [ ] Create `metaeval/harness/` module structure
- [ ] Implement `EvalConfig`, `EvalRun`, `EvalResults` in `core/types.py`
- [ ] Implement `ModelSpec` with provider parsing
- [ ] Implement `LMEvalResultsFile` parser
- [ ] Implement `LMEvalSample` parser with MCQ/OSQ conversion
- [ ] Implement `LocalBackend` for Ollama execution
- [ ] Implement basic `LMEvalRunner`
- [ ] Add `metaeval eval` CLI command
- [ ] Add `metaeval results list/show` commands

**Deliverable**: Can run `metaeval eval --model llama3.1 --benchmark sysenebench`

### Phase 2: Result Integration (Week 2-3)

**Goal**: Seamless flow from eval to analysis

- [ ] Update `bias/detection.py` to accept `EvalResults` directly
- [ ] Update `compare/analysis.py` to accept `EvalResults` directly
- [ ] Add `--last` flag to analysis commands
- [ ] Add `--runs` flag for multi-run comparison
- [ ] Implement result storage/retrieval by run ID
- [ ] Add `metaeval results import` for external lm-eval outputs
- [ ] Add `metaeval results export` (CSV, JSON)

**Deliverable**: `metaeval eval ... && metaeval analyze bias --last`

### Phase 3: Multi-Backend Support (Week 3-4)

**Goal**: Support API providers and HPC

- [ ] Implement `APIBackend` for OpenAI/Anthropic via lm-eval
- [ ] Implement `HPCBackend` for SLURM job submission
- [ ] Add `metaeval providers check` command
- [ ] Add provider-specific configuration
- [ ] Add async execution support for API calls
- [ ] Add job status tracking for HPC

**Deliverable**: `metaeval eval --model openai/gpt-4o --backend api`

### Phase 4: OSQ + Judging Integration (Week 4-5)

**Goal**: Unified OSQ evaluation with automatic judging

- [ ] Integrate judge pipeline with eval command
- [ ] Add `--judge` flag to eval command
- [ ] Stream judging progress
- [ ] Store judged results with eval run
- [ ] Add consensus judging option
- [ ] Add judge calibration hooks

**Deliverable**: `metaeval eval --format osq --judge ollama/llama3.1:70b`

### Phase 5: Polish & Documentation (Week 5-6)

- [ ] Add comprehensive error handling
- [ ] Add retry logic with exponential backoff
- [ ] Add cost estimation for API runs
- [ ] Add progress streaming for long runs
- [ ] Write user documentation
- [ ] Add integration tests
- [ ] Update existing notebooks

---

## 6. Configuration Updates

### 6.1 New Config Section

```python
# metaeval/core/config.py

@dataclass
class HarnessConfig:
    """Configuration for lm-eval harness integration."""

    # Task generation
    default_task_dir: Path = Path("tasks")
    default_output_dir: Path = Path("output")

    # Execution
    default_backend: str = "local"
    default_batch_size: str = "auto"
    lmeval_path: str = "lm_eval"  # Path to lm-eval executable

    # Results storage
    results_db_path: Path = Path(".metaeval/runs.db")
    keep_raw_outputs: bool = True

    # Timeouts
    eval_timeout_seconds: int = 7200  # 2 hours
    sample_timeout_seconds: int = 60


# Add to MetaevalConfig
@dataclass
class MetaevalConfig:
    ...
    harness: HarnessConfig = field(default_factory=HarnessConfig)
```

### 6.2 Model Registry

```yaml
# ~/.metaeval/models.yaml

providers:
  ollama:
    base_url: "http://localhost:11434/v1"
    lmeval_model_type: "local-chat-completions"

  openai:
    api_key_env: "OPENAI_API_KEY"
    lmeval_model_type: "openai-chat-completions"

  anthropic:
    api_key_env: "ANTHROPIC_API_KEY"
    lmeval_model_type: "anthropic-chat-completions"

models:
  llama3.1:8b:
    provider: ollama
    display_name: "Llama 3.1 8B"

  gpt-4o:
    provider: openai
    display_name: "GPT-4o"
```

---

## 7. Backwards Compatibility

### 7.1 Preserved Interfaces

- All existing `metaeval` CLI commands unchanged
- All existing dataclasses preserved
- Parsers continue to work standalone
- Direct lm-eval usage still possible

### 7.2 Deprecation Path

```python
# benchmark/tasks.py - add deprecation warning
import warnings

def generate_mcq_task(...):
    warnings.warn(
        "generate_mcq_task() is deprecated. Use metaeval.harness.tasks instead.",
        DeprecationWarning
    )
    from metaeval.harness.tasks import generate_mcq_task as new_func
    return new_func(...)
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# tests/harness/test_results.py
def test_parse_lmeval_results():
    results = LMEvalResultsFile.from_json(FIXTURES / "lmeval_output.json")
    assert results.get_accuracy("sysenebench_mcq") == 0.75

def test_sample_to_mcq_result():
    sample = LMEvalSample.from_json({"doc": {...}, "resps": [...], ...})
    mcq = sample.to_mcq_result(model="llama3.1")
    assert isinstance(mcq, MCQResult)
```

### 8.2 Integration Tests

```python
# tests/harness/test_runner.py
@pytest.mark.integration
def test_full_eval_run():
    config = EvalConfig(model="ollama/llama3.1:8b", benchmark="test_task", format="mcq")
    runner = LMEvalRunner(config)
    run = runner.run()
    assert run.status == "completed"
    assert run.results.accuracy is not None
```

---

## 9. Open Questions

1. **Result persistence**: SQLite DB vs. filesystem (JSON/JSONL)?
2. **Run ID format**: UUID vs. human-readable (`llama3.1-sysenebench-20240115`)?
3. **Streaming**: Real-time progress vs. polling?
4. **HPC integration**: Job submission vs. result monitoring?
5. **Model aliases**: Support `gpt4` → `openai/gpt-4o` mappings?

---

## 10. Success Metrics

- [ ] `metaeval eval` can replicate all current SBATCH workflows
- [ ] Zero manual JSON parsing required for standard workflows
- [ ] Analysis commands accept run IDs directly
- [ ] < 5% overhead vs. direct lm-eval invocation
- [ ] All existing tests pass
- [ ] New integration tests cover critical paths

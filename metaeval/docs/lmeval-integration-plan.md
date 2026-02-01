# lm-eval Integration Plan (Revised)

> **Goal**: Parse lm-eval outputs into metaeval types so `metaeval analyze` commands work seamlessly with lm-eval results. No wrapper CLI - users run lm-eval directly.

## Design Philosophy

1. **Don't wrap lm-eval** - Users run `lm_eval` directly, refer them to lm-eval docs
2. **Parse lm-eval outputs** - New `metaeval/harness/` module parses `results.json` and `samples.jsonl`
3. **Unified types** - Convert lm-eval output → metaeval `MCQResult`/`OSQResult` for analysis
4. **Support existing output structure** - Parse the output format from `src/phase4_inference/output/`

---

## 1. lm-eval Output Format (What We Parse)

### Directory Structure
```
output/
├── sysengbench-a/                    # Task name (MCQ variant A)
│   └── llama3.3__70b/                # Model name (sanitized)
│       ├── results_2025-11-15T01-12-13.json
│       └── samples_sysengbench-a_2025-11-15T01-12-13.jsonl
├── sysengbench-osq/                  # OSQ task
│   └── llama3.3__70b/
│       ├── results_2025-11-14T23-24-28.json
│       └── samples_sysengbench-osq_2025-11-14T23-24-28.jsonl
```

### results.json (Aggregate Metrics)
```json
{
  "results": {
    "sysengbench-a": {
      "exact_match,strict-match": 0.9248,
      "exact_match_stderr,strict-match": 0.0078
    }
  },
  "model_name": "llama3.3:70b",
  "model_name_sanitized": "llama3.3__70b",
  "n-samples": {"sysengbench-a": {"original": 1144, "effective": 1144}},
  "total_evaluation_time_seconds": "265.55"
}
```

### samples.jsonl - MCQ Format
```json
{
  "doc_id": 0,
  "doc": {
    "Question ID": 1,
    "question": "What best describes...",
    "choiceA": "...", "choiceB": "...", "choiceC": "...", "choiceD": "...",
    "answer": "A",
    "INCOSE Handbook Category": "...",
    "Tags": "..."
  },
  "target": "A",
  "filtered_resps": ["A"],
  "exact_match": 1.0
}
```

### samples.jsonl - OSQ Format
```json
{
  "doc_id": 0,
  "doc": {
    "Question ID": 1,
    "osq_prompt": "Define \"uncertainty\" in systems engineering...",
    "expected_answer": "A condition in which...",
    "full_credit_criteria": "3 points: ...",
    "partial_credit_criteria": "2 points: ...",
    "no_credit_criteria": "0 points: ...",
    "blooms_level": "Remember"
  },
  "target": "A condition in which...",
  "resps": [["In systems engineering, uncertainty refers to..."]],
  "filtered_resps": ["In systems engineering, uncertainty refers to..."]
}
```

---

## 2. New Module: `metaeval/harness/`

```
metaeval/harness/
├── __init__.py
├── parser.py         # LMEvalParser - main entry point
├── results.py        # LMEvalResults dataclass (from results.json)
├── samples.py        # LMEvalSample dataclass (from samples.jsonl)
└── discovery.py      # Find lm-eval output directories
```

### 2.1 Core Parser

```python
# metaeval/harness/parser.py

from pathlib import Path
from metaeval.harness.results import LMEvalResults
from metaeval.harness.samples import LMEvalSample
from metaeval.parsers.mcq import MCQResult
from metaeval.parsers.osq import OSQResult

class LMEvalParser:
    """Parse lm-eval output directories into metaeval types."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def parse(self) -> "ParsedRun":
        """Parse results.json and samples.jsonl from output directory."""
        results_file = self._find_results_json()
        samples_file = self._find_samples_jsonl()

        results = LMEvalResults.from_json(results_file)
        samples = [LMEvalSample.from_json(line) for line in self._read_jsonl(samples_file)]

        return ParsedRun(
            results=results,
            samples=samples,
            task=results.task_name,
            model=results.model_name,
            format=self._detect_format(samples),
        )

    def to_mcq_results(self) -> list[MCQResult]:
        """Convert to metaeval MCQResult objects for bias analysis."""
        run = self.parse()
        return [s.to_mcq_result(run.model, run.task) for s in run.samples]

    def to_osq_results(self) -> list[OSQResult]:
        """Convert to metaeval OSQResult objects for judging."""
        run = self.parse()
        return [s.to_osq_result(run.model) for s in run.samples]

    def _detect_format(self, samples: list[LMEvalSample]) -> str:
        """Detect MCQ vs OSQ from sample structure."""
        if samples and "osq_prompt" in samples[0].doc:
            return "osq"
        return "mcq"
```

### 2.2 Results Dataclass

```python
# metaeval/harness/results.py

@dataclass
class LMEvalResults:
    """Parsed lm-eval results.json."""
    task_name: str
    model_name: str
    model_name_sanitized: str

    # Metrics
    accuracy: float | None = None
    accuracy_stderr: float | None = None

    # Metadata
    n_samples: int = 0
    eval_time_seconds: float = 0.0
    lm_eval_version: str = ""
    date: datetime | None = None

    # Raw data for extensibility
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, path: Path) -> "LMEvalResults":
        data = json.loads(path.read_text())

        # Extract first task (usually only one)
        task_name = list(data["results"].keys())[0]
        task_results = data["results"][task_name]

        # Find accuracy metric (varies by filter name)
        accuracy = None
        accuracy_stderr = None
        for key, value in task_results.items():
            if key.startswith("exact_match") and "stderr" not in key:
                accuracy = value
            elif "stderr" in key:
                accuracy_stderr = value

        return cls(
            task_name=task_name,
            model_name=data.get("model_name", ""),
            model_name_sanitized=data.get("model_name_sanitized", ""),
            accuracy=accuracy,
            accuracy_stderr=accuracy_stderr,
            n_samples=data.get("n-samples", {}).get(task_name, {}).get("effective", 0),
            eval_time_seconds=float(data.get("total_evaluation_time_seconds", 0)),
            lm_eval_version=data.get("lm_eval_version", ""),
            raw=data,
        )
```

### 2.3 Sample Dataclass

```python
# metaeval/harness/samples.py

@dataclass
class LMEvalSample:
    """Single sample from lm-eval samples.jsonl."""
    doc_id: int
    doc: dict
    target: str
    resps: list
    filtered_resps: list
    exact_match: float | None = None

    @classmethod
    def from_json(cls, data: dict) -> "LMEvalSample":
        return cls(
            doc_id=data["doc_id"],
            doc=data["doc"],
            target=data["target"],
            resps=data.get("resps", []),
            filtered_resps=data.get("filtered_resps", []),
            exact_match=data.get("exact_match"),
        )

    def to_mcq_result(self, model: str, variant: str = "") -> MCQResult:
        """Convert to metaeval MCQResult."""
        return MCQResult(
            question_id=self.doc.get("Question ID", self.doc_id),
            question=self.doc.get("question", ""),
            choices={
                "A": self.doc.get("choiceA", ""),
                "B": self.doc.get("choiceB", ""),
                "C": self.doc.get("choiceC", ""),
                "D": self.doc.get("choiceD", ""),
            },
            correct_answer=self.doc.get("answer", self.target),
            model_answer=self.filtered_resps[0] if self.filtered_resps else "",
            is_correct=self.exact_match == 1.0,
            model=model,
            benchmark_variant=variant,
            raw_response=self.resps[0][0] if self.resps else "",
        )

    def to_osq_result(self, model: str) -> OSQResult:
        """Convert to metaeval OSQResult."""
        return OSQResult(
            question_id=self.doc.get("Question ID", self.doc_id),
            question=self.doc.get("osq_prompt", ""),
            expected_answer=self.doc.get("expected_answer", self.target),
            model_response=self.filtered_resps[0] if self.filtered_resps else "",
            model=model,
            rubric={
                "full_credit": self.doc.get("full_credit_criteria", ""),
                "partial_credit": self.doc.get("partial_credit_criteria", ""),
                "no_credit": self.doc.get("no_credit_criteria", ""),
            },
            raw_response=self.resps[0][0] if self.resps else "",
        )
```

### 2.4 Discovery Helper

```python
# metaeval/harness/discovery.py

def find_runs(base_dir: Path, task_filter: str | None = None) -> list[Path]:
    """Find all lm-eval output directories."""
    runs = []
    for task_dir in base_dir.iterdir():
        if task_filter and task_filter not in task_dir.name:
            continue
        for model_dir in task_dir.iterdir():
            if (model_dir / "results.json").exists() or \
               list(model_dir.glob("results_*.json")):
                runs.append(model_dir)
    return sorted(runs)

def find_latest_results(model_dir: Path) -> Path:
    """Find most recent results.json in a model directory."""
    results_files = list(model_dir.glob("results_*.json"))
    if results_files:
        return max(results_files, key=lambda p: p.stat().st_mtime)
    return model_dir / "results.json"
```

---

## 3. CLI Integration

### 3.1 Updated `metaeval analyze` Commands

```python
# metaeval/cli/main.py

@app.command()
def analyze_bias(
    output_dir: Path = typer.Argument(..., help="lm-eval output directory"),
    task: str = typer.Option(None, help="Filter by task name"),
    model: str = typer.Option(None, help="Filter by model name"),
):
    """Analyze position bias from lm-eval MCQ results."""
    from metaeval.harness.parser import LMEvalParser
    from metaeval.harness.discovery import find_runs

    runs = find_runs(output_dir, task_filter=task)
    if model:
        runs = [r for r in runs if model in r.name]

    for run_dir in runs:
        parser = LMEvalParser(run_dir)
        mcq_results = parser.to_mcq_results()
        # Feed to existing bias analyzer
        ...

@app.command()
def analyze_judge(
    output_dir: Path = typer.Argument(..., help="lm-eval output directory (OSQ)"),
    judge_model: str = typer.Option("ollama/llama3.1:70b", help="Judge model"),
):
    """Judge OSQ responses from lm-eval output."""
    from metaeval.harness.parser import LMEvalParser

    parser = LMEvalParser(output_dir)
    osq_results = parser.to_osq_results()

    # Feed to existing judge pipeline
    for result in osq_results:
        judgment = judge.evaluate(
            question=result.question,
            expected=result.expected_answer,
            response=result.model_response,
            rubric=result.rubric,
        )
        ...
```

### 3.2 Help Text for lm-eval

```python
@app.command()
def eval():
    """
    Run model evaluation.

    metaeval does not wrap lm-eval. Run lm-eval directly:

        lm_eval \\
          --model local-chat-completions \\
          --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \\
          --tasks ./tasks/sysengbench.yaml \\
          --output_path ./output \\
          --log_samples

    See: https://github.com/EleutherAI/lm-evaluation-harness

    Then analyze results with:
        metaeval analyze bias ./output/sysengbench/llama3.1__8b/
        metaeval analyze judge ./output/sysengbench-osq/llama3.1__8b/
    """
    console.print("[yellow]See lm-eval documentation for running evaluations.[/yellow]")
    console.print("https://github.com/EleutherAI/lm-evaluation-harness")
```

---

## 4. Updated Type Mappings

### lm-eval → metaeval

| lm-eval Field | metaeval Type | Field |
|---------------|---------------|-------|
| `doc.Question ID` | `MCQResult` | `question_id` |
| `doc.question` | `MCQResult` | `question` |
| `doc.choiceA/B/C/D` | `MCQResult` | `choices` |
| `doc.answer` | `MCQResult` | `correct_answer` |
| `filtered_resps[0]` | `MCQResult` | `model_answer` |
| `exact_match` | `MCQResult` | `is_correct` |
| `doc.osq_prompt` | `OSQResult` | `question` |
| `doc.expected_answer` | `OSQResult` | `expected_answer` |
| `resps[0][0]` | `OSQResult` | `model_response` |
| `doc.full_credit_criteria` | `OSQResult` | `rubric["full_credit"]` |

### Variant Detection

Task name → position variant:
- `sysengbench` or `sysengbench-a` → Position A (original)
- `sysengbench-b` → Position B
- `sysengbench-c` → Position C
- `sysengbench-d` → Position D
- `sysengbench-osq` → OSQ format

---

## 5. Implementation Plan

### Phase 1: Core Parsing (Priority)

- [ ] Create `metaeval/harness/` module
- [ ] Implement `LMEvalResults.from_json()`
- [ ] Implement `LMEvalSample.from_json()`
- [ ] Implement `LMEvalSample.to_mcq_result()`
- [ ] Implement `LMEvalSample.to_osq_result()`
- [ ] Implement `LMEvalParser` with directory handling
- [ ] Add unit tests with fixture data from `src/phase4_inference/output/`

### Phase 2: CLI Integration

- [ ] Update `metaeval analyze bias` to accept lm-eval output dir
- [ ] Update `metaeval analyze judge` to accept lm-eval output dir
- [ ] Add `find_runs()` discovery helper
- [ ] Add `metaeval eval` help command pointing to lm-eval

### Phase 3: Batch Processing

- [ ] Support multiple model directories in one command
- [ ] Support `--all-models` flag to process entire task directory
- [ ] Add CSV/JSON export of parsed results
- [ ] Add comparison tables across models

---

## 6. Example Workflows

### Bias Analysis (MCQ)

```bash
# User runs lm-eval (their responsibility)
lm_eval --model local-chat-completions \
  --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \
  --tasks ./sysengbench-a.yaml,./sysengbench-b.yaml,./sysengbench-c.yaml,./sysengbench-d.yaml \
  --output_path ./output \
  --log_samples

# metaeval parses and analyzes
metaeval analyze bias ./output/ --task sysengbench
```

### OSQ Judging

```bash
# User runs lm-eval
lm_eval --model local-chat-completions \
  --model_args model=llama3.1:8b,base_url=http://localhost:11434/v1/chat/completions \
  --tasks ./sysengbench-osq.yaml \
  --output_path ./output \
  --log_samples

# metaeval parses and judges
metaeval analyze judge ./output/sysengbench-osq/llama3.1__8b/ \
  --judge ollama/llama3.1:70b
```

---

## 7. Benefits of This Approach

1. **No maintenance burden** - Don't maintain lm-eval wrapper or duplicate docs
2. **Always compatible** - Parse lm-eval's output format, not wrap its CLI
3. **Clean separation** - lm-eval does inference, metaeval does analysis
4. **Leverages existing code** - Reuses `MCQResult`, `OSQResult`, existing analyzers
5. **Works with existing outputs** - Parses the 100+ runs already in `src/phase4_inference/output/`

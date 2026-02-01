"""Tests for lm-eval harness parser."""

import json
import tempfile
from pathlib import Path

import pytest

from metaeval.harness.parser import LMEvalParser, ParsedRun
from metaeval.harness.results import LMEvalResults
from metaeval.harness.samples import LMEvalSample
from metaeval.harness.discovery import find_runs, list_models, list_tasks
from metaeval.parsers.mcq import MCQResult
from metaeval.parsers.osq import OSQResult


# Sample MCQ data from actual lm-eval output
SAMPLE_MCQ_RESULTS = {
    "results": {
        "sysengbench-a": {
            "exact_match,strict-match": 0.9248,
            "exact_match_stderr,strict-match": 0.0078
        }
    },
    "model_name": "llama3.3:70b",
    "model_name_sanitized": "llama3.3__70b",
    "n-samples": {"sysengbench-a": {"original": 1144, "effective": 1144}},
    "total_evaluation_time_seconds": "265.55",
    "lm_eval_version": "0.4.9.1",
    "date": 1731655933.0,
}

SAMPLE_MCQ_SAMPLE = {
    "doc_id": 0,
    "doc": {
        "Question ID": 1,
        "Tags": "Introduction to risk",
        "INCOSE Handbook Category": "INCOSEHandbook/Systems Engineering Overview",
        "question": "What best describes the concept of uncertainty in systems engineering?",
        "choiceA": "The condition where the outcomes are not predictable.",
        "choiceB": "A method for analyzing costs and benefits.",
        "choiceC": "The act of integrating different system components.",
        "choiceD": "The process of systematically improving a system.",
        "answer": "A",
        "label": 0,
    },
    "target": "A",
    "resps": [["A"]],
    "filtered_resps": ["A"],
    "exact_match": 1.0,
    "doc_hash": "abc123",
    "prompt_hash": "def456",
}

# Sample OSQ data
SAMPLE_OSQ_RESULTS = {
    "results": {
        "sysengbench-osq": {
            "exact_match,none": 0.027,
            "exact_match_stderr,none": 0.0056
        }
    },
    "model_name": "llama3.3:70b",
    "model_name_sanitized": "llama3.3__70b",
    "n-samples": {"sysengbench-osq": {"original": 845, "effective": 845}},
    "total_evaluation_time_seconds": "1329.49",
    "lm_eval_version": "0.4.9.1",
}

SAMPLE_OSQ_SAMPLE = {
    "doc_id": 0,
    "doc": {
        "Question ID": 1,
        "osq_prompt": "Define 'uncertainty' in systems engineering. Answer in 1-2 sentences.",
        "expected_answer": "A condition in which system outcomes are not predictable.",
        "full_credit_criteria": "3 points: States unpredictability and cause.",
        "partial_credit_criteria": "2 points: Mentions unpredictability only.",
        "no_credit_criteria": "0 points: Wrong concept.",
        "blooms_level": "Remember",
    },
    "target": "A condition in which system outcomes are not predictable.",
    "resps": [["Uncertainty refers to the lack of complete knowledge about a system's behavior."]],
    "filtered_resps": ["Uncertainty refers to the lack of complete knowledge about a system's behavior."],
    "exact_match": 0.0,
}


@pytest.fixture
def mcq_output_dir(tmp_path):
    """Create a temporary MCQ output directory."""
    output_dir = tmp_path / "sysengbench-a" / "llama3.3__70b"
    output_dir.mkdir(parents=True)

    # Write results.json
    results_file = output_dir / "results_2025-01-15.json"
    results_file.write_text(json.dumps(SAMPLE_MCQ_RESULTS))

    # Write samples.jsonl
    samples_file = output_dir / "samples_sysengbench-a_2025-01-15.jsonl"
    samples_file.write_text(json.dumps(SAMPLE_MCQ_SAMPLE) + "\n")

    return output_dir


@pytest.fixture
def osq_output_dir(tmp_path):
    """Create a temporary OSQ output directory."""
    output_dir = tmp_path / "sysengbench-osq" / "llama3.3__70b"
    output_dir.mkdir(parents=True)

    # Write results.json
    results_file = output_dir / "results_2025-01-15.json"
    results_file.write_text(json.dumps(SAMPLE_OSQ_RESULTS))

    # Write samples.jsonl
    samples_file = output_dir / "samples_sysengbench-osq_2025-01-15.jsonl"
    samples_file.write_text(json.dumps(SAMPLE_OSQ_SAMPLE) + "\n")

    return output_dir


@pytest.fixture
def multi_run_dir(tmp_path):
    """Create multiple output directories for testing discovery."""
    # MCQ variants
    for variant in ["a", "b", "c", "d"]:
        for model in ["llama3.3__70b", "gpt-4o"]:
            output_dir = tmp_path / f"sysengbench-{variant}" / model
            output_dir.mkdir(parents=True)

            results = SAMPLE_MCQ_RESULTS.copy()
            results["results"] = {f"sysengbench-{variant}": SAMPLE_MCQ_RESULTS["results"]["sysengbench-a"]}
            results["model_name_sanitized"] = model

            (output_dir / "results_2025-01-15.json").write_text(json.dumps(results))
            (output_dir / "samples_sysengbench-a_2025-01-15.jsonl").write_text(
                json.dumps(SAMPLE_MCQ_SAMPLE) + "\n"
            )

    # OSQ
    for model in ["llama3.3__70b", "gpt-4o"]:
        output_dir = tmp_path / "sysengbench-osq" / model
        output_dir.mkdir(parents=True)

        results = SAMPLE_OSQ_RESULTS.copy()
        results["model_name_sanitized"] = model

        (output_dir / "results_2025-01-15.json").write_text(json.dumps(results))
        (output_dir / "samples_sysengbench-osq_2025-01-15.jsonl").write_text(
            json.dumps(SAMPLE_OSQ_SAMPLE) + "\n"
        )

    return tmp_path


class TestLMEvalResults:
    """Tests for LMEvalResults dataclass."""

    def test_from_json(self, mcq_output_dir):
        """Test parsing results.json."""
        results_file = list(mcq_output_dir.glob("results_*.json"))[0]
        results = LMEvalResults.from_json(results_file)

        assert results.task_name == "sysengbench-a"
        assert results.model_name == "llama3.3:70b"
        assert results.model_name_sanitized == "llama3.3__70b"
        assert results.accuracy == pytest.approx(0.9248)
        assert results.accuracy_stderr == pytest.approx(0.0078)
        assert results.n_samples == 1144
        assert results.eval_time_seconds == pytest.approx(265.55)
        assert results.lm_eval_version == "0.4.9.1"

    def test_is_mcq(self, mcq_output_dir):
        """Test MCQ detection."""
        results_file = list(mcq_output_dir.glob("results_*.json"))[0]
        results = LMEvalResults.from_json(results_file)
        assert results.is_mcq is True
        assert results.is_osq is False

    def test_is_osq(self, osq_output_dir):
        """Test OSQ detection."""
        results_file = list(osq_output_dir.glob("results_*.json"))[0]
        results = LMEvalResults.from_json(results_file)
        assert results.is_osq is True
        assert results.is_mcq is False

    def test_variant_detection(self, mcq_output_dir):
        """Test position variant detection."""
        results_file = list(mcq_output_dir.glob("results_*.json"))[0]
        results = LMEvalResults.from_json(results_file)
        assert results.variant == "A"


class TestLMEvalSample:
    """Tests for LMEvalSample dataclass."""

    def test_from_json_mcq(self):
        """Test parsing MCQ sample."""
        sample = LMEvalSample.from_json(SAMPLE_MCQ_SAMPLE)

        assert sample.doc_id == 0
        assert sample.question_id == 1
        assert sample.target == "A"
        assert sample.model_answer == "A"
        assert sample.is_correct is True
        assert sample.is_mcq is True
        assert sample.is_osq is False

    def test_from_json_osq(self):
        """Test parsing OSQ sample."""
        sample = LMEvalSample.from_json(SAMPLE_OSQ_SAMPLE)

        assert sample.doc_id == 0
        assert sample.question_id == 1
        assert sample.is_osq is True
        assert sample.is_mcq is False
        assert "uncertainty" in sample.model_response.lower()

    def test_to_mcq_result(self):
        """Test conversion to MCQResult."""
        sample = LMEvalSample.from_json(SAMPLE_MCQ_SAMPLE)
        result = sample.to_mcq_result(model="llama3.3:70b", variant="A")

        assert isinstance(result, MCQResult)
        assert result.question_id == 1
        assert result.model == "llama3.3:70b"
        assert result.benchmark_variant == "A"
        assert result.correct_answer == "A"
        assert result.model_answer == "A"
        assert result.is_correct is True
        assert "A" in result.choices

    def test_to_osq_result(self):
        """Test conversion to OSQResult."""
        sample = LMEvalSample.from_json(SAMPLE_OSQ_SAMPLE)
        result = sample.to_osq_result(model="llama3.3:70b")

        assert isinstance(result, OSQResult)
        assert result.question_id == 1
        assert result.model == "llama3.3:70b"
        assert "uncertainty" in result.question.lower()
        assert result.rubric is not None
        assert "full_credit" in result.rubric


class TestLMEvalParser:
    """Tests for LMEvalParser."""

    def test_parse_mcq(self, mcq_output_dir):
        """Test parsing MCQ output directory."""
        parser = LMEvalParser(mcq_output_dir)
        run = parser.parse()

        assert isinstance(run, ParsedRun)
        assert run.task == "sysengbench-a"
        assert run.model == "llama3.3:70b"
        assert run.format == "mcq"
        assert run.accuracy == pytest.approx(0.9248)
        assert len(run.samples) == 1

    def test_parse_osq(self, osq_output_dir):
        """Test parsing OSQ output directory."""
        parser = LMEvalParser(osq_output_dir)
        run = parser.parse()

        assert isinstance(run, ParsedRun)
        assert run.task == "sysengbench-osq"
        assert run.format == "osq"
        assert len(run.samples) == 1

    def test_to_mcq_results(self, mcq_output_dir):
        """Test converting to MCQResult list."""
        parser = LMEvalParser(mcq_output_dir)
        results = parser.to_mcq_results()

        assert len(results) == 1
        assert all(isinstance(r, MCQResult) for r in results)
        assert results[0].question_id == 1
        assert results[0].is_correct is True

    def test_to_osq_results(self, osq_output_dir):
        """Test converting to OSQResult list."""
        parser = LMEvalParser(osq_output_dir)
        results = parser.to_osq_results()

        assert len(results) == 1
        assert all(isinstance(r, OSQResult) for r in results)
        assert results[0].question_id == 1

    def test_parse_all(self, multi_run_dir):
        """Test parsing all output directories."""
        runs = list(LMEvalParser.parse_all(multi_run_dir))

        # 4 variants * 2 models + 1 osq * 2 models = 10 runs
        assert len(runs) == 10

    def test_parse_all_with_filter(self, multi_run_dir):
        """Test parsing with task filter."""
        runs = list(LMEvalParser.parse_all(multi_run_dir, task_filter="osq"))
        assert len(runs) == 2
        assert all(r.format == "osq" for r in runs)

    def test_collect_mcq_by_variant(self, multi_run_dir):
        """Test collecting MCQ results by variant."""
        results = LMEvalParser.collect_mcq_by_variant(multi_run_dir)

        assert len(results) == 2  # 2 models
        for model, variants in results.items():
            assert len(variants) == 4  # A, B, C, D
            for variant, mcq_results in variants.items():
                assert all(isinstance(r, MCQResult) for r in mcq_results)

    def test_collect_osq(self, multi_run_dir):
        """Test collecting OSQ results."""
        results = LMEvalParser.collect_osq(multi_run_dir)

        assert len(results) == 2  # 2 models
        for model, osq_results in results.items():
            assert all(isinstance(r, OSQResult) for r in osq_results)


class TestDiscovery:
    """Tests for discovery helpers."""

    def test_find_runs(self, multi_run_dir):
        """Test finding all run directories."""
        runs = find_runs(multi_run_dir)
        assert len(runs) == 10

    def test_find_runs_with_task_filter(self, multi_run_dir):
        """Test finding runs with task filter."""
        runs = find_runs(multi_run_dir, task_filter="osq")
        assert len(runs) == 2

    def test_find_runs_with_model_filter(self, multi_run_dir):
        """Test finding runs with model filter."""
        runs = find_runs(multi_run_dir, model_filter="llama")
        assert len(runs) == 5  # 4 MCQ variants + 1 OSQ

    def test_list_models(self, multi_run_dir):
        """Test listing all models."""
        models = list_models(multi_run_dir)
        assert len(models) == 2
        assert "llama3.3__70b" in models
        assert "gpt-4o" in models

    def test_list_tasks(self, multi_run_dir):
        """Test listing all tasks."""
        tasks = list_tasks(multi_run_dir)
        assert len(tasks) == 5  # sysengbench-a, b, c, d, osq
        assert "sysengbench-osq" in tasks


class TestIntegrationWithRealData:
    """Integration tests using real lm-eval output (if available)."""

    @pytest.fixture
    def real_output_dir(self):
        """Get real output directory if it exists."""
        real_dir = Path("/home/user/dissertation/src/phase4_inference/output")
        if real_dir.exists():
            return real_dir
        pytest.skip("Real output directory not available")

    def test_parse_real_mcq(self, real_output_dir):
        """Test parsing real MCQ output."""
        mcq_dirs = find_runs(real_output_dir, task_filter="sysengbench-a")
        if not mcq_dirs:
            pytest.skip("No MCQ output available")

        parser = LMEvalParser(mcq_dirs[0])
        results = parser.to_mcq_results()

        assert len(results) > 0
        assert all(isinstance(r, MCQResult) for r in results)

    def test_parse_real_osq(self, real_output_dir):
        """Test parsing real OSQ output."""
        osq_dirs = find_runs(real_output_dir, task_filter="osq")
        if not osq_dirs:
            pytest.skip("No OSQ output available")

        parser = LMEvalParser(osq_dirs[0])
        results = parser.to_osq_results()

        assert len(results) > 0
        assert all(isinstance(r, OSQResult) for r in results)
        # Check rubric is populated
        assert results[0].rubric is not None

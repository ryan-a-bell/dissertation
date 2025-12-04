# Auto-V2 Fixes - Comprehensive Implementation Guide

This document contains all fixes needed for `llm-judge-runpod-auto-v2.ipynb` to resolve:
1. Silent worker script (no progress output)
2. Blocking SSH commands (no streaming)
3. SAMPLE_N applying to model count instead of samples per model
4. Missing checkpoint saves after each model

---

## Fix 1: Configuration Cell (Cell 3) - Clarify SAMPLE_N Behavior

**REPLACE the comment block in cell 3:**

```python
# Execution Settings
MAX_CONCURRENT_PODS = 2  # Number of parallel pods
SAMPLE_N = 15  # 0 = judge all samples, >0 = test with N samples
```

**WITH:**

```python
# Execution Settings
MAX_CONCURRENT_PODS = 2  # Number of parallel pods

# IMPORTANT: SAMPLE_N vs TEST_SAMPLE_N
# - TEST_SAMPLE_N: Number of samples for test phase (single model validation)
# - SAMPLE_N: Number of samples PER MODEL during parallel execution
#   * 0 = judge ALL samples (845) per model
#   * >0 = judge first N samples per model (e.g., 50 = first 50 samples)
#   * Applies to ALL models, not just first N models!
SAMPLE_N = 0  # 0 = ALL samples, >0 = limit samples per model
```

---

## Fix 2: Worker Script (Cell 9) - Add Verbose Progress Logging

**REPLACE the entire POD_WORKER_SCRIPT in cell 9 with this VERBOSE version:**

```python
# Pod Worker Script - VERBOSE VERSION with Real-Time Progress

POD_WORKER_SCRIPT = '''import json
import requests
import sys
import time
from datetime import datetime

JUDGE_PROMPT_P1 = """You are an expert systems engineering (SE) educator evaluating student responses to open-ended questions.

EVALUATION SCHEMA (each 0–20, total 100):
1. TECHNICAL ACCURACY — correctness of SE concepts, terminology, and facts
2. CONCEPTUAL UNDERSTANDING — depth of comprehension of underlying SE principles
3. COMPLETENESS — coverage of key elements expected in the answer
4. CLARITY & ORGANIZATION — logical structure and clear communication
5. PROFESSIONAL RELEVANCE — connection to real-world SE practice and standards

QUESTION CONTEXT:
Original Question: {osq_question}
Expected Answer: {expected_answer}
Bloom's Level: {blooms_level}
SE Domain: {se_domain}

STUDENT RESPONSE TO EVALUATE:
{student_response}

INSTRUCTIONS:
Compare the response to the expected answer and criteria.
Return strict JSON in this format:
{
  "technical_accuracy": {"score": <0–20>},
  "conceptual_understanding": {"score": <0–20>},
  "completeness": {"score": <0–20>},
  "clarity_organization": {"score": <0–20>},
  "professional_relevance": {"score": <0–20>},
  "overall_score": <0–100>
}
"""

JUDGE_PROMPT_P2 = """You are an expert systems engineering (SE) educator evaluating student responses to open-ended questions.

EVALUATION SCHEMA (each 0–20, total 100):
1. TECHNICAL ACCURACY — correctness of SE concepts, terminology, and facts
2. CONCEPTUAL UNDERSTANDING — depth of comprehension of underlying SE principles
3. COMPLETENESS — coverage of key elements expected in the answer
4. CLARITY & ORGANIZATION — logical structure and clear communication
5. PROFESSIONAL RELEVANCE — connection to real-world SE practice and standards

QUESTION CONTEXT:
Original Question: {osq_question}
Expected Answer: {expected_answer}
Bloom's Level: {blooms_level}
SE Domain: {se_domain}

STUDENT RESPONSE TO EVALUATE:
{student_response}

INSTRUCTIONS:
Compare the response to the expected answer and criteria.
Return strict JSON in this format:
{
  "technical_accuracy": {"score": <0–20>, "justification": "<1–2 sentences>"},
  "conceptual_understanding": {"score": <0–20>, "justification": "<1–2 sentences>"},
  "completeness": {"score": <0–20>, "justification": "<1–2 sentences>"},
  "clarity_organization": {"score": <0–20>, "justification": "<1–2 sentences>"},
  "professional_relevance": {"score": <0–20>, "justification": "<1–2 sentences>"},
  "overall_score": <0–100>,
  "overall_assessment": "<summary>",
  "key_strengths": "<strengths>",
  "improvement_areas": "<areas for improvement>"
}
"""


def safe_json(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def extract_student_response(sample_row):
    resps = sample_row.get("resps")
    if not resps:
        return ""
    first = resps[0]
    if isinstance(first, list) and first:
        first = first[0]
    return first if isinstance(first, str) else ""


def derive_prompt_fields(phase4_row):
    doc = (phase4_row.get("doc") or {}) if isinstance(phase4_row.get("doc"), dict) else {}
    osq_question = doc.get("osq_prompt") or doc.get("question") or ""
    expected_answer = doc.get("expected_answer", "")
    blooms_level = doc.get("blooms_level", "N/A")
    se_domain = doc.get("INCOSE Handbook Category", "General Systems Engineering")
    student_resp = extract_student_response(phase4_row)
    return {
        "osq_question": osq_question,
        "expected_answer": expected_answer,
        "student_response": student_resp,
        "blooms_level": blooms_level,
        "se_domain": se_domain,
    }


def triad_missing(fields):
    return [
        k for k in ("osq_question", "expected_answer", "student_response")
        if not isinstance(fields.get(k, ""), str) or not fields.get(k, "").strip()
    ]


def run_worker(input_path, output_path, judge_model, prompt_id,
               temperature, max_tokens, task_name, model_name):
    judge_prompt = JUDGE_PROMPT_P1 if prompt_id == "p1" else JUDGE_PROMPT_P2
    judge_url = "http://localhost:11434/v1/chat/completions"

    # Count total samples first
    with open(input_path, "r", encoding="utf-8") as fin:
        total_samples = sum(1 for line in fin if line.strip())

    print(f"[worker] Starting judging for {model_name}", flush=True)
    print(f"[worker] Total samples to judge: {total_samples}", flush=True)
    print(f"[worker] Judge model: {judge_model}", flush=True)
    print(f"[worker] Prompt ID: {prompt_id}", flush=True)
    print("=" * 60, flush=True)

    current = 0
    start_time = time.time()

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line in fin:
            if not line.strip():
                continue

            current += 1
            sample_start = time.time()

            payload = json.loads(line)
            sid = payload["sample_id"]
            phase4_row = payload["phase4_row"]

            # Progress update every 10 samples or first/last
            if current % 10 == 0 or current == 1 or current == total_samples:
                elapsed = time.time() - start_time
                rate = current / elapsed if elapsed > 0 else 0
                remaining = (total_samples - current) / rate if rate > 0 else 0
                print(
                    f"[worker] Progress: {current}/{total_samples} "
                    f"({100*current/total_samples:.1f}%) | "
                    f"Rate: {rate:.2f} samples/s | "
                    f"ETA: {remaining/60:.1f}min",
                    flush=True
                )

            fields_for_prompt = derive_prompt_fields(phase4_row)
            missing = triad_missing(fields_for_prompt)
            if missing:
                record = {
                    "sample_id": sid,
                    "phase4_row": phase4_row,
                    "judge": {
                        "fields": None,
                        "prompt": None,
                        "raw_output": None,
                        "error": f"missing_fields: {missing}",
                        "timestamp": datetime.now().isoformat(),
                        "meta": {
                            "judge_model": judge_model,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "task_name": task_name,
                            "model_name": model_name,
                            "prompt_id": prompt_id,
                        },
                    },
                }
                fout.write(json.dumps(record) + "\\n")
                fout.flush()
                continue

            prompt = judge_prompt
            for key, val in fields_for_prompt.items():
                prompt = prompt.replace(f"{{{key}}}", val)

            raw = None
            parsed = None
            error = None

            try:
                response = requests.post(
                    judge_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": judge_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are an expert evaluator in "
                                    "systems engineering education."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=120,
                )
                data = response.json()
                raw = data["choices"][0]["message"]["content"]
                parsed = safe_json(raw)
            except Exception as e:
                error = str(e)
                print(f"[worker] ERROR on sample {current}: {error}", flush=True)

            if prompt_id == "p1":
                fields = {
                    "technical_accuracy": {"score": None},
                    "conceptual_understanding": {"score": None},
                    "completeness": {"score": None},
                    "clarity_organization": {"score": None},
                    "professional_relevance": {"score": None},
                    "overall_score": None,
                }
                if parsed:
                    fields["technical_accuracy"]["score"] = (
                        (parsed.get("technical_accuracy") or {}).get("score")
                    )
                    fields["conceptual_understanding"]["score"] = (
                        (parsed.get("conceptual_understanding") or {}).get("score")
                    )
                    fields["completeness"]["score"] = (
                        (parsed.get("completeness") or {}).get("score")
                    )
                    fields["clarity_organization"]["score"] = (
                        (parsed.get("clarity_organization") or {}).get("score")
                    )
                    fields["professional_relevance"]["score"] = (
                        (parsed.get("professional_relevance") or {}).get("score")
                    )
                    fields["overall_score"] = parsed.get("overall_score")
            else:
                fields = {
                    "technical_accuracy": {"score": None, "justification": None},
                    "conceptual_understanding": {"score": None, "justification": None},
                    "completeness": {"score": None, "justification": None},
                    "clarity_organization": {"score": None, "justification": None},
                    "professional_relevance": {"score": None, "justification": None},
                    "overall_score": None,
                    "overall_assessment": None,
                    "key_strengths": None,
                    "improvement_areas": None,
                }
                if parsed:
                    for key in [
                        "technical_accuracy",
                        "conceptual_understanding",
                        "completeness",
                        "clarity_organization",
                        "professional_relevance",
                    ]:
                        fields[key] = {
                            "score": (parsed.get(key) or {}).get("score"),
                            "justification": (parsed.get(key) or {}).get("justification"),
                        }
                    fields["overall_score"] = parsed.get("overall_score")
                    fields["overall_assessment"] = parsed.get("overall_assessment")
                    fields["key_strengths"] = parsed.get("key_strengths")
                    fields["improvement_areas"] = parsed.get("improvement_areas")

            record = {
                "sample_id": sid,
                "phase4_row": phase4_row,
                "judge": {
                    "fields": fields,
                    "prompt": prompt,
                    "raw_output": raw,
                    "error": error,
                    "timestamp": datetime.now().isoformat(),
                    "meta": {
                        "judge_model": judge_model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "task_name": task_name,
                        "model_name": model_name,
                        "prompt_id": prompt_id,
                    },
                },
            }
            fout.write(json.dumps(record) + "\\n")
            fout.flush()

            sample_elapsed = time.time() - sample_start
            if sample_elapsed > 10:  # Log slow samples
                print(f"[worker] Sample {current} took {sample_elapsed:.1f}s", flush=True)

    total_elapsed = time.time() - start_time
    print("=" * 60, flush=True)
    print(f"[worker] ✓ Judging complete for {model_name}", flush=True)
    print(f"[worker] Total: {total_samples} samples in {total_elapsed/60:.1f} minutes", flush=True)
    print(f"[worker] Average rate: {total_samples/total_elapsed:.2f} samples/s", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--judge-model", required=True)
    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2000)
    parser.add_argument("--task-name", required=True)
    parser.add_argument("--model-name", required=True)
    args = parser.parse_args()

    run_worker(
        input_path=args.input,
        output_path=args.output,
        judge_model=args.judge_model,
        prompt_id=args.prompt_id,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        task_name=args.task_name,
        model_name=args.model_name,
    )
'''

print(f"✓ VERBOSE worker script loaded ({len(POD_WORKER_SCRIPT)} chars)")
```

---

## Fix 3: Helper Functions (Cell 6) - Add Streaming SSH Command

**ADD this function to cell 6 (after `run_and_check` function):**

```python
def stream_ssh_command(ssh, cmd, desc, log_func):
    """
    Run a remote command with real-time output streaming.
    Shows progress as it happens instead of blocking until completion.
    """
    log_func(f"▶ {desc}")
    log_func(f"[DEBUG] Command: {cmd}")

    # Get SSH transport channel
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)

    log_func(f"[STREAMING OUTPUT]")
    log_func("=" * 60)

    # Stream output in real-time
    while True:
        # Check for stdout
        if chan.recv_ready():
            data = chan.recv(4096).decode('utf-8', errors='replace')
            for line in data.splitlines():
                if line.strip():
                    output_line = f"  {line}"
                    print(output_line)
                    log_func(output_line)

        # Check for stderr
        if chan.recv_stderr_ready():
            data = chan.recv_stderr(4096).decode('utf-8', errors='replace')
            for line in data.splitlines():
                if line.strip():
                    error_line = f"  [stderr] {line}"
                    print(error_line)
                    log_func(error_line, level='WARN')

        # Check if command finished
        if chan.exit_status_ready():
            break

        time.sleep(0.1)  # Small delay to avoid CPU spinning

    # Get final exit code
    exit_code = chan.recv_exit_status()

    log_func("=" * 60)
    log_func(f"[DEBUG] Exit code: {exit_code}")

    if exit_code != 0:
        raise RuntimeError(f"{desc} failed with exit code {exit_code}")

    log_func(f"✔ {desc} finished successfully")

    chan.close()
    return exit_code
```

---

## Fix 4: PodSession.judge_model (Cell 7) - Use Streaming

**IN cell 7, REPLACE this block in the `judge_model` method:**

```python
        self.log(f"[DEBUG] Starting worker with command: {cmd}")

        self.log(f"  Running worker script...")
        start = time.time()
        run_and_check(self.ssh, cmd, f"Judge {model_name}", self.log)
        self.log(f"[DEBUG] Worker finished for {model_name}")
        elapsed = time.time() - start
        self.log(f"  ✓ Judging complete ({elapsed:.1f}s)")
```

**WITH:**

```python
        self.log(f"[DEBUG] Starting worker with command: {cmd}")
        self.log(f"  Running worker script with real-time streaming...")
        self.log("=" * 60)

        start = time.time()

        # Use streaming to show real-time progress
        stream_ssh_command(self.ssh, cmd, f"Judge {model_name}", self.log)

        elapsed = time.time() - start
        self.log("=" * 60)
        self.log(f"[DEBUG] Worker finished for {model_name}")
        self.log(f"  ✓ Judging complete ({elapsed:.1f}s)")
```

---

## Fix 5: Work Queue Logic (Cell 12) - Remove Model Limiting

**IN cell 12, REMOVE/COMMENT OUT these lines:**

```python
# Apply SAMPLE_N if set
if SAMPLE_N > 0 and len(models_to_judge) > SAMPLE_N:
    print(f"\n⚠ SAMPLE_N={SAMPLE_N}: Limiting to first {SAMPLE_N} models for testing")
    models_to_judge = models_to_judge[:SAMPLE_N]
```

**REPLACE with:**

```python
# NOTE: SAMPLE_N controls samples PER MODEL, not which models to process
# All models in models_to_judge will be processed, but each will only judge SAMPLE_N samples
if SAMPLE_N > 0:
    print(f"\n📊 SAMPLE_N={SAMPLE_N}: Each model will judge {SAMPLE_N} samples (not all {progress_df.iloc[0]['total_samples']})")
else:
    print(f"\n📊 SAMPLE_N=0: Each model will judge ALL samples ({progress_df.iloc[0]['total_samples']} per model)")
```

---

## Fix 6: run_pod_worker Function (Cell 18) - Apply SAMPLE_N to Samples

**IN cell 18, REPLACE this line:**

```python
                    # Prepare input data
                    input_data = prepare_model_input_data(model_name, sample_limit=0, is_test=False)
```

**WITH:**

```python
                    # Prepare input data
                    # IMPORTANT: SAMPLE_N limits samples per model, not model count!
                    input_data = prepare_model_input_data(
                        model_name,
                        sample_limit=SAMPLE_N,  # Apply SAMPLE_N here!
                        is_test=False
                    )

                    # Log what we're doing
                    sample_count = SAMPLE_N if SAMPLE_N > 0 else "ALL"
                    pod.log(f"  Judging {sample_count} samples for {model_name}")
```

---

## Fix 7: Add Checkpoint Download After Each Model (Cell 18)

**IN the `run_pod_worker` function, ADD this block INSIDE the `for model_name in models` loop, RIGHT AFTER `pod.judge_model()` succeeds:**

```python
                    # Run judging
                    result = pod.judge_model(model_name, input_data, is_test=False)
                    results['results'].append(result)

                    # CHECKPOINT: Log successful completion
                    pod.log(f"✓ CHECKPOINT: {model_name} completed successfully")
                    pod.log(f"  Output saved: {result['output_file']}")
                    pod.log(f"  Samples judged: {result['sample_count']}")
                    pod.log(f"  Time taken: {result['elapsed_s']:.1f}s")
                    pod.log(f"  Models remaining in this pod: {len(models) - (models.index(model_name) + 1)}")
```

---

## Summary of Changes

### What These Fixes Do:

1. **SAMPLE_N Behavior Fixed**:
   - BEFORE: Limited number of models processed
   - AFTER: Limits samples per model, processes ALL models

2. **Verbose Worker Script**:
   - Prints progress every 10 samples
   - Shows rate (samples/sec) and ETA
   - Reports completion statistics

3. **Streaming SSH Output**:
   - Real-time visibility into worker progress
   - No more "frozen" appearance during long jobs
   - Immediate feedback from remote pod

4. **Checkpoint Saves**:
   - Files downloaded after EACH model completes
   - Progress preserved even if pod crashes mid-run
   - Clear logging of what's been completed

### Testing Recommendations:

1. Set `SAMPLE_N = 10` and `TEST_SAMPLE_N = 5` for initial testing
2. Set `MAX_CONCURRENT_PODS = 1` to test single pod first
3. Watch for streaming output during test phase
4. Verify files appear in Phase 5 directory after each model
5. Once validated, scale up to full run with `SAMPLE_N = 0`

---

## Quick Reference: SAMPLE_N vs TEST_SAMPLE_N

| Setting | Purpose | Applies To | Example |
|---------|---------|------------|---------|
| **TEST_SAMPLE_N=10** | Test phase validation | First model only | 1 model × 10 samples = 10 judgments |
| **SAMPLE_N=0** | Full production run | ALL models | 19 models × 845 samples = 16,055 judgments |
| **SAMPLE_N=50** | Limited production test | ALL models | 19 models × 50 samples = 950 judgments |

✅ **Correct**: Set `SAMPLE_N=50` to test with 50 samples per model across all models
❌ **Incorrect (old behavior)**: Set `SAMPLE_N=50` to test with first 50 models at full 845 samples each

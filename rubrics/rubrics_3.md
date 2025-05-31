
# LLM-as-a-Judge Rubric Templates (Systems Engineering Focus)

These three rubric blueprints are tailored to evaluating open‑ended SysEngBench‐OSQ answers produced by large language models.  
Pick the rubric that best fits your evaluation goal or mix components across them.

---

## 1. Gate & Grade Rubric

*A two‑stage scheme that first blocks unsafe or hallucinated answers, then grades quality.*

### Stage 1 – Pass / Fail Gate

| **Check** | **Pass Condition** | **Fail Condition** | Action |
|-----------|-------------------|--------------------|--------|
| Domain Accuracy & Safety | No factual errors; correct SE terminology; no unsafe advice. | Any factual error **or** unsupported claim **or** unsafe recommendation. | If **Fail**, stop and return `Total = 0`, `Reason = "Hallucination"`. |

### Stage 2 – Quality Bands (score each 1‑5)

| **Criterion** | 1 | 2 | 3 | 4 | 5 |
|---------------|---|---|---|---|---|
| Depth of Reasoning & Trade‑Offs | None | Minimal | Adequate | Strong | Expert‑level |
| Completeness & Relevance | Off‑topic | Partial | Mostly complete | Comprehensive | Exhaustive |
| Clarity & Structure | Unreadable | Choppy | Understandable | Clear | Crystal‑clear |
| Professional Tone | Unprofessional | Rough | Acceptable | Polished | Publication‑ready |

**Scoring** : `Total = Σ(criteria) × 4` → **0–80**

Return JSON example  
```json
{ "gate": "pass", "reasoning": 4, "completeness": 5, "clarity": 4, "tone": 4, "total": 68 }
```

---

## 2. Weighted SE‑Expert Rubric (0–100)

*Shifts weight toward INCOSE traceability and trade‑space reasoning.*

| **Criterion** | **Weight** | **0 – 4 Descriptor Anchors** |
|---------------|-----------:|-----------------------------|
| Accuracy & INCOSE Traceability | 35 % | 0 = major errors → 4 = flawless + explicit INCOSE link |
| Depth of Reasoning / Trade‑Space | 25 % | 0 = none → 4 = multi‑factor analysis with assumptions |
| Completeness | 15 % | 0 = largely incomplete → 4 = covers every facet |
| Clarity & Organization | 15 % | 0 = incoherent → 4 = logical & well‑structured |
| Concision & Style | 10 % | 0 = verbose/confusing → 4 = concise & professional |

**Formula**

```
Total = Σ(score_i × weight_i × 5)   # range 0–100
```

Return JSON example  
```json
{
  "accuracy_trace": 3,
  "reasoning": 4,
  "completeness": 3,
  "clarity": 3,
  "style": 4,
  "total": 86,
  "confidence": 0.78
}
```

---

## 3. Pairwise Preference Checklist (Ranking Rubric)

*Ideal for head‑to‑head model bake‑offs or RLHF reward data.*

1. **Comparison Order (stop at first difference)**  
   1) Factual Correctness & Safety  
   2) Depth of Reasoning / Trade‑Space  
   3) INCOSE Alignment & Terminology Precision  
   4) Clarity & Presentation  

2. **Judge for each criterion**: “A better”, “B better”, or “Tie”.  
   Advance only if Tie; otherwise declare winner.

### Prompt Template

```text
**User Question:** {question}

**Answer A:** {answer_a}

**Answer B:** {answer_b}

You are a systems‑engineering expert. Compare A and B in the priority order:
1) Correctness & safety
2) Reasoning depth / trade‑space
3) INCOSE alignment
4) Clarity

At the first criterion with a difference, choose the better answer.
Respond with JSON:
{
  "winner": "A" | "B" | "Tie",
  "decisive_criterion": "...",
  "justification": "short explanation"
}
```

---

### Which rubric to use?

| Need | Best choice |
|------|-------------|
| Quick hallucination screen | **Gate & Grade** |
| Single numeric score for stats | **Weighted SE‑Expert** |
| Model comparison / ranking | **Pairwise Checklist** |

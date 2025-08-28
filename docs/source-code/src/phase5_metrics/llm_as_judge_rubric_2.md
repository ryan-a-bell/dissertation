
| **Criterion** | **Weight** | **0 – 4 (Poor)** | **5 – 9 (Fair)** | **10 – 14 (Good)** | **15 – 20 (Excellent)** |
|---------------|-----------:|------------------|------------------|---------------------|--------------------------|
| **Domain Accuracy & Traceability** | **30 %** | Major factual errors or misuse of SE concepts; no trace to INCOSE categories. | Some correct info but notable inaccuracies or missing citations. | Mostly accurate; minor slips; key INCOSE concepts referenced. | Completely accurate, precise, and explicitly tied to correct INCOSE tasks/terminology. |
| **Depth of Reasoning / Trade-Space Analysis** | **25 %** | No reasoning or purely surface statements. | Minimal rationale; simplistic trade-offs. | Solid reasoning with at least one explicit trade-off or assumption. | Rigorous, multi-factor reasoning; clear assumptions, constraints, and trade analysis. |
| **Relevance & Completeness** | **20 %** | Off-topic or largely incomplete. | Partially answers; important facets missing. | Addresses most parts with adequate depth. | Fully covers all requested facets; no major omissions. |
| **Clarity & Structure** | **15 %** | Disorganized, hard to follow. | Understandable but clunky or scattered. | Logical flow; minor clarity issues. | Crystal-clear, well-structured; figures/bullets where useful. |
| **Hallucination / Safety Penalty**¹ | **–10 → 0 pt** | Fabricated data, unsafe advice, or blatant hallucination detected. | – | – | No hallucinations; sources or rationale transparent. |
| **Language Quality (concise, professional)** | **10 %** | Frequent grammar errors / verbosity. | Some errors but understandable. | Generally clean writing. | Near-flawless, concise, professional tone. |
| **Evaluator Confidence**² | *(recorded separately, 0–1)* |  |  |  |  |

¹ *Deduct up to 10 points from the subtotal if hallucinations or unsafe recommendations appear.*

² *LLM judge returns a float 0–1 (“How confident are you in this grade?”) used for downstream filtering or weighted ICC.*


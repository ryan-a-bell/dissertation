# Systems Engineering AI Consensus & Agent Frameworks

> **Purpose**: Living research document consolidating ideas, architecture, experimental design, and hypotheses for extending *Automating AI Expert Consensus: Feasibility of Language Model‑Assisted Consensus Methods for Systems Engineering* into a multi‑agent, multi‑topology, knowledge‑aware evaluation program.

---

## 1. Research Lineage & Motivation

### Prior Work (Baseline)
The prior paper established the *feasibility* of automating traditional systems‑engineering consensus methods using large language models. It:
- Cataloged applicable SE consensus methods (Delphi, Fuzzy Delphi, Structured Expert Judgment, NGT, Stepladder, Dialectical Inquiry, Multi‑Voting).
- Identified implementation challenges (bias, role stability, convergence, memory, oversight).
- Proposed agentic orchestration frameworks as practical scaffolding.
- Explicitly called for a reusable Python library implementing AI‑assisted consensus.

### Extension Contribution (This Work)
This research moves from *method feasibility* to *organizational effectiveness* by asking:

> **Which combinations of agent team topology, consensus method, and knowledge regime produce the best SE outcomes for different task classes?**

New contributions:
1. Comparative evaluation of **agent team topologies** executing identical consensus methods.
2. Controlled experimentation with **knowledge supplementation regimes** (general vs niche vs heterogeneous vs conflicting).
3. Quantitative measurement of **consensus quality, stability, robustness, and cost**.
4. Delivery of the previously proposed **ConsensusOps** library as an executable research artifact.

---

## 2. Core Research Questions

1. How do different **agent team topologies** affect the performance of established SE consensus methods?
2. How does **domain‑specific (niche) knowledge** alter consensus quality, convergence, and robustness?
3. Which topology–consensus pairings are best suited to specific SE tasks (trade studies, change impact, hazard analysis, verification planning)?
4. Under what conditions does added expertise *fragment* rather than improve consensus?

---

## 3. Experimental Design Overview

A full **factorial design**:

```
Agent Topology (T) × Consensus Method (C) × Knowledge Regime (K)
```

All experiments are:
- Fully synthetic
- Deterministic or seeded
- Free of human subjects or PII
- Automatically scored against ground truth

---

## 4. Agent Team Topologies (T)

### T1 — A2A Pipeline
Sequential, stage‑gated handoffs:
- Requirements → Architecture → Trade → V&V
- Consensus applied at terminal stages

**Strengths**: Speed, auditability
**Weaknesses**: Early error amplification

---

### T2 — Hub‑and‑Spoke (CAO / Chief Engineer)
Central moderator governs standards, waivers, and gates.

**Strengths**: Compliance, review readiness
**Weaknesses**: Latency, potential anchoring

---

### T3 — Blackboard + Knowledge Graph
Artifact‑centric collaboration via a shared model and provenance graph.

**Strengths**: Change impact, traceability, conflict representation
**Weaknesses**: Infrastructure complexity

---

### T4 — Contract‑Net / Market (IPT Analog)
CFP → agent bids → selection via aggregation.

**Strengths**: Trade‑space exploration, competition
**Weaknesses**: Requires careful scoring normalization

---

### T5 — Swarm / Cells
Distributed cells with periodic synchronization.

**Strengths**: Exploration, creativity
**Weaknesses**: Drift without governance

---

## 5. Consensus Methods (C)

### Classical & Structured Methods
- Delphi / Fuzzy Delphi
- Structured Expert Judgment (Cooke’s method)
- Nominal Group Technique (NGT)
- Stepladder
- Dialectical Inquiry
- Multi‑Voting

### Quantitative Aggregation
- Majority Judgment
- Trimmed mean / median
- Rank aggregation (Borda, Copeland, Kemeny approximations)
- MCDM (AHP, TOPSIS, PROMETHEE)

### Probabilistic / Evidence Fusion
- Dawid–Skene
- Hierarchical Bayesian aggregation
- Dempster–Shafer belief fusion

### Distributed Consensus (Swarm)
- Gossip / push‑sum
- Byzantine‑resilient voting variants

---

## 6. Knowledge Regimes (K)

| Code | Description |
|----|------------|
| K0 | No retrieval (base LLM only) |
| K1 | General SE corpus |
| K2 | High‑quality niche domain corpus |
| K3 | Conflicting or outdated corpus |
| K4 | Heterogeneous niche corpora per agent |

Purpose:
- Isolate the value of expertise
- Test robustness to misinformation
- Observe fragmentation vs complementarity

---

## 7. SE Task Scenarios

All scenarios are synthetic with oracle ground truth:

1. Requirements refinement & hazard tagging
2. Trade study and alternative ranking
3. Change Impact Analysis (CIA) on SysML v2 slices
4. Verification planning & coverage analysis
5. SRR/PDR/CDR gate readiness checks

---

## 8. Evaluation Metrics

### Product Quality
- CIA Precision / Recall / F1
- Traceability yield & orphan rate
- Verification coverage
- Trade‑study regret / NDCG

### Consensus Quality
- Kendall’s W (agreement)
- Kendall’s τ (ranking similarity)
- Fleiss’ κ (categorical agreement)
- Entropy reduction across rounds

### Process & Cost
- Time to convergence
- Message / token counts
- Rework fraction
- Gate‑pass probability

### Robustness
- Performance degradation under K3
- Resistance to adversarial or noisy agents

### Provenance & Governance
- Citation backing rate
- Contradiction rate
- Agent contribution (Shapley‑style)

---

## 9. ConsensusOps Library (Deliverable)

A reusable Python package implementing consensus logic independent of agent framework.

**Modules**:
- `delphi.py`
- `sej.py`
- `vote.py`
- `rank.py`
- `mcdm.py`
- `probabilistic.py`
- `dst.py`
- `dialectic.py`

Each module:
- Accepts standardized proposal schemas
- Emits decisions + provenance
- Computes convergence metrics

---

## 10. Technology Stack

- LLMs: local and hosted (switchable)
- Agent frameworks: CrewAI, AutoGen, Swarm
- Orchestration: LangGraph
- Retrieval: Haystack / LlamaIndex
- Vector DB: Qdrant / Weaviate
- Blackboard / KG: Neo4j
- Policy & rules: SHACL + Rego
- Messaging: NATS
- Experiment control: Hydra + seeded runs

---

## 11. Hypotheses (Pre‑Registration Candidates)

H1: Blackboard + evidence‑based consensus dominates CIA and traceability tasks.

H2: Contract‑Net + rank aggregation yields superior trade‑space exploration.

H3: Hub‑and‑Spoke + Delphi produces the most review‑ready artifacts.

H4: Heterogeneous niche knowledge improves outcomes only when strong consensus mechanisms are present.

H5: Swarm topologies require periodic global consensus to prevent drift under K4.

---

## 12. Threats to Validity

- LLM stochasticity → mitigated via seeded runs
- Retrieval confounds → logged and analyzed as covariates
- Metric gaming → multi‑objective reporting
- Overfitting to synthetic tasks → scenario diversity

---

## 13. Research Roadmap

1. Implement ConsensusOps v0.1
2. Baseline Hub & Blackboard on two scenarios
3. Add K2/K3 stress tests
4. Expand to Contract‑Net and Swarm
5. Publish dataset, code, and results

---

## 14. Intended Use

This document serves as:
- Dissertation backbone
- Grant proposal seed
- Living lab notebook
- Open‑source roadmap

---

*End of document*


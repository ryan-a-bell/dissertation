# Literature Knowledge Graph Workflows

This document outlines **practical, end-to-end workflows** for building and analyzing a **knowledge graph of academic papers and their citations** in order to:

- Understand *who cites whom*
- Reveal *intellectual lineages*
- Identify *clusters, silos, and bridges*
- Detect *knowledge gaps* suitable for new research

The workflows are organized by **starting point**, since that determines both tooling and rigor.

---

## 1️⃣ Starting from **One Seed Paper**
> *“I have one foundational paper — show me the field around it.”*

### Primary Objectives
- Rapidly understand the paper’s intellectual context
- Identify prior foundations and downstream work
- Surface adjacent clusters the paper does *not* engage with

This approach prioritizes **speed and intuition**, followed by validation.

---

### Step A — Rapid Neighborhood Scan (≈10 minutes)

**Actions**
1. Input the paper’s DOI into a citation-mapping tool
2. Capture:
   - Prior works (references)
   - Derivative works (papers citing it)
3. Expand the graph 1–2 hops
4. Enable timeline / temporal views

**What to Look For**
- Papers that act as *bridges* between clusters
- Late papers citing early foundational work
- Asymmetrical citation behavior between clusters

This step often reveals **candidate gaps immediately**.

---

### Step B — Structural Validation (≈30–60 minutes)

**Actions**
1. Query an open scholarly database for:
   - Full reference list
   - Cited-by relationships
   - Concepts / topics
2. Build:
   - Citation network
   - Co-citation network
3. Visualize clusters and centrality

**Purpose**
- Distinguish *true gaps* from UI artifacts
- Confirm whether clusters are socially or conceptually siloed

---

### Step C — Optional: Promote to a Working Knowledge Graph

**Actions**
- Ingest papers into a graph database
- Model nodes:
  - Paper
  - Author
  - Venue
  - Concept
- Model edges:
  - CITES
  - AUTHORED_BY
  - PUBLISHED_IN

**Questions Enabled**
- Which concepts never co-occur in citations?
- Which authors bridge subfields?
- Where are temporal dead zones?

---

### Best Use Cases
- Early-stage exploration
- Related-work sections
- Identifying synthesis opportunities

---

## 2️⃣ Starting from a **Zotero Library**
> *“I already curated the literature — now analyze it.”*

This is the **highest signal-to-noise** entry point.

---

### Step A — Treat Zotero as Ground Truth

**Actions**
1. Export Zotero library (CSV or BibTeX)
2. Resolve DOIs / unique paper IDs
3. Pull enriched metadata:
   - Abstracts
   - Concepts
   - Citation counts
   - References and cited-by links

**Why This Matters**
- Zotero represents *intentional selection*
- Downstream analysis is anchored to your judgment

---

### Step B — Corpus-Level Network Analysis

**Actions**
- Construct:
  - Direct citation network
  - Bibliographic coupling network
  - Co-citation clusters
- Identify:
  - Isolated subgraphs
  - Dominant lineages
  - Under-cited but central papers

**This Is Where Real Gaps Appear**
- Theory with no application
- Methods cited without benchmarks
- Applications citing no theory

---

### Step C — Formal Gap Identification

**Graph Queries to Run**
- Concepts appearing in abstracts but never co-cited
- Authors frequently cited together but never cross-citing
- Parallel venues publishing similar work with no interaction

**Outcome**
- Defensible, visualizable gap claims
- Strong basis for dissertation chapters or journal positioning

---

### Best Use Cases
- Dissertation research
- Meta-analyses
- Framework or benchmark positioning
- Reproducible literature reviews

---

## 3️⃣ Starting from a **Keyword Query**
> *“I want to understand an entire field.”*

This approach is the **most powerful** — and the most dangerous if done poorly.

---

### Step A — Controlled Corpus Construction

**Actions**
1. Query an open scholarly index using:
   - Keywords
   - Concept filters
   - Time bounds
   - Venue constraints
2. Cap initial corpus (≈300–1,000 papers)
3. Deduplicate semantically overlapping results

**Critical Rule**
> Garbage in → hallucinated gaps out

---

### Step B — Field-Scale Mapping

**Actions**
- Build:
  - Citation network
  - Co-citation clusters
  - Topic evolution over time

**What to Look For**
- Rapidly growing clusters with shallow theoretical roots
- Mature clusters with no modern successors
- Methods disconnected from applications

---

### Step C — Strategic Gap Detection

**Interpretive Layer**
Tag clusters as:
- Theory
- Method
- Application
- Benchmark
- Tooling

**Gap Questions**
- Which methods lack benchmarks?
- Which applications cite no theory?
- Which theories are never instantiated?

These intersections are **high-value paper opportunities**.

---

### Best Use Cases
- Survey papers
- New research agendas
- Grant proposals
- Strategic positioning

---

## 🔁 Summary: Choosing the Right Path

| Starting Point | Primary Strategy | Strength |
|---------------|------------------|----------|
| One seed paper | Rapid mapping → validation | Speed + intuition |
| Zotero library | Corpus-driven graph analysis | Rigor + defensibility |
| Keyword query  | Field-scale modeling | Discovery + novelty |
---

## Next Extensions (Optional)
- Automate pipelines using APIs and Python
- Quantify gap metrics (cluster separation, citation asymmetry)
- Integrate literature graphs into digital threads or system models

This document can serve as a **repeatable playbook** for literature-driven discovery and research planning.


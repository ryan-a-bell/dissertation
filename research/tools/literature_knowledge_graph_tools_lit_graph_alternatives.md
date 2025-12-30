# Literature Knowledge Graph Tools (LitGraph Alternatives)

This document summarizes tools and workflows for **visualizing scholarly knowledge graphs**, where **nodes = papers** and **edges = citations/references**. The goal is to help identify:
- Who cites whom
- Research clusters and lineages
- Knowledge gaps and underexplored connections

---

## 1. Plug-and-Play Web Tools (Fastest to Use)

### Litmaps
**Strengths**
- Interactive citation maps built from seed papers
- Strong temporal view (how a field evolves)
- Automatic discovery of related and newer papers

**Best for**
- Finding gaps between older foundational work and newer literature
- Seeing how ideas propagate over time

---

### Connected Papers
**Strengths**
- Extremely fast “seed paper → graph” visualization
- Clean, intuitive UI
- Good for discovering adjacent work

**Best for**
- Rapid exploration around a single influential paper
- Identifying nearby clusters you may have missed

---

### Research Rabbit
**Strengths**
- Continuous exploration workflow
- Strong author-based and paper-based expansion
- Acts like a recommendation engine for research

**Best for**
- Iterative literature discovery
- Growing a reading list organically

---

## 2. Bibliometric & Citation-Network Analysis Tools (More Rigor)

### CitNetExplorer
**Strengths**
- Designed specifically for citation networks
- Direct citation lineage analysis
- Strong clustering and drill-down features

**Best for**
- Understanding the development of a research field
- Analyzing who references whom in detail

---

### VOSviewer
**Strengths**
- Bibliometric mapping (citation, co-citation, bibliographic coupling)
- Handles large datasets well
- Supports clustering and density views

**Best for**
- Field-level structure and theme identification
- Visualizing clusters at scale

---

### CiteSpace / Sci2 / Gephi (DIY Analysis)
**Strengths**
- Full control over data and analysis
- Advanced graph metrics and custom layouts

**Typical workflow**
1. Export citation data from a scholarly database
2. Build a graph (papers + citations)
3. Analyze and visualize using Gephi or Sci2

**Best for**
- Custom bibliometric studies
- Reproducible academic analysis

---

## 3. Open-Source & Graph-Explorer Style Tools

### Argo Scholar
**Strengths**
- Open-source, web-based
- Built on Semantic Scholar data
- Shareable exploration sessions

**Best for**
- Open, collaborative literature exploration
- Lightweight graph browsing without heavy setup

---

### Oignon
**Strengths**
- Open-source citation graph exploration
- Focus on scalability and traversal depth

**Best for**
- Users wanting a LitGraph-like tool they can run and extend

---

## 4. Build-Your-Own Knowledge Graph (Maximum Control)

### OpenAlex-Based Pipeline

**Why OpenAlex**
- Large, open catalog of scholarly works
- API access to papers, authors, venues, and citations

**Typical Pipeline**
1. Define seed papers (DOIs, titles, or keywords)
2. Query OpenAlex for:
   - References
   - Cited-by relationships
3. Build a graph:
   - Nodes: papers, authors, venues
   - Edges: cites, authored-by, published-in
4. Visualize and analyze using:
   - Gephi (interactive exploration)
   - Neo4j (queryable knowledge graph)
   - Cytoscape.js (web-based UI)

**Best for**
- Reproducible research
- Integration with LLMs, RAG, or MBSE pipelines
- Long-term, evolving literature knowledge graphs

---

## 5. How to Use These Tools to Find Knowledge Gaps

Look for the following graph patterns:

### Bridging Papers
- Nodes connecting two otherwise separate clusters
- Often under-cited but highly influential

### Isolated Clusters
- Groups of papers that do not cite each other
- Indicates siloed communities or missed synthesis

### Temporal Gaps
- Foundational cluster with few recent citations
- Opportunity for modern review or extension

### Citation Asymmetry
- One cluster cites another heavily, but not vice versa
- Suggests unidirectional influence or awareness gaps

---

## 6. Quick Tool Selection Guide

**Fast discovery, minimal setup**
- Litmaps
- Connected Papers
- Research Rabbit

**Rigorous citation lineage analysis**
- CitNetExplorer
- VOSviewer

**Open, extensible, KG-friendly workflows**
- OpenAlex + Neo4j / Gephi
- Argo Scholar
- Oignon

---

## 7. Recommended Next Steps

1. Start with a web tool (Litmaps or Connected Papers) to identify core clusters
2. Export or list key papers
3. Use OpenAlex to build a reproducible citation graph
4. Analyze gaps, bridges, and cluster boundaries
5. Feed insights into reviews, dissertations, or research roadmaps

---

*This document is designed to be dropped directly into a research repo, Obsidian vault, or dissertation support materials.*


# Chapter 1 Gap Analysis and Remediation Plan

**Document:** `manuscript/overleaf/chapter1.tex`
**Analysis Date:** 2025-12-30
**Status:** Completed

---

## Executive Summary

Chapter 1 (Introduction) has a solid structural foundation but contains several incomplete sections, placeholder content, and structural redundancies that need to be addressed before the manuscript is complete. This document catalogs all identified gaps and provides a systematic remediation plan.

---

## Gap Inventory

### Critical Gaps (Content Missing/Incomplete)

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| G1 | Lines 10-12 | **Missing SE definitions** - Placeholder bullets `- 1 def, - 2 def, - 3 def` instead of actual definitions | 🔴 Critical |
| G2 | Lines 31, 82, 90, 126 | **PPT citation placeholders** - `<<cite from ppt>>` not replaced with proper citations | 🔴 Critical |
| G3 | Lines 120-128 | **LLM failure modes stub** - Section contains only notes, no substantive content on hallucinations, prompt injection, contamination | 🔴 Critical |
| G4 | Lines 82-88 | **Missing cross-domain AI productivity evidence** - Placeholder for Longshore, SEW4AI, Wach work | 🔴 Critical |
| G5 | Lines 121-123 | **Missing safety-critical/disconnected use cases** - Notes only about DoD/shipboard applications | 🔴 Critical |

### Structural Issues

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| G6 | Lines 43-57 | **Duplicate "old text" block** - Redundant SE explanation that repeats concepts already covered | 🟠 Major |
| G7 | Lines 7-57 | **Section 1.1 flow disruption** - Disjointed narrative with comment at line 41 noting reorganization needed | 🟠 Major |
| G8 | Lines 10-12 | **Markdown syntax in LaTeX** - Uses `- ` instead of `\begin{itemize}` | 🟠 Major |

### Missing Scholarly Elements

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| G9 | Section 1.2-1.3 | **No explicit hypothesis statement** - Research questions exist but no formal hypothesis | 🟡 Moderate |
| G10 | Section 1.2 | **Weak research gap statement** - Gap is implied but not explicitly articulated | 🟡 Moderate |
| G11 | Line 71 | **Unverified citation** - `\cite{brown2023engineering}` may not exist in references.bib | 🟡 Moderate |

### Minor Polish Items

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| G12 | Lines 77, 88 | **Incomplete sentences** - Missing periods/transitions | 🟢 Minor |
| G13 | Throughout | **Inconsistent acronym usage** - Mix of `LLMs` and `\acp{llm}` | 🟢 Minor |

---

## Remediation Plan

### Step 1: Add Systems Engineering Definitions (G1, G8)

**Target:** Lines 10-12

**Action:** Replace markdown placeholder with proper LaTeX enumeration containing three authoritative SE definitions:

1. **INCOSE SE Handbook (2015):** "Systems engineering is a transdisciplinary and integrative approach to enable the successful realization, use, and retirement of engineered systems, using systems principles and concepts, and scientific, technological, and management methods."

2. **ISO/IEC/IEEE 15288:2023:** "An interdisciplinary approach governing the total technical and managerial effort required to transform a set of stakeholder needs, expectations, and constraints into a solution and to support that solution throughout its life."

3. **NASA Systems Engineering Handbook:** "A methodical, disciplined approach for the design, realization, technical management, operations, and retirement of a system."

**Files Modified:** `chapter1.tex`

---

### Step 2: Consolidate Section 1.1 Structure (G6, G7)

**Target:** Lines 7-57

**Action:**
1. Delete redundant "old text" block (lines 43-57) - content is duplicative
2. Reorganize remaining content into logical flow:
   - SE Complexity (cognitive load, interdependencies)
   - SE Impact (program success correlation)
   - Lifecycle Cost (10-100x multiplier)
   - AI Opportunity (bandwidth augmentation)
   - Trust Requirement (transition to Section 1.1.3)

**Files Modified:** `chapter1.tex`

---

### Step 3: Complete LLM Failure Modes Section (G3, G5)

**Target:** Lines 120-128 (Section 1.1.3.1)

**Action:** Write substantive paragraphs covering:

1. **Hallucinations:** Confident generation of factually incorrect information; particularly dangerous in SE where erroneous requirements or design decisions propagate through lifecycle

2. **Prompt Injection:** Adversarial inputs that manipulate model behavior; security concern for SE tools processing untrusted inputs

3. **Training Data Contamination:** Benchmark leakage and memorization; challenges validity of evaluation results

4. **Reasoning Opacity:** Difficulty tracing model decision paths; conflicts with SE traceability requirements

5. **Disconnected/Air-gapped Deployment:** DoD and safety-critical systems often operate without internet connectivity; implications for model updates, RAG systems, and API-based services

**Files Modified:** `chapter1.tex`

---

### Step 4: Add Cross-Domain AI Evidence (G4)

**Target:** Lines 82-88

**Action:** Add paragraph with specific productivity gains and citations:

- Software engineering: 25-55% productivity gains (GitHub Copilot studies)
- Mechanical/civil design: 10-40% reduction in design iteration time
- Manufacturing: Up to 10x speedup on routine documentation tasks

**Citations to add:**
- `\cite{longshore_leveraging_2024}`
- `\cite{Wach2025LLMTradeOffs}`
- `\cite{wach_using_2024}`

**Files Modified:** `chapter1.tex`

---

### Step 5: Strengthen Problem Statement (G9, G10)

**Target:** Section 1.2 (The Problem)

**Action:**
1. Add explicit **Research Gap Statement** before research questions
2. Add formal **Hypothesis Statement**

**Proposed Hypothesis:**
> "If the evaluation modalities of MCQs and OSQs are systematically compared for systems engineering domain-specific tasks, then OSQs will reveal deeper reasoning capabilities and limitations that MCQs alone cannot capture, while MCQs will provide more cost-effective and reproducible baseline measurements."

**Files Modified:** `chapter1.tex`

---

### Step 6: Fix Citations (G2, G11)

**Target:** Lines 31, 71, 82, 90, 126

**Action:**
1. Replace all `<<cite from ppt>>` placeholders with proper `\cite{}` commands
2. Verify `brown2023engineering` exists in references.bib (if not, replace or add)
3. Use existing citations from .bib where applicable

**Files Modified:** `chapter1.tex`

---

### Step 7: Polish (G12, G13)

**Target:** Throughout chapter

**Action:**
1. Fix incomplete sentences (add periods, transitions)
2. Standardize acronym usage to LaTeX `\ac{}` and `\acp{}` commands
3. Ensure consistent terminology

**Files Modified:** `chapter1.tex`

---

## Verification Checklist

After remediation, verify:

- [x] All placeholder text removed
- [x] No markdown syntax in LaTeX file
- [x] All citations resolve correctly
- [x] Section flow is logical and non-redundant
- [x] Hypothesis statement present
- [x] Research gap explicitly stated
- [x] LLM failure modes section complete
- [x] Cross-domain evidence included with citations
- [x] Acronyms used consistently

---

## Notes

- The chapter has good bones - the research questions, contributions, and structure sections are well-developed
- Primary issues are incomplete drafts in Sections 1.1.1, 1.1.3.1, and 1.2
- References.bib already contains relevant citations (Longshore, Wach, etc.) that just need to be incorporated

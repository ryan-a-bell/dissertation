# Related Work Prompt Variants

**Purpose**: Alternative prompt configurations for specific dissertation contexts. Use these as replacements for the Task/Output sections in the core prompt.

**Prerequisite**: Use the dissertation context from `related-work-core.md` with these variants.

---

## Variant A: Ultra-Tight (For Dense Chapters)

Use when space is limited or the literature review section is already lengthy.

### Replacement Task Block

> **Task**
> Produce a **single cohesive paragraph** situating the external work relative to this dissertation.
>
> Your output should:
> - Emphasize methodological overlap and key distinctions
> - Avoid redundancy with prior related-work sections
> - Focus on the most salient connection to this dissertation's contributions
>
> **Output Constraints**
> - Write in **formal academic prose** suitable for direct inclusion
> - Maximum length: **one paragraph (4-6 sentences)**
> - Do not use bullet points
> - Maintain neutral, scholarly tone
>
> **External Work to Analyze**
>
> `[PASTE PAPER ABSTRACT / FULL TEXT HERE]`

---

## Variant B: Comparative Emphasis (For Methodology Comparisons)

Use when the external work has a similar experimental design and you need to highlight methodological differences.

### Replacement Task Block

> **Task**
> Analyze the external work with emphasis on **evaluation design, task structure, and judgment mechanisms**.
>
> Your output should:
> - Compare the external work's evaluation methodology to this dissertation's approach
> - Highlight differences in question difficulty calibration, subjectivity handling, and scalability
> - Discuss how question formats (MCQ vs OSQ or equivalent) are treated
> - Address any consensus or multi-judge approaches used
>
> **Output Constraints**
> - Write in **formal academic prose** suitable for direct inclusion
> - Length target: **2-3 paragraphs**
> - Structure around methodological comparison, not just findings
> - Do not use bullet points
>
> **External Work to Analyze**
>
> `[PASTE PAPER ABSTRACT / FULL TEXT HERE]`

---

## Variant C: Gap-Highlighting (For Justifying Novelty)

Use when positioning the external work to motivate the need for your dissertation's contributions.

### Replacement Task Block

> **Task**
> Analyze the external work and **explicitly highlight its limitations** that motivate the need for this dissertation's contributions.
>
> Your output should:
> - Summarize the external work's approach and contributions
> - Identify specific gaps, limitations, or unaddressed questions
> - Explain how this dissertation addresses those gaps
> - Frame the dissertation as a natural extension or necessary complement
>
> **Output Constraints**
> - Write in **formal academic prose** suitable for direct inclusion
> - Length target: **2-3 paragraphs**
> - Maintain respectful, scholarly tone (critique the gap, not the authors)
> - Do not use bullet points
> - Avoid dismissive language; frame as "opportunities for further research" that this dissertation addresses
>
> **External Work to Analyze**
>
> `[PASTE PAPER ABSTRACT / FULL TEXT HERE]`

---

## Quick Reference: When to Use Each Variant

| Variant | Use When | Typical Length |
|---------|----------|----------------|
| **Core** (default) | General related work analysis | 1-3 paragraphs |
| **A: Ultra-Tight** | Space-constrained sections, dense chapters | 1 paragraph |
| **B: Comparative** | Similar methodology in external work | 2-3 paragraphs |
| **C: Gap-Highlighting** | Justifying dissertation novelty | 2-3 paragraphs |

---

## Combining Variants

You can mix elements from different variants. For example:
- Use **Variant C** for foundational papers that directly motivate your work
- Use **Variant A** for tangentially related papers
- Use **Variant B** for benchmark papers with comparable methodology

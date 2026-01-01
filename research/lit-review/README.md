# Literature Review Prompts (Phase 2 / 2.5)

This folder contains two prompts designed to support a **Phase 2 evidence-ingestion workflow** for a literature review, where you:
- map a paper to your outline bins, and
- extract **verbatim** quotes with location metadata for later synthesis.

## Files

- `phase2_evidence_ingestion_prompt.md`  
  Strict extraction + bin mapping (minimal interpretation)

- `phase25_annotated_capture_prompt.md`  
  Same extraction + a Phase 2.5 “annotated capture” section to support clustering



Approach 1 = “my outline is the scaffold; help me clean + bucket the evidence inside it.”
- phase275

Approach 2 = “my outline might be wrong; help me discover the true clusters and feed them back into Phase 1.”
- phase2to1

## How to use

1. Open a prompt file.
2. Copy the **Copy/Paste Prompt** block into your LLM tool.
3. Paste either:
   - full paper text, or
   - abstract + intro + conclusion (first pass), then methods/results (second pass).
4. Paste the extracted quotes directly into your outline bins, keeping the provided location metadata.

## Notes

- Quotes are intentionally short (1–4 sentences) to preserve compliance and keep the capture “surgical”.
- If you want paste-ready bullets, include the optional “Paste Blocks” add-on at the bottom of the prompt.


--- 

Need to somewhat merge this with above

# Literature Review Prompts — Phase 2.75 and Phase 3 (Approach 1)

These prompts extend your Phase 2 workflow into Phase 3 while preserving your existing outline.

## Files

- `phase275_global_bucketing_prompt.md`  
  Organize a messy `.tex` evidence dump into thematic buckets per outline bin, flagging duplicates/misfiles/conflicts.

- `phase3_synthesis_by_bucket_prompt.md`  
  Convert bucketed evidence into synthesis text with explicit traceability to citation keys.

## Recommended workflow

1. Run Phase 2 as you are doing now (drop quotes/snippets into outline bins).
2. Run Phase 2.75 on one top-level section of your `.tex` at a time (to keep context manageable).
3. Merge bucketed outputs (concatenate by bin).
4. Run Phase 3 to produce synthesis paragraphs + transitions + candidate gap statements.
5. Move into Phase 4 (tables/diagrams) and Phase 5 (gaps), using the Phase 3 outputs.

## Notes

- Phase 2.75 is *organization only*: it keeps snippets verbatim and does not rewrite prose.
- Phase 3 allows paraphrase but requires citation-key traceability.

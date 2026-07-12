# Phase E.8 — ChatGPT Audit Batches

## Goal
Split the residual audit sample into fixed-size batches so ChatGPT can annotate them reliably without manual slicing.

## Batch spec
- source sample: `experiments/residual_audit/reports/residual_audit_sample_v1.jsonl`
- total rows: `400`
- batch size: `25`
- total batches: `16`

## Generated files
- batch index: `experiments/residual_audit/reports/chatgpt_batches_v1_index.json`
- batch directory: `experiments/residual_audit/reports/chatgpt_batches_v1/`

## Recommended workflow
1. load `chatgpt_annotation_prompt.md`
2. load `annotation_schema.json`
3. send one batch at a time from `chatgpt_batches_v1/`
4. save ChatGPT outputs separately as:
   - `experiments/residual_audit/reports/annotations/batch_XX_annotations.jsonl`
5. aggregate all annotation files after completion

## Why batching matters
- reduces prompt length risk
- makes the audit resumable
- makes reviewer progress traceable
- allows spot-checking quality batch by batch

# Phase E.8 — Residual Audit Draft v1

## Goal
Produce a first structured annotation pass over a reproducible sample of the current residual `other`.

## Input
- sample file: `experiments/residual_audit/reports/residual_audit_sample_v1.jsonl`
- sample size: `400`
- source dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- source residual size: `35,952`

## Method
This draft annotation pass used:
- the prepared residual audit sample
- the structured annotation schema
- internal semantic retrieval candidates
- explicit heuristics over title, departments, skills, and text excerpts

This is a pre-audit draft, not a final human-reviewed ground truth.

## Output
- annotations: `experiments/residual_audit/reports/residual_audit_annotations_draft_v1.jsonl`
- summary: `experiments/residual_audit/reports/residual_audit_annotations_draft_v1_summary.json`

## Bucket Distribution
- `keep_other_by_policy`: `365`
- `recoverable_now`: `11`
- `recoverable_with_context`: `21`
- `taxonomy_gap`: `1`
- `noise_or_non_role`: `2`

## Initial Reading
The draft is very conservative.

What it suggests:
- a large part of the sample still looks ambiguous or unsafe to force-map with current evidence
- a small but real subset appears recoverable now with narrow rules
- another small subset appears recoverable only with stronger context
- pure noise exists, but it is not the dominant class in this sample

## Important Caveat
This should not be treated as final truth.
It should be treated as:
- a first machine-assisted residual composition estimate
- useful for prioritization
- useful for identifying which records need human or ChatGPT review first

## Recommended Next Step
Use this draft in one of two ways:
1. review only the non-`keep_other_by_policy` cases first
2. send the 16 ChatGPT batches for full structured annotation and compare the distribution against this draft

## Practical Value
This draft already narrows the expensive review set:
- focus review first on `33` records
  - `11 recoverable_now`
  - `21 recoverable_with_context`
  - `1 taxonomy_gap`

That is much faster than starting from all `400` records without any triage.

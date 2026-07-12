# Phase E.8.3 — Clean Residual Re-Sampling

## Goal
Create a second audit sample from the occupational residual after removing the shadow macro-class `non_role_recruiting_entry`.

## Why this matters
The first audit sample (`v1`) still contained recruiting placeholders and generic application entries.
That polluted the measurement of the true occupational residual.

This second sample is built from:
- `data/jobs/jobs_titled_en_recovery_v57_non_role_shadow.jsonl`

where:
- `classification_status == non_role` has already been separated in shadow
- only the remaining occupational `other` rows are sampled

## Clean residual baseline
- source dataset: `data/jobs/jobs_titled_en_recovery_v57_non_role_shadow.jsonl`
- occupational `other` rows: `35,493`
- removed non-role slice: `563`

## Outputs
- sample: `experiments/residual_audit/reports/residual_audit_sample_v2_clean.jsonl`
- manifest: `experiments/residual_audit/reports/residual_audit_manifest_v2_clean.json`
- batch index: `experiments/residual_audit/reports/chatgpt_batches_v2_clean_index.json`
- batch folder: `experiments/residual_audit/reports/chatgpt_batches_v2_clean/`

## Recommended next use
Use the same:
- `experiments/residual_audit/chatgpt_annotation_prompt.md`
- `experiments/residual_audit/annotation_schema.json`

but annotate `v2_clean`, not `v1`.

## Expected benefit
This second audit should measure the composition of the real occupational residual more cleanly:
- recoverable now
- recoverable with context
- taxonomy gap
- keep other by policy
- residual noise still present after non-role filtering

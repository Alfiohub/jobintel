# Phase E.8 — LLM Residual Audit Setup

## Goal
Prepare a residual audit package so ChatGPT can act as a structured annotator on a reproducible sample of the current `other` residual.

## Why this step
The current system is architecturally stable, but the main open problem is still the size and composition of the residual:
- official current `other`: `35,952`

Before choosing the next major investment, we need a better estimate of how much of that residual is:
- recoverable now
- recoverable only with richer context
- blocked by taxonomy
- correct to keep in `other`
- pure noise

## Package contents
- sample file: `experiments/residual_audit/reports/residual_audit_sample_v1.jsonl`
- manifest: `experiments/residual_audit/reports/residual_audit_manifest_v1.json`
- schema: `experiments/residual_audit/annotation_schema.json`
- prompt template: `experiments/residual_audit/chatgpt_annotation_prompt.md`

## Sample design
- source dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- population: rows where `classification_status == other`
- sample size: `400`
- random seed: `42`

## Included evidence per record
Each sample record includes:
- `title_raw`
- `title_clean`
- `company_name`
- `url`
- `employment_type`
- `seniority`
- location fields
- `skills`
- `departments`
- `description_excerpt`
- `responsibilities_excerpt`
- `requirements_excerpt`

This is enough for ChatGPT to behave like a structured human reviewer, not a blind title-only guesser.

## Intended annotation buckets
- `recoverable_now`
- `recoverable_with_context`
- `taxonomy_gap`
- `keep_other_by_policy`
- `noise_or_non_role`

## Recommended workflow
1. feed the schema and prompt to ChatGPT first
2. then provide records from `residual_audit_sample_v1.jsonl` in manageable batches
3. collect structured JSON annotations
4. aggregate the label distribution
5. use that distribution to decide the next strategic investment

## What this does not do
- it does not modify production
- it does not auto-promote rules
- it does not replace human judgment on final promotions

## Expected outcome
This step should turn the residual from an intuition problem into a measurable composition problem.

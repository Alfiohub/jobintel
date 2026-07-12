# Residual Audit Package

This folder prepares a structured audit package for the current `other` residual.

## Goal
Create a reproducible sample that can be reviewed by a human or by ChatGPT acting as a structured annotator.

## Outputs
- `reports/residual_audit_sample_v1.jsonl`
- `reports/residual_audit_manifest_v1.json`
- `annotation_schema.json`
- `chatgpt_annotation_prompt.md`

## Current Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- target population: rows with `classification_status == other`

## Usage
Build the package:

```bash
uv run python -m experiments.residual_audit.build_llm_audit_package
```

Then use:
- `reports/residual_audit_sample_v1.jsonl` as the annotation set
- `annotation_schema.json` as the output contract
- `chatgpt_annotation_prompt.md` as the instruction template

## Notes
- This package is shadow-only and does not modify the official classifier.
- The sample is reproducible through a fixed random seed.

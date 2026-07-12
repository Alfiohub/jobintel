# Title Context Layer

Shadow-only experiment space for Chapter 11.

## Purpose
Use job-ad context to review titles that remain ambiguous after:
- official title rules
- semantic title-only reviewer

## Initial scope
- `Onboarding Specialist`
- `Implementation Engineer`
- `Partner Manager`
- later: `Producer`, `Designer`, `Operations Analyst`

## Inputs
- `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- `data/jobs/jobs_extracted_en.jsonl`

## Principle
- no direct production mapping
- no silent override of official rules
- context is reviewer evidence only

## Planned modules
- `build_context_join.py`
- `score_context_signals.py`
- `review_hybrid_candidates.py`
- `refine_hybrid_policy.py`
- `shadow_context_rules.py`
- `run_shadow_context_batch.py`

## Run
```bash
uv run python -m experiments.title_context_layer.build_context_join
uv run python -m experiments.title_context_layer.score_context_signals
uv run python -m experiments.title_context_layer.review_hybrid_candidates
uv run python -m experiments.title_context_layer.refine_hybrid_policy
uv run python -m experiments.title_context_layer.run_shadow_context_batch
```

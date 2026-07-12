# Phase E.16 — Engine Hardening v1

## Goal
Apply the minimum engine-level hardening needed before building an orchestrator.

## Changes Applied
- promoted `non_role_recruiting_entry` into the official title taxonomy
- added explicit title rules for common recruiting-placeholder patterns:
  - `general application`
  - `open application`
  - `talent community`
  - `talent pool`
  - `future opportunities`
  - `expression of interest`
  - `don't see what you're looking for`
- introduced explicit `classification_status = non_role`
- preserved downstream compatibility by treating `non_role_recruiting_entry` as excluded in indexed output via `title_is_other = true`
- added `top_non_role_titles` to title-stage and eval reports
- standardized context-lane metadata with:
  - `lane_type`
  - `target_label`
  - `target_family`
  - `concentration`
  - `risk_level`
- made `experiments/` importable as a Python package so experiment scripts can be run as modules

## Core Files Updated
- `src/jobintel_next/domain/models/contracts.py`
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/classifier.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `src/jobintel_next/pipelines/titles/run.py`
- `src/jobintel_next/pipelines/titles/eval.py`
- `src/jobintel_next/pipelines/indexed/io.py`
- `src/jobintel_next/pipelines/indexed/run.py`

## Experiment Utilities Added
- `experiments/title_context_layer/report_utils.py`
- `experiments/__init__.py`
- `experiments/title_context_layer/__init__.py`
- `experiments/title_semantic_layer/__init__.py`

## Updated Validation
- title-stage / eval / indexed / CLI subset tests: `79 passed`
- command used:
  - `uv run pytest tests/pipelines/test_titles_stage_step12.py tests/pipelines/test_titles_eval_step13.py tests/pipelines/test_indexed_stage_step14.py tests/test_cli_titles_step12.py`

## Updated Context-Lane Artifacts
Re-generated as modules with standardized metadata:
- `experiments/title_context_layer/reports/phase_e15_account_manager_scoring_v1.json`
- `experiments/title_context_layer/reports/phase_e15_partner_lane_refinement_v1.json`
- `experiments/title_context_layer/reports/phase_e15_partner_lane_shadow_batch_v1.json`

## Practical Effect
The engine is still conservative, but now it is more orchestrable:
- non-role recruiting placeholders are first-class instead of leaking into plain `other`
- lane reports now carry explicit metadata for ranking and governance
- concentration and risk are standardized instead of inferred ad hoc
- experiment scripts can be called consistently with `python -m ...`

## Remaining Nice-to-Have
- add a shared markdown renderer for standardized lane reports
- decide whether to expose `non_role` separately in retrieval filters instead of only via `normalized_title`
- backfill older JSON reports only if they are needed for comparison

## Recommendation
- `engine_hardening_sufficient_for_orchestrator_v1`

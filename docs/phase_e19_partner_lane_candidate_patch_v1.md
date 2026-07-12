# Phase E.19 — Partner Lane Candidate Patch v1

## Goal
Implement the partner-lane context rule inside the official title-stage surface and validate it as far as possible in the current workspace.

## Implementation
Official context rule added in:
- `src/jobintel_next/pipelines/titles/context_rules.py`
- `src/jobintel_next/pipelines/titles/run.py`

Behavior:
- runs only after title-only classification returns `other`
- requires partner-lane title family
- requires partner-commercial department evidence
- requires at least two commercial context signals
- blocks client/provider/clinical/education contexts

## Validation
Tests passed:
- `uv run pytest tests/pipelines/test_titles_stage_step12.py tests/pipelines/test_titles_eval_step13.py tests/pipelines/test_indexed_stage_step14.py tests/test_cli_titles_step12.py`
- result: `81 passed`

Additional explicit tests added:
- positive partner-lane context promotion
- blocked partner-lane negative case

## Benchmark status
The full materialized rerun to `v66` was completed successfully after freeing disk space.

Artifacts:
- `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`
- `docs/title_recovery_pass_v66_partner_lane_candidate/title_stage_step12.json`
- `docs/title_recovery_pass_v66_partner_lane_candidate/title_eval_step13.json`

Official rerun result against `v64`:
- baseline `other` in `v64`: `35,273`
- `v66 other`: `35,255`
- official partner-lane matches: `18`
- official delta: `-18`
- `matched`: `45,399 -> 45,417`
- `non_role`: unchanged at `339`

## Streaming validation against `v64`
The earlier streaming validation remains useful as a pre-benchmark check and matched the full rerun exactly:
- projected partner-lane matches: `18`
- projected `other` after candidate rule: `35,255`
- projected delta: `-18`

Streaming eval artifact:
- `experiments/title_context_layer/reports/phase_e15_partner_lane_candidate_streaming_eval_v1.json`

## Interpretation
This candidate patch is stricter than the earlier shadow lane:
- shadow validated lane on `v64`: `-27`
- official candidate patch streaming eval: `-18`

That means:
- the rule is not overbroad
- but it is leaving some previously promotable shadow cases on the table
- this is a precision-first candidate, not a maximal-coverage candidate

## Decision
- `candidate_patch_benchmarked_ready_for_review`

## Recommended next step
One of these two:
1. accept this stricter production candidate as precision-first
2. do one final tuning pass only if recovering the missing `9` shadow cases is worth the added risk

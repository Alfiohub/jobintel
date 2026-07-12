# Phase E.19 — Partner Lane Acceptance v1

## Goal
Close the first production-candidate review for the `partner_lane` context rule after full benchmark validation.

## Decision
- `accepted_as_precision_first_production_candidate`

## Baseline
- previous official baseline: `data/jobs/jobs_titled_en_recovery_v64_non_role_official.jsonl`
- candidate benchmark dataset: `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`

## Official benchmark result
- `rows_total`: `81,011`
- `v64 other`: `35,273`
- `v66 other`: `35,255`
- delta `other`: `-18`
- `v64 matched`: `45,399`
- `v66 matched`: `45,417`
- delta `matched`: `+18`
- `non_role`: unchanged at `339`

## Rule result
- official rule id: `ctx_partner_lane_v1`
- total official matches: `18`
- target label: `account_manager`
- target family: `sales`

## Why this is accepted
- full rerun benchmark completed successfully
- benchmark exactly matches the earlier streaming validation
- the rule remains narrow and partner-only
- blocked contexts remain explicitly excluded
- the rule improves coverage without changing `non_role`

## Known limitation
This production candidate is stricter than the earlier shadow lane:
- shadow delta on `v64`: `-27`
- official candidate delta on `v64`: `-18`

Interpretation:
- the official rule is precision-first
- some shadow-promotable cases are still left in `other`
- this is acceptable for the first production-candidate cut

## Operational conclusion
Treat `v66` as the current operating baseline for the next recovery cycle.

Next work should not retune this rule immediately unless one of these happens:
- audit shows missed partner cases are materially valuable
- a second partner-lane refinement can recover misses without broadening risk

## Recommended next step
- return to orchestrator-driven prioritization from the new `v66` baseline

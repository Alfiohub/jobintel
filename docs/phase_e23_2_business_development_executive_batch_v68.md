# Phase E.23.2 — Business Development Executive Batch v68

## Goal
Test a narrow title-only production patch for `Business Development Executive` variants.

## Patch
Added rule in `src/jobintel_next/pipelines/titles/rules.py`:
- `sales_business_development_executive_v68`
- pattern: `(?:federal\s+|iso\s+)?business development executive`
- target: `account_executive / sales`

## Validation
Tests passed:
- `88 passed`

## Benchmark
- baseline dataset: `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`
- output dataset: `data/jobs/jobs_titled_en_recovery_v68_bd_executive_batch.jsonl`
- eval dir: `docs/title_recovery_pass_v68_bd_executive_batch`

## Result
- `v66 other`: `35,255`
- `v68 other`: `35,236`
- delta `other`: `-19`
- `v66 matched`: `45,417`
- `v68 matched`: `45,436`
- rule hits: `19`

## Interpretation
This lane is clean and behaves exactly as expected:
- narrow title family
- consistent commercial sales interpretation
- no spillover beyond the reviewed executive subset

## Decision
- `business_development_executive_batch_validated`

## Recommended next step
- keep this rule
- then return to the prioritized queues rather than expanding `business_development` broadly

# Phase E.11.1 — Context Join v1

## Goal
Materialize the first `title + context` working set on top of the `v58` residual, using the context-first clusters selected in Phase E.11.

## Input
- titled residual base: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- extracted source: `data/jobs/jobs_extracted_en.jsonl`

## Output
- joined working set: `experiments/title_context_layer/reports/phase_e11_context_join_v1.jsonl`
- summary: `experiments/title_context_layer/reports/phase_e11_context_join_v1_summary.json`
- customer-success candidate subset: `experiments/title_context_layer/reports/phase_e11_customer_success_candidates_v1.jsonl`

## Join Size
- joined rows total: `280`

## Counts By Cluster
- `customer_success_manager`: `118`
- `account_manager`: `65`
- `project_manager`: `97`

## Pattern Notes
### `customer_success_manager`
- `Onboarding Specialist`: `31`
- `Client Retention Specialist`: `7`
- `Customer Adoption & Success`: `2`
- `Service Enablement Manager, CX`: `1`
- broad `Engagement Manager` capture: `77`

### `account_manager`
- `Partner Development Manager`: `31`
- `Partner Growth Manager`: `12`
- `Client Partnership Specialist`: `6`
- `Partner Director`: `5`
- `Provider Engagement Specialist`: `4`

### `project_manager`
- `Project Engineer`: `76`
- `Professional Services Manager`: `10`
- `Delivery Excellence Manager`: `4`
- `Portfolio Management`: `4`

## Reading
The join confirms that the context lane has real mass on the official residual.

But it also reveals a necessary refinement before scoring:
- `customer_success_manager` is viable, but the current `Engagement Manager` capture is too broad and should be narrowed before a pilot rule is drafted
- `account_manager` already looks like a good reviewer-first cluster
- `project_manager` is currently dominated by `Project Engineer`, which is likely too engineering-heavy to mix with service-delivery titles in one context gate

## Recommendation
- move first on the `customer_success_manager` subset, but narrow it to onboarding / adoption / retention forms before scoring
- split `project_manager` into:
  1. services/delivery titles
  2. engineering project titles
- keep `account_manager` in reviewer-first mode for a second pass

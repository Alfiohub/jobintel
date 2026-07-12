# Phase E.11.2 — Context Refinement v1

## Goal
Refine the first `E.11.1` context working set into operational subgroups before any shadow scoring or context-gated rule design.

## Input
- joined working set: `experiments/title_context_layer/reports/phase_e11_context_join_v1.jsonl`

## Output
- refinement JSON: `experiments/title_context_layer/reports/phase_e11_cluster_refinement_v1.json`
- customer-success promotable subset: `experiments/title_context_layer/reports/phase_e11_customer_success_promotable_v1.jsonl`
- customer-success review-only subset: `experiments/title_context_layer/reports/phase_e11_customer_success_review_only_v1.jsonl`
- project services subset: `experiments/title_context_layer/reports/phase_e11_project_services_v1.jsonl`
- project engineering subset: `experiments/title_context_layer/reports/phase_e11_project_engineering_v1.jsonl`
- account partner subset: `experiments/title_context_layer/reports/phase_e11_account_partner_v1.jsonl`
- account client subset: `experiments/title_context_layer/reports/phase_e11_account_client_v1.jsonl`

## Refinement Result
### `customer_success_manager`
- promotable subset: `40`
- review-only subset: `72`
- excluded subset: `6`
- decision: `ready_for_shadow_scoring_on_promotable_subset`

Top promotable titles:
- `Onboarding Specialist`: `13`
- `Client Retention Specialist (Remote)`: `5`
- `SaaS Onboarding Specialist`: `2`
- `Customer Onboarding Specialist`: `2`
- `Manager, Customer Adoption & Success (EMEA)`: `2`

Reading:
- the onboarding / adoption / retention lane is now separated cleanly enough for the next shadow pilot
- broad `Engagement Manager` variants remain too mixed and stay reviewer-only

### `project_manager`
- services/delivery subset: `18`
- engineering-delivery subset: `79`
- decision: `split_before_any_context_gate`

Reading:
- `Project Engineer` dominates this cluster and should not be mixed with services delivery
- the promotable future lane here is the services/delivery subset, not the engineering subset

### `account_manager`
- partner subset: `49`
- client subset: `16`
- decision: `reviewer_first_keep_context`

Reading:
- the cluster is commercially coherent, but still too broad for an immediate gate
- next useful step is reviewer-based split inside partner-growth vs client-strategy work

## Recommendation
- `E.11.3` should target only `phase_e11_customer_success_promotable_v1.jsonl`
- do not score or gate the broad `Engagement Manager` subset yet
- keep `account_manager` and `project_manager` in reviewer-first mode until their subclusters are tighter

# Phase E.17 — Residual Recovery Orchestrator v1

## Goal
Turn the existing residual-recovery discipline into a repeatable orchestrated workflow.

## Baseline
- dataset: `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`
- rows_total: `81011`
- other: `35581`

## Lane Status
- non_role: `ready_for_official_rerun`
- attack_now: `active`
- recoverable_with_context: `active`
- taxonomy_gap: `active`

## Non-Role
- candidate_count_shadow: `563`
- from_other_shadow: `459`
- from_matched_shadow: `104`
- delta_other_shadow: `-459`

## Top Attack-Now Candidates
- `software_engineer` | projected `2307` | sample `26`
- `engineering_manager` | projected `710` | sample `8`
- `business_development_manager` | projected `621` | sample `7`
- `sales_director` | projected `532` | sample `6`
- `financial_analyst` | projected `444` | sample `5`
- `it_support_specialist` | projected `444` | sample `5`
- `mechanical_engineer` | projected `444` | sample `5`
- `systems_administrator` | projected `444` | sample `5`

## Top Context Candidates
- `partner_lane_context_lane` -> `account_manager/sales` | status `ready_for_production_candidate_review` | delta `-27` | risk `medium-low`
- `account_manager_context_lane` -> `account_manager/sales` | status `not_ready_for_production_candidate_review_yet` | delta `-19` | risk `medium`

## Taxonomy Candidates
- `quantitative_researcher` | family `finance` | status `ready_for_future_taxonomy_patch_candidate`
- `credit_analyst` | family `finance` | status `ready_for_future_taxonomy_patch_candidate`
- `market_access_director` | family `None` | status `deferred_pending_family_expansion`

## Recommended Execution Order
- step 1: `official_non_role_rerun` | Cheap structural cleanup before any further residual ranking.
- step 2: `partner_lane_rule_proposal` | Best validated recoverable_with_context lane so far.
- step 3: `next_attack_now_batch` | Continue title-only recovery only on top ranked narrow clusters.
- step 4: `taxonomy_patch_followup_rules` | Quantitative researcher and credit analyst now have official taxonomy support.

## Recommendation
- `orchestrator_v1_ready`

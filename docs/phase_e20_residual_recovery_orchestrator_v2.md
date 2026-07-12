# Phase E.20 — Residual Recovery Orchestrator v2

## Goal
Rerun the orchestrator on the current baseline after official non-role promotion and partner-lane acceptance.

## Baseline
- dataset: `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`
- rows_total: `81011`
- other: `35255`

## Lane Status
- non_role: `completed_official`
- attack_now: `active`
- recoverable_with_context: `active`
- taxonomy_gap: `active`

## Non-Role
- candidate_count_shadow: `563`
- from_other_shadow: `459`
- from_matched_shadow: `104`
- delta_other_shadow: `-459`
- official_delta_other: `-308`

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
- `partner_lane_context_lane` -> `account_manager/sales` | status `accepted_as_precision_first_production_candidate` | shadow `-27` | official `-18` | risk `medium-low`
- `account_manager_context_lane` -> `account_manager/sales` | status `not_ready_for_production_candidate_review_yet` | shadow `-19` | risk `medium`

## Taxonomy Candidates
- `quantitative_researcher` | family `finance` | status `ready_for_future_taxonomy_patch_candidate`
- `credit_analyst` | family `finance` | status `ready_for_future_taxonomy_patch_candidate`
- `market_access_director` | family `None` | status `deferred_pending_family_expansion`

## Recommended Execution Order
- step 1: `rerank_attack_now_from_v66` | Non-role and partner-lane gains are already absorbed into the current baseline.
- step 2: `reopen_next_context_lane` | Partner lane is now accepted; the next context opportunity should be selected from the remaining residual.
- step 3: `taxonomy_patch_followup_rules` | Quantitative researcher and credit analyst now have official taxonomy support but still need exploitation rules.
- step 4: `refresh_residual_audit_only_if_signal_shifts` | A new broad audit is not needed immediately; reuse the existing discipline unless the residual profile materially changes.

## Recommendation
- `orchestrator_v2_ready`

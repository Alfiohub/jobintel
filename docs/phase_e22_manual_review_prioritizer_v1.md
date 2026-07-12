# Phase E.22 — Manual Review Prioritizer v1

## Goal
Turn the open-set router manual-review mass into ordered actionable queues.

- input dataset: `data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl`
- manual_review_total: `35150`

## Attack-Now Queue
- `business_development_manager` | count `397` | titles `278` | companies `180` | priority `4.57`
- `financial_analyst` | count `159` | titles `122` | companies `118` | priority `2.19`
- `sales_director` | count `145` | titles `117` | companies `72` | priority `2.05`
- `software_engineer` | count `75` | titles `47` | companies `28` | priority `1.35`
- `engineering_manager` | count `31` | titles `30` | companies `16` | priority `0.91`
- `mechanical_engineer` | count `14` | titles `14` | companies `7` | priority `0.65`
- `it_support_specialist` | count `10` | titles `5` | companies `10` | priority `0.55`
- `systems_administrator` | count `5` | titles `5` | companies `5` | priority `0.35`

## Recoverable-With-Context Queue
- `project_manager` | count `122` | titles `84` | companies `50` | priority `1.456`
- `account_manager` | count `108` | titles `61` | companies `46` | priority `1.344`
- `customer_success_manager` | count `31` | titles `17` | companies `18` | priority `0.728`

## Long-Tail Policy
- `do_not_work_cluster_by_cluster_without_semantic_clustering`

## Recommendation
- first attack_now target: `business_development_manager`
- first context target: `project_manager`

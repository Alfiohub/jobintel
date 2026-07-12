# Phase E.21 — Open-Set Residual Router v1

## Goal
Replace final `other` with explicit routed buckets over the current `v66` baseline.

## Input
- dataset: `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`

## Output
- routed dataset: `data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl`

## Counts By Route Status
- `matched_role`: `45417`
- `manual_review`: `35150`
- `non_role`: `339`
- `taxonomy_gap`: `105`

## Counts By Route Lane
- `matched`: `45417`
- `long_tail`: `34053`
- `attack_now`: `836`
- `non_role`: `339`
- `recoverable_with_context`: `261`
- `taxonomy_gap`: `105`

## Top Suggested Targets
- `software_engineer`: `10458`
- `account_executive`: `3609`
- `marketing_specialist`: `2539`
- `account_manager`: `2106`
- `product_manager`: `1819`
- `operations_specialist`: `1395`
- `project_manager`: `1283`
- `sales_engineer`: `1087`
- `engineering_manager`: `1043`
- `business_development_representative`: `933`

## Recommendation
- first: `attack_now_manual_review_queue`
- second: `recoverable_with_context_manual_review_queue`
- third: `taxonomy_gap_queue`

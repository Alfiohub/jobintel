# Phase E.15.3 — Account Manager Context Lane Formal Review

## Goal
Decide whether the `account_manager` context lane is ready for production-candidate drafting after the first shadow batch on `v61`.

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`
- baseline `other`: `35,581`

## Scoring summary
- joined rows: `65`
- promotable: `19`
- review-only: `40`
- excluded: `6`
- scoring decision: `ready_for_account_manager_shadow_batch`

## Shadow result
- output dataset: `data/jobs/jobs_titled_en_recovery_v62_account_manager_shadow.jsonl`
- shadow matches added: `19`
- other after shadow: `35,562`
- delta other: `-19`

## What matched well
Titles with the cleanest commercial-partnership signal:
- `Partner Growth Manager`
- `Partner Development Manager - Mandarin Speaker`
- `Partner Development Manager, Financial Partnership Capabilities`
- `Partner Development Manager, Global Networks`
- `Strategic Partner Director`
- `Senior Partner Development Manager`

Common evidence patterns:
- department in `Sales`, `Partnerships`, or `Partner Development`
- pipeline / bookings / revenue language
- named partner portfolios
- explicit partner growth / partner development ownership
- go-to-market and commercial expansion responsibilities

## What stayed review-only
The lane is still mixed in these clusters:
- `Strategic SI Partner Development Manager`
- `Regional Client Partnership Specialist, Educational Services`
- `Manager, Client Strategy`
- `Client Strategist`
- `Partner Director, IBM - APAC`

Reason:
- these cases are often sales-adjacent and promising
- but they blend alliances, client strategy, education staffing, provider / service terminology, or broader partnership operations
- forcing them today would widen the gate too early

## Concentration risk
The promotable subset is not evenly distributed.

By company:
- `connecteam`: `8`
- `stripe`: `3`
- `affirm`: `2`
- `lightspeedhq`: `2`
- others: singletons

By title:
- `Partner Growth Manager`: `10`
- `Senior Partner Development Manager`: `2`
- all other promotable titles: singletons

Reading:
- the lane is real
- but the current promotable subset is concentrated in one very strong title pattern: `Partner Growth Manager`

## Formal decision
- decision: `not_ready_for_production_candidate_review_yet`

## Why
The lane is stronger than the previous customer-success pilot, but still not broad enough for a production-candidate gate.

Concrete reasons:
1. shadow delta is only `-19`
2. promotable subset is concentrated in one title family
3. review-only inventory (`40`) is still much larger than promotable (`19`)
4. the best cases are very likely promotable, but the lane as a whole is not yet stable enough

## What this means
Do not draft a production rule yet for broad `account_manager` context gating.

Instead, split the lane into narrower sub-lanes:
- `Partner Growth Manager`
- `Partner Development Manager`
- optionally later: `Client Strategy`

## Recommended next step
- `E.15.4 — Narrow Partner Growth / Partner Development Shadow Refinement`

Focus only on:
- `Partner Growth Manager`
- `Partner Development Manager`
- `Senior Partner Development Manager`
- `Strategic Partner Director`

Keep out for now:
- `Client Strategist`
- `Manager, Client Strategy`
- `Regional Client Partnership Specialist, Educational Services`
- `Strategic SI Partner Development Manager`

## Recommendation
- `shadow_signal_real_but_needs_narrower_partner_lane`

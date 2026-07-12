# Phase E.15.5 — Partner Lane Formal Review

## Goal
Decide whether the narrowed partner-only `account_manager` context lane is ready for production-candidate drafting.

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`
- baseline `other`: `35,581`

## Narrow partner lane
Source:
- refinement input: `phase_e15_account_manager_scoring_v1.json`
- refinement output: `phase_e15_partner_lane_refinement_v1.json`

Counts:
- source promotable: `19`
- source review-only: `40`
- partner-lane promotable: `27`
- partner-lane review-only: `3`
- partner-lane excluded: `35`

## Shadow result
- output dataset: `data/jobs/jobs_titled_en_recovery_v63_partner_lane_shadow.jsonl`
- shadow matches added: `27`
- other after shadow: `35,554`
- delta other: `-27`

## What matched well
Titles:
- `Core Partner Development Manager - UKI`
- `Partner Growth Manager`
- `Strategic SI Partner Development Manager`
- `Senior Technology Partner Development Manager`
- `Partner Development Manager`
- `Senior Partner Development Manager`
- `Partner Director, IBM - APAC`
- `Strategic Partner Director`
- `Regional Partner Director - Northeast`

Shared evidence:
- departments in `Sales`, `Partner Development`, `Alliances`, or `Partnerships`
- pipeline / bookings / revenue language
- partner portfolio ownership
- co-sell / GTM / joint business plan language
- executive partner relationship ownership

## Concentration check
By company:
- `hubspotjobs`: `7`
- `stripe`: `4`
- `fivetran`: `3`
- `klaviyo`: `3`
- `lightspeedhq`: `3`
- `affirm`: `2`
- others: singletons

By title:
- `Core Partner Development Manager - UKI`: `4`
- `Partner Growth Manager`: `3`
- `Strategic SI Partner Development Manager`: `3`
- `Senior Technology Partner Development Manager`: `3`
- several additional partner-development variants: `1–2` each

Reading:
- still some concentration, but no longer dominated by one company or one exact title
- the lane now looks like a real commercial-partnership cluster, not a one-off artifact

## Residual review-only cases
Only `3` remain review-only:
- `RippleX Partner Director`
- `Partner Development Manager (Banks)`
- `Affiliate Partner Growth Manager (Fluent in Mandarin)`

Reason:
- missing or weak partner/sales department signal
- not enough to block the lane overall

## Formal decision
- decision: `ready_for_production_candidate_review`

## Why
1. the narrowed lane improves from `-19` to `-27`
2. promotable cases now substantially outnumber review-only (`27` vs `3`)
3. the matched set spans multiple companies and multiple partner-growth / partner-development title variants
4. exclusions are explicit and understandable

## Risk level
- `medium-low`

Main risk:
- overmatching broader alliances/client-strategy titles if the future rule is widened beyond the current partner-only subset

## Constraint for future patch
A production-candidate rule must stay limited to:
- partner growth / partner development / partner director style titles
- partner/sales/alliances department or equivalent partner-commercial context
- explicit commercial signals such as pipeline, bookings, revenue, GTM, portfolio growth

Do not include yet:
- `Client Strategist`
- `Manager, Client Strategy`
- `Regional Client Partnership Specialist, Educational Services`
- broader provider/client engagement roles

## Recommendation
- `ready_to_draft_partner_lane_context_rule`

## Next step
- `E.15.6 — Partner Lane Production-Candidate Rule Proposal`

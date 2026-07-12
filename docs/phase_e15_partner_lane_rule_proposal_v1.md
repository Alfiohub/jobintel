# Phase E.15.6 — Partner Lane Production-Candidate Rule Proposal v1

## Goal
Draft a production-candidate `title + context` rule for the narrowed partner-commercial lane inside the broader `account_manager` context cluster.

## Baseline
- current official baseline dataset: `data/jobs/jobs_titled_en_recovery_v64_non_role_official.jsonl`
- rows_total: `81,011`
- other baseline: `35,273`
- non_role baseline: `339`

## Scope
In scope:
- partner-commercial growth / development / director titles

Out of scope:
- client strategy
- provider engagement
- educational partnerships
- generic alliances titles without commercial evidence

## Proposed target
- normalized title: `account_manager`
- role family: `sales`

## Why this is plausible
Validation source:
- formal review: `phase_e15_partner_lane_formal_review_v1.json`
- shadow batch: `phase_e15_partner_lane_shadow_batch_v1.json`

Signal:
- promotable partner-lane cases: `27`
- review-only: `3`
- excluded: `35`
- shadow delta on validated lane: `-27`
- risk: `medium-low`

## Rule design principles
- title-first system remains unchanged
- context-gated rule runs only after title normalization would otherwise produce `other`
- no context-only classification
- no broad alliances/client-strategy promotion
- gate must stay partner-only and commercial

## Shared trigger
A partner-lane rule may be evaluated only if all are true:
- `classification_status == other` after title-only pass
- `title_clean` matches a partner-lane title pattern
- extracted context is available by `url`
- commercial partner evidence crosses threshold

## Title gate
Keep the title gate narrow.

In scope title families:
- `Partner Growth Manager`
- `Partner Development Manager`
- `Senior Partner Development Manager`
- `Core Partner Development Manager`
- `Strategic SI Partner Development Manager`
- `Senior Technology Partner Development Manager`
- `Partner Director`
- `Strategic Partner Director`
- `Regional Partner Director`

Not yet in scope:
- `Client Strategist`
- `Manager, Client Strategy`
- `Client Partnership Specialist`
- bare `Partnerships Manager`
- generic `Alliances Manager`

## Context evidence required
Require at least `2` strong partner-commercial signals, for example:
- `pipeline`
- `bookings`
- `revenue`
- `go-to-market`
- `portfolio growth`
- `merchant acquisition`
- `co-sell`
- `joint business plan`
- `partner relationships`
- `strategic partnerships`

Supportive department signals:
- `sales`
- `partner development`
- `alliances`
- `partnerships`

## Exclusion signals
Do not map if broader non-commercial partnership signals dominate, for example:
- `client strategy`
- `provider`
- `patient`
- `clinical`
- `education`
- `district`

Do not map if partner context is weak and department evidence is absent.

## Promotion shape
Conceptual production shape:
- if title is in the partner-growth / partner-development / partner-director family
- and context has partner-commercial evidence >= threshold
- and blocked client/provider/education signals are absent
- map to `account_manager`

## Why not safe title-only
Titles like `Partner Director` or `Partner Development Manager` are still too cross-domain on their own.
The validated lane only became clean after narrowing by:
- partner-commercial department evidence
- revenue/pipeline/GTM language
- explicit exclusions for client/provider/education-heavy contexts

## Risk
- `medium-low`

Main risk:
- widening the gate beyond the partner-commercial subset and accidentally pulling in client-strategy or provider-engagement roles

## Recommended test strategy
Positive:
- partner growth portfolio ownership
- partner development with sales / alliances / partner-development department
- commercial partner roles with revenue / bookings / GTM language

Negative:
- client strategy
- client partnership specialist in education / services contexts
- provider engagement
- patient / clinical partnership roles
- generic partnership titles without commercial evidence

## Recommendation
- `ready_to_draft_partner_lane_context_patch_candidate`

The next correct step is:
- implement this rule in shadow form inside the official title pipeline surface
- add explicit positive/negative tests
- rerun benchmark and compare against `v64`

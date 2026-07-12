# Phase E.23.1 — Business Development IC Review v1

## Goal
Review the `business_development_individual_contributor` sub-lane and decide whether it is promotable as a single title-only batch.

## Source
- input dataset: `data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl`
- filtered queue:
  - `route_status = manual_review`
  - `route_lane = attack_now`
  - `suggested_target_label = business_development_manager`
  - `business_development_individual_contributor` title subset

## Headline
The IC subset is still not a single clean lane.
It splits into 5 distinct title buckets.

## Counts
- IC subset total: `76`
- unique titles: `51`
- unique companies: `35`

## Sub-buckets

### `executive`
- count: `19`
- examples:
  - `Business Development Executive`
  - `Federal Business Development Executive`
  - `Business Development Executive - DACH`
- decision:
  - `best_first_attack_now_candidate`
- reason:
  - title family is narrow and commercially consistent.

### `associate`
- count: `18`
- examples:
  - `Business Development Associate`
  - `Senior Business Development Associate`
- decision:
  - `possible_followup_attack_now`
- reason:
  - reasonably coherent, but still more title variation than executive.

### `lead`
- count: `17`
- examples:
  - `Business Development Lead`
  - `Business Development Lead - Manager, Launch`
  - `Cloud Alliances Business Development Lead`
- decision:
  - `not_title_only_clean`
- reason:
  - overlaps with partnerships, alliances, and technical BD.

### `associate_director`
- count: `13`
- examples:
  - `Associate Director, Business Development`
  - `Associate Director, Business Development, Maritime`
- decision:
  - `leadership_lane_not_ic`
- reason:
  - should not be mixed with pure IC recovery.

### `analyst`
- count: `9`
- examples:
  - `Analyst, Business Development`
  - `Business Development Analyst`
- decision:
  - `small_but_clean_followup`
- reason:
  - coherent but small.

## Decision
- do **not** patch the whole IC subset at once.
- the first narrow candidate worth testing is:
  - `business_development_executive`

## Recommended next step
- `E.23.2 — Business Development Executive Candidate Patch`

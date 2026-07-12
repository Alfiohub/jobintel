# Phase E.23 — Business Development Split v1

## Goal
Split the broad `business_development_manager` manual-review queue into narrower operational sub-lanes.

## Source
- input dataset: `data/jobs/jobs_titled_en_recovery_v67_open_set_router.jsonl`
- filtered queue:
  - `route_status = manual_review`
  - `route_lane = attack_now`
  - `suggested_target_label = business_development_manager`

## Headline
The `397`-row queue is not a single clean cluster.
It splits into multiple distinct families with different recovery paths.

## Sub-lanes

### `business_development_leadership`
- count: `144`
- unique titles: `85`
- unique companies: `60`
- examples:
  - `Manager, Business Development`
  - `Director, Business Development`
  - `Business Development Director, Content Ops`
  - `Life Sciences Business Development Director`
- decision:
  - `review_first_then_possible_attack_now`
- reason:
  - commercially coherent but still broad across verticals and seniority.

### `corporate_development`
- count: `83`
- unique titles: `60`
- unique companies: `50`
- examples:
  - `Corporate Development Manager`
  - `Senior Analyst, Strategy & Corporate Development`
  - `VP, Corporate Development`
  - `Head of M&A Integrations`
- decision:
  - `separate_lane_not_same_as_business_development`
- reason:
  - M&A / corp-dev cluster should not be forced into the same recovery lane.

### `business_development_generic`
- count: `70`
- unique titles: `60`
- unique companies: `53`
- examples:
  - `Business Development`
  - `Business Development Specialist`
  - `Business Development Coordinator`
  - `Business Development and Capture Manager`
- decision:
  - `too_broad_keep_split`
- reason:
  - generic and mixed; high overmatch risk.

### `business_development_individual_contributor`
- count: `59`
- unique titles: `39`
- unique companies: `29`
- examples:
  - `Business Development Associate`
  - `Business Development Executive`
  - `Analyst, Business Development`
- decision:
  - `best_first_candidate_inside_bd_cluster`
- reason:
  - narrower than leadership/corp-dev and more internally consistent.

### `technical_or_partnership_bd`
- count: `21`
- unique titles: `19`
- unique companies: `16`
- examples:
  - `Technical Business Development - Automotive`
  - `Business Development & Partnerships Lead`
  - `Cloud Alliances Business Development Lead`
- decision:
  - `recoverable_with_context_not_attack_now`
- reason:
  - overlaps with partnership/alliances lanes and needs context.

### `intern_low_signal`
- count: `20`
- unique titles: `15`
- unique companies: `10`
- examples:
  - `Business Development Intern`
  - `Partnerships & Business Development Intern`
  - `Business Development MBA Intern`
- decision:
  - `deprioritize`
- reason:
  - low-value/low-signal for current production recovery work.

## Decision
- do **not** patch `business_development_manager` as a single cluster.
- next correct move:
  - isolate `business_development_individual_contributor`
  - keep `corporate_development` separate
  - route `technical_or_partnership_bd` to context work

## Recommended next step
- `E.23.1 — Business Development IC Lane Review`

# Phase E.12.3 — Taxonomy Decision Draft v1

## Goal
Record the current taxonomy decision state for the finance-specialist candidates after proposal and residual validation.

## Inputs Considered
- `docs/phase_e12_taxonomy_gap_review_v1.md`
- `docs/phase_e12_finance_specialist_taxonomy_proposal_v1.md`
- `docs/phase_e12_finance_specialist_validation_v1.md`

## Decision Summary
### Approved as taxonomy candidates
- `quantitative_researcher` -> `finance`
- `credit_analyst` -> `finance`

### Deferred
- `market_access_director`

## Final Decisions

### 1. `quantitative_researcher`
Decision:
- `approve_candidate_label`

Why:
- coherent specialist finance role
- repeated across multiple companies
- validated on full residual with measured candidate count `92`
- poor fit to existing labels such as `financial_analyst` or `data_scientist`

Constraints:
- taxonomy-only approval for now
- no production rules in this phase
- future rule design must explicitly exclude cross-domain variants

Status:
- `ready_for_future_taxonomy_patch_candidate`

### 2. `credit_analyst`
Decision:
- `approve_candidate_label`

Why:
- coherent finance specialization
- validated on full residual with measured candidate count `28`
- closer to an official label candidate than to a generic remap into `financial_analyst`

Constraints:
- taxonomy-only approval for now
- no production rules in this phase
- future rule design must start from explicit title forms (`Credit Analyst`, `Credit Assessment`, `CMBS`) and exclude trader variants

Status:
- `ready_for_future_taxonomy_patch_candidate`

### 3. `market_access_director`
Decision:
- `defer`

Why:
- implies a broader family decision beyond the current taxonomy
- not acceptable as a simple label insertion under `sales` or `marketing`

Status:
- `deferred_pending_family_expansion`

## What This Decision Does Not Do
- does not modify `taxonomy.py`
- does not modify `rules.py`
- does not change production behavior
- does not auto-promote any titles out of `other`

## What This Decision Enables
- a future isolated taxonomy patch for:
  - `quantitative_researcher`
  - `credit_analyst`
- a later production-rule design phase only after that taxonomy patch is approved

## Recommendation
- `taxonomy_decision_state_established`

## Next Correct Step
If we continue on the taxonomy lane, the next step is:
- `E.12.4` draft the isolated taxonomy patch candidate for the two approved finance labels

If we switch back to recovery, the next best lane is:
- another title-only `attack_now` batch from the residual backlog

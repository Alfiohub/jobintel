# Phase 11.3 — Context-Gated Rule Proposal v1

## Goal
Define the first production-candidate `title + context` rules for ambiguous titles that cannot be resolved safely from title-only matching.

## Scope
In scope:
- `Onboarding Specialist`
- `Producer`

Out of scope:
- `Partner Manager`
- `Implementation Engineer`
- `Operations Analyst`
- `Designer`

Reason:
- only the two in-scope clusters show both strong dominant context and enough high-confidence examples to justify drafting future gated rules

## Baseline
- current official baseline dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows_total: `81,011`
- other baseline: `35,952`

## Rule Design Principles
- title-first system remains unchanged
- context-gated rules only run after title normalization would otherwise produce `other`
- no context-only classification
- no black-box promotion
- every context gate must be:
  - readable
  - auditable
  - testable
  - narrow

## Shared Hybrid Trigger
A context-gated rule may be evaluated only if all are true:
- `classification_status == other` after title-only pass
- `title_clean` matches the exact target title cluster
- extracted context is available by `url`
- context evidence crosses a minimum threshold

## Proposal A — `Onboarding Specialist`

### Proposed target
- normalized title: `customer_success_manager`
- role family: `customer_success`

### Why this is plausible
- cluster volume: `13`
- dominant context family: `customer_success`
- dominant share: `92.31%`
- high-confidence examples: `10`
- conflicts: `1` (`people_operations`)

### Title gate
- exact title family:
  - `Onboarding Specialist`
  - optional future expansion only after separate review:
    - `Customer Onboarding Specialist`
    - `Merchant Onboarding Specialist`

For v1 proposal, keep it to `Onboarding Specialist` only.

### Context evidence required
Require at least `2` strong customer-success signals, for example:
- `customer`
- `client`
- `merchant`
- `implementation`
- `onboarding`
- customer-facing product adoption language

### Exclusion signals
Do not map if strong HR/people signals dominate:
- `employee`
- `new hire`
- `hr`
- `hris`
- `employee lifecycle`

Do not map if compliance signals dominate:
- `kyc`
- `aml`
- `verification`
- `due diligence`

### Promotion shape
- not a broad regex
- a gated rule expressed conceptually as:
  - if title is `Onboarding Specialist`
  - and context has customer-success evidence >= threshold
  - and HR/compliance exclusions are absent
  - map to `customer_success_manager`

### Risk
- `medium-low`

### Why not safe title-only
- at least one observed example points to `people_operations`
- title-only would still overmatch HR/compliance onboarding cases

## Proposal B — `Producer`

### Proposed target
- normalized title: `content_producer`
- role family: `content`

### Why this is plausible
- cluster volume: `27`
- dominant context family: `content`
- dominant share: `96.3%`
- high-confidence examples: `13`
- conflicts: `1` (`software_engineering`, game-production style)

### Title gate
- exact title family:
  - `Producer`

For v1 proposal, do not expand to broader title variants automatically.

### Context evidence required
Require at least `2` content/media signals, for example:
- `content`
- `news`
- `broadcast`
- `creative`
- `video`
- `campaign`

### Exclusion signals
Do not map if game/software production signals dominate:
- `game`
- `jira`
- `scrum`
- `engineers`
- strong technical delivery / game studio production context

### Promotion shape
- if title is exactly `Producer`
- and content/media evidence >= threshold
- and game/software production exclusions are absent
- map to `content_producer`

### Risk
- `medium`

### Why not safe title-only
- naked `Producer` is historically ambiguous
- one observed cluster member clearly points to game/software production

## Why `Partner Manager` Is Deferred
- dominant family is `sales`
- but high-confidence evidence is still too thin
- title remains cross-domain enough that a future gated rule could still overmatch

Decision:
- keep reviewer-only for now

## Recommended Acceptance Gate Before Production Draft
Before either proposal becomes a real patch:
- run a targeted context audit on at least `20` examples where possible
- require dominant-family share >= `0.8`
- require at least `2` high-confidence examples for the promoted family
- require explicit exclusion tests for the main conflict family

## Recommended Test Strategy For Future Patch

### `Onboarding Specialist`
Positive:
- merchant/customer/platform onboarding context
- onboarding tied to customer adoption, implementation, or merchant setup

Negative:
- HR onboarding
- employee onboarding
- KYC/AML onboarding

### `Producer`
Positive:
- news/content/video/campaign producer context

Negative:
- game studio production
- technical production/project delivery
- bare producer without qualifying context

## Recommendation
- `ready_to_draft_context_gated_rules_for_review`

The next correct step is not immediate production merge.
The next correct step is:
- draft the production-candidate rule logic in shadow form
- define explicit context feature extraction
- write positive/negative scenario tests before touching official rules

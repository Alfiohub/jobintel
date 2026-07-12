# Phase 11.6 — Formal Review of Context-Gated Rule Candidates

## Scope
- `Onboarding Specialist` -> `customer_success_manager/customer_success`
- `Producer` -> `content_producer/content`

## Baseline
- official baseline dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows total: `81,011`
- other baseline: `35,952`

## Shadow Audit Input
- shadow output dataset: `data/jobs/jobs_titled_en_recovery_v56_context_shadow_v2.jsonl`
- shadow report: `experiments/title_context_layer/reports/shadow_context_batch_v2.json`

## Shadow Audit Result
- total shadow matches: `37`
- delta other in shadow: `-37`
- rule hits:
  - `ctx_onboarding_specialist_customer_success_v2`: `11`
  - `ctx_producer_content_v1`: `26`

## Candidate Review

### `Onboarding Specialist`
- verdict: `ready_for_production_candidate_review`
- target: `customer_success_manager/customer_success`
- matched in shadow: `11`
- kept out in shadow:
  - compliance-heavy onboarding (`Adyen`)
  - weaker client-service / operations onboarding (`Focus Financial`)
- representative positive matches:
  - `Cision` -> product onboarding, client objectives, software onboarding, adoption
  - `GlossGenius` -> customer transition to platform, implementation process, customer success / sales adjacency
  - `RxVantage` -> onboarding and supporting practices onto platform with long-term success language
- main risk:
  - SaaS/customer onboarding can still overlap with operations or implementation support
- review decision:
  - acceptable for a production-candidate patch only if accompanied by explicit negative tests on HR and compliance onboarding

### `Producer`
- verdict: `ready_for_production_candidate_review`
- target: `content_producer/content`
- matched in shadow: `26`
- kept out in shadow:
  - game/software producer (`2K`) correctly blocked by `game/jira/scrum/engineers`
- representative positive matches:
  - `TEGNA` -> news/broadcast/video context
  - `DEPT` -> content/creative/campaign context
  - `Eucalyptus` -> content/creative context
- main risk:
  - some creative/agency contexts can still drift into project delivery or technical production if the evidence set is widened later
- review decision:
  - strongest context-gated candidate currently available

## Auditability Check
- rules remain title-gated first
- context is only evaluated on `classification_status == other`
- evidence terms are explicit and inspectable
- exclusions are explicit and inspectable
- no context-only classification path exists

## Recommended Test Pack For Candidate Production Patch

### `Onboarding Specialist`
Positive:
- customer onboarding tied to platform adoption
- merchant onboarding tied to customer setup
- onboarding adjacent to customer success / sales / revops / implementation

Negative:
- HR onboarding
- employee onboarding / HRIS
- compliance onboarding with `kyc`, `aml`, `verification`, `due diligence`, `underwriting`
- weak client-service onboarding without clear product/platform signals

### `Producer`
Positive:
- content producer with `content`, `news`, `broadcast`, `creative`, `video`, `campaign`

Negative:
- game producer
- producer with `jira`, `scrum`, `engineers`
- technical delivery / software production context

## Decision
- `ready_for_candidate_patch_review`

## Recommendation
- close Chapter 11
- next step: prepare a production-candidate patch review, still conservative, for:
  - `Producer`
  - `Onboarding Specialist`
- do not include `Partner Manager` yet

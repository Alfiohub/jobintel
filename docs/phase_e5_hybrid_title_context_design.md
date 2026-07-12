# Capitolo 11 — Hybrid Title + Context Design

## Goal
Design a second-stage reviewer for titles that remain ambiguous after the official rule-based pipeline, using ad context from the job JSON without replacing the production classifier.

## Baseline
- current benchmark dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows_total: `81,011`
- other baseline: `35,952`
- current system state:
  - Chapters 1–10 closed
  - rule-based pipeline remains the production source of truth
  - semantic layer already exists as shadow reviewer

## Why Chapter 11 Is Needed
The remaining residual is no longer dominated by clean title-only clusters. A meaningful share of `other` is made of titles whose semantics depend on surrounding context.

Examples:
- `Onboarding Specialist`
- `Operations Analyst`
- `Partner Manager`
- `Sales Representative`
- `Producer`
- `Designer`
- `Implementation Engineer`

Title-only classification is unstable for these families because the same title string appears in different functions.

## Available Context Signals
Confirmed available in local datasets:

### From `data/jobs/jobs_cleaned_en.jsonl`
- `description_clean`
- `requirements_clean`
- `responsibilities_clean`
- `departments_raw`
- `company_name`
- `location_clean`

### From `data/jobs/jobs_extracted_en.jsonl`
- `skills`
- `seniority`
- `employment_type`
- `location_type`
- `tags`
- structured salary/location fields

### Present in titled outputs
The titled datasets already retain lightweight context fields such as:
- `skills`
- `seniority`
- `employment_type`
- `tags`
- `company_name`

For richer disambiguation, the hybrid layer should join `jobs_titled_*` rows back to `jobs_extracted_en.jsonl` by `url`.

## Context Audit: What The Data Already Shows

### 1. `Onboarding Specialist`
Observed contexts split across:
- merchant onboarding
- customer onboarding
- compliance/onboarding checks
- employee/hire language

Strong recurring signals:
- `customer`
- `employee`
- `hire`
- `implementation`
- `client`

Conclusion:
- not safe as title-only
- likely resolvable with context routing

### 2. `Operations Analyst`
Observed contexts include:
- business/program operations
- product operations
- security operations
- finance/revenue operations

Strong recurring signals:
- `excel`
- `product`
- `analytics`
- weaker split across `sql`, `finance`, `security`, `sales`

Conclusion:
- context needed
- likely multi-family, not a single title-only rule

### 3. `Partner Manager`
Observed contexts are mostly sales/channel/alliance oriented.

Strong recurring signals:
- `sales`
- `partnership`
- `channel`
- `reseller`
- `cloud`

Conclusion:
- promising for context-assisted routing into sales/alliances
- still unsafe title-only

### 4. `Sales Representative`
Observed contexts are not homogeneous enterprise sales.
The sampled rows are heavily consumer-finance / loan related.

Strong recurring signals:
- `loan`
- some `account`

Conclusion:
- title-only generic sales remains unsafe
- context can separate consumer-finance, enterprise sales, field sales, retail-like flows

### 5. `Producer`
Observed contexts clearly separate media/content work from game production and generic producer noise.

Strong recurring signals:
- `content`
- `news`
- `broadcast`
- `creative`
- `video`

Conclusion:
- context is high-value here
- much stronger than title-only

### 6. `Designer`
Observed contexts split by modality but are highly informative.

Strong recurring signals:
- `ui`
- `brand`
- `product`
- `graphic`
- `motion`
- `visual`
- `ux`

Conclusion:
- title-only too broad
- context could support routing to existing design labels or future finer review

### 7. `Implementation Engineer`
Observed contexts are strongly technical and customer-facing.

Strong recurring signals:
- `customer`
- `solutions`
- `integration`
- `onboarding`
- `api`
- `identity`

Conclusion:
- not safe as title-only
- context can likely distinguish implementation/solutions/integration engineering

## Proposed Hybrid Architecture

### Stage 1: Official production classification
- run the existing rule-based classifier first
- if `classification_status == matched`, stop

### Stage 2: Hybrid reviewer trigger
Only trigger hybrid review when:
- `classification_status == other`
- title belongs to a known ambiguous cluster family
- or reviewer confidence from title-only semantic layer is below threshold

### Stage 3: Context fetch
Join current titled row with extracted row by `url` and assemble:
- `title_clean`
- `description_clean`
- `requirements_clean`
- `responsibilities_clean`
- `departments_raw`
- `skills`
- `seniority`
- `employment_type`
- `company_name`

### Stage 4: Feature extraction
Build transparent features, not black-box hidden state.

Recommended feature groups:
- title tokens
- department tokens
- skills tokens
- keyword counts from `description_clean` / `requirements_clean` / `responsibilities_clean`
- known high-signal phrase flags
- semantic retrieval results on combined text windows

### Stage 5: Context reviewer output
For each ambiguous row/cluster produce:
- top internal candidate
- top ESCO candidate
- top O*NET candidate
- context evidence
- confidence
- risk
- recommended action

No automatic production mapping at this stage.

## Recommended Decision Policy

### `safe_rule_candidate`
Only when:
- title is ambiguous in general
- but context is unusually strong and repeated across cluster samples
- and a future rule can still be written readably

### `needs_tighter_rule`
When:
- context reveals a coherent subgroup
- but it still requires a narrow gated rule

### `needs_context_not_title_only`
Default for clusters where:
- the title is cross-domain
- context decides the family

### `taxonomy_gap`
When:
- context is clear
- but the current internal taxonomy has no clean destination

### `keep_other_for_now`
When:
- title and context still do not converge safely

## Guardrails
- title-first remains the production contract
- context may only act as reviewer evidence, not silent override
- no direct LLM auto-labeling in production
- every future promotion must still become:
  - readable rule
  - explicit taxonomy decision
  - tested patch
- retain `decision_trace` for every hybrid recommendation

## Recommended First Pilot Clusters
These are the best candidates for a first hybrid pilot:

1. `Onboarding Specialist`
- why: title-only ambiguous, context clearly discriminative

2. `Implementation Engineer`
- why: technical/customer-facing context is strong and repeated

3. `Partner Manager`
- why: context strongly points to channel/partner sales in many samples

4. `Producer`
- why: media/content vs game/content signals are visible in text

5. `Designer`
- why: `ux/ui/brand/graphic/motion` split is context-rich

## Clusters To Exclude From The First Pilot
- `General Manager`
- `Business Analyst`
- `Principal Engineer`
- naked `Engineer`
- naked `Architect`

Reason:
- too much residual ambiguity even with context unless a deeper semantic layer is added

## Minimal Implementation Plan

### Phase 11.1
Create a shadow-only context joiner:
- input: titled row
- join key: `url`
- output: hybrid review payload

### Phase 11.2
Create transparent keyword/context scoring for 3–5 pilot clusters

### Phase 11.3
Produce a reviewer report:
- cluster
- sample rows
- context evidence
- recommended internal target
- confidence/risk

### Phase 11.4
Promote only if the result can be translated back into:
- a tight official rule
- or a clear taxonomy decision

## Success Criteria
- hybrid reviewer reduces ambiguity for selected clusters
- at least some `title-only ambiguous` families become explainable
- no production classifier behavior changes yet
- recommendations remain auditable and reproducible

## Current Recommendation
Proceed with a shadow-only hybrid pilot, not production adoption.

The next correct artifact is:
- a context joiner
- a pilot reviewer for `Onboarding Specialist`, `Implementation Engineer`, and `Partner Manager`

These three give the best balance of:
- ambiguous title-only behavior
- strong context signals
- realistic future promotion path

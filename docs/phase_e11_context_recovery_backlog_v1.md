# Phase E.11 — Context Recovery Backlog v1

## Goal
Open the next recovery lane after `v58` by targeting high-value residual clusters that require `title + context`, not broader title-only rules.

## Baseline
- current production-style baseline: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- rows_total: `81,011`
- current other: `35,732`

## Why This Phase Exists
`v58` confirmed that narrow title-only recovery still works for explicit engineering leadership, IT support/admin, and sales-director titles.

It also confirmed the next bottleneck:
- large residual pockets are not clean title-only regex problems
- they are recoverable only when job-ad context disambiguates the title

## Context-First Priority Clusters

### 1. `customer_success_manager`
- sample count: `6`
- projected residual count: `532`
- priority: `high`
- decision: `promising_context_gate_candidate`

Representative titles:
- `Client Retention Specialist (Remote)`
- `Service Enablement Manager, CX`
- `Manager, Customer Adoption & Success (EMEA)`
- `Onboarding Specialist`
- `Operations Associate, GTM Onboarding Specialist`

Positive signals observed:
- `customer success`
- `customer adoption`
- `client retention`
- `onboarding`
- `customer services`
- `customer stakeholders`

Negative signals to guard against:
- `hr`
- `employee lifecycle`
- `kyc`
- `aml`
- `compliance`

Reading:
- this is the strongest next context candidate
- it directly extends the earlier `Onboarding Specialist` work with a broader but still coherent adoption/success cluster

### 2. `account_manager`
- sample count: `10`
- projected residual count: `887`
- priority: `high`
- decision: `reviewer_first_then_context_gate`

Representative titles:
- `Partner Development Manager`
- `Global Partner Experience Lead`
- `Provider Engagement Specialist`
- `Senior Enterprise Client Strategist`
- `Manager, Client Strategy`
- `Partner Growth Manager`
- `Client Partnership Specialist`

Positive signals observed:
- `sales`
- `business development`
- `partner success`
- `client strategy`
- `growth plans`
- `portfolio of brands`

Negative signals to guard against:
- `people operations`
- `internal enablement only`
- `marketing-only`

Reading:
- commercially oriented partner/client titles recur often
- title semantics are too broad to promote directly
- this cluster needs a reviewer-first pass before any context gate is drafted

### 3. `project_manager`
- sample count: `9`
- projected residual count: `799`
- priority: `high`
- decision: `reviewer_first_then_context_gate`

Representative titles:
- `Engagement Manager, EMEA`
- `Delivery Excellence Manager- Central`
- `Professional Services Manager II, Enterprise`
- `Engagement Manager II`
- `Staff Engineering Program Support`
- `Engagement Manager (SaaS Implementation)`

Positive signals observed:
- `professional services`
- `implementation`
- `delivery`
- `project management`
- `resource tracking`
- `customer engagements`

Negative signals to guard against:
- `pure account ownership`
- `pure operations management`
- `domain-expert IC engineering`

Reading:
- this is a strong services/delivery cluster
- but the titles span engagement, delivery, professional services, and program-support forms
- a reviewer pass should split clean promotable subclusters before rule design

## Execution Order
1. `customer_success_manager`
- build the next context pilot first
- focus on onboarding / adoption / retention variants

2. `project_manager`
- run reviewer-first split on engagement / delivery / professional-services titles

3. `account_manager`
- run reviewer-first split on partner / client-strategy / growth titles

## Recommended E.11 Deliverables
- `E.11.1` context sample join for the three clusters on full residual rows
- `E.11.2` reviewer split for promotable vs review-only subclusters
- `E.11.3` first shadow context batch focused on `customer_success_manager`

## Recommendation
- do not jump directly to production rules for `account_manager` or `project_manager`
- do start with a `customer_success_manager` shadow batch, because the observed signals are the cleanest and most repeatable
- keep taxonomy review separate; this phase is about context-backed recovery, not label expansion

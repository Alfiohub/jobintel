# Phase E.12.1 — Finance Specialist Taxonomy Proposal v1

## Goal
Propose a small, isolated taxonomy expansion for two finance-specialist labels surfaced by the residual audit.

## Scope
In scope:
- `quantitative_researcher`
- `credit_analyst`

Explicitly out of scope:
- `market_access_director`
- any broader role-family expansion beyond existing `finance`
- any production rule patch in this phase

## Why This Proposal Exists
The residual audit and taxonomy gap review both showed that some residual titles are not failing because rules are missing.
They are failing because the current taxonomy has no clean destination for them.

This proposal is intentionally narrow:
- same family: `finance`
- no new family introduction
- no classifier behavior change yet
- taxonomy decision only

## Proposed Additions

### 1. `quantitative_researcher`
- proposed normalized title: `quantitative_researcher`
- proposed role family: `finance`

Observed evidence:
- `Quantitative Researcher, Trading Research`
- `Equity Quantitative Researcher`
- `Senior Quantitative Researcher Futures`
- `Quantitative Researcher`

Why this label is justified:
- repeated across multiple companies
- semantically coherent
- clearly distinct from `financial_analyst`
- clearly distinct from `data_scientist`
- useful downstream because it isolates quant-finance research from generic finance and generic data science

Why not map to existing labels:
- `financial_analyst` underfits systematic/trading-research work
- `data_scientist` loses the finance/trading function and would distort downstream grouping

Risk:
- moderate overlap with quant-trader / quant-analyst style roles if future titles become broader

Recommendation:
- approve as taxonomy candidate
- do not add production rules until a small title-cluster validation pass is completed

### 2. `credit_analyst`
- proposed normalized title: `credit_analyst`
- proposed role family: `finance`

Observed evidence:
- `Corporate Portfolio Finance - Director`
- `Corporate Credit Assessment - Director - Senior Director`
- `CMBS New Issuance - Associate - Associate Director`

Why this label is justified:
- coherent structured-finance / ratings / credit-analysis function
- clearly more specific than `financial_analyst`
- aligns with common downstream finance segmentation

Why not map to existing labels:
- `financial_analyst` is too broad for ratings / credit / structured-finance work
- the observed language repeatedly points to credit-specific evaluation rather than general FP&A / corporate finance

Risk:
- title surface forms are less uniform than for `quantitative_researcher`
- some examples are department-heavy rather than title-clean, so rule work would need extra validation

Recommendation:
- approve as taxonomy candidate
- require more full-residual evidence before any production rule work

## Why `market_access_director` Is Excluded
- this is not just a missing title label
- it implies a likely new higher-level family such as `life_sciences`
- forcing it into `sales` or `marketing` would degrade taxonomy quality

Decision:
- keep deferred

## Acceptance Criteria
- both proposed labels fit cleanly into existing `finance`
- neither proposal widens production behavior in this phase
- the proposal remains taxonomy-only and auditable
- downstream semantics improve relative to forcing both clusters into `financial_analyst`

## Exit Conditions
- proposal reviewed
- decision recorded for `quantitative_researcher`
- decision recorded for `credit_analyst`
- separate decision retained for `market_access_director = defer`

## Recommendation
- `ready_for_taxonomy_decision_review`

# Phase E.12.4 — Taxonomy Patch Candidate v1

## Goal
Prepare an isolated taxonomy patch candidate for the two approved finance-specialist labels, without applying it to production code yet.

## Candidate Scope
Add to `src/jobintel_next/pipelines/titles/taxonomy.py`:
- `quantitative_researcher`: `finance`
- `credit_analyst`: `finance`

## Why This Patch Is Narrow
- no new role family is introduced
- no title rules are added
- no production behavior changes in this phase
- the patch only adds two taxonomy destinations already approved in `E.12.3`

## Proposed Taxonomy Insertions
```python
"quantitative_researcher": "finance",
"credit_analyst": "finance",
```

## Rationale
### `quantitative_researcher`
- validated residual candidate count: `92`
- coherent specialist quant-finance research role
- poor fit to `financial_analyst`
- poor fit to `data_scientist`

### `credit_analyst`
- validated residual candidate count: `28`
- coherent credit / ratings / structured-finance role
- more precise than forcing titles into `financial_analyst`

## What This Patch Does Not Include
- no rules for `Quantitative Researcher`
- no rules for `Credit Analyst`
- no label for `market_access_director`
- no `life_sciences` family expansion

## Risks
### `quantitative_researcher`
- some cross-domain contamination exists
- future rule work will need explicit exclusions for non-finance variants

### `credit_analyst`
- some nearby titles like `Portfolio Finance Trader` should not be pulled in later by broad matching

## Acceptance Criteria
- taxonomy remains internally valid
- new labels live under existing `finance`
- no production classifier behavior changes until a separate rule patch is approved

## Exit Condition
- patch candidate reviewed and ready for optional application in a separate future step

## Recommendation
- `ready_for_isolated_taxonomy_patch_review`

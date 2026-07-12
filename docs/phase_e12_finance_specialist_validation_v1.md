# Phase E.12.2 — Finance Specialist Residual Validation v1

## Goal
Validate whether the two finance-specialist taxonomy candidates from `E.12.1` recur on the real residual beyond the audited sample.

## Baseline
- residual base: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- residual size: `35,732`

## 1. `quantitative_researcher`
Measured residual candidate count:
- `92`

Representative titles observed:
- `Quantitative Researcher`
- `Senior Quantitative Researcher - Options Market Making`
- `Quantitative Researcher - Trading Team`
- `Quantitative Researcher - Equities`
- `Quantitative Researcher - Macro`
- `Quantitative Researcher - Machine Learning`
- `Crypto - Quantitative Researcher`
- `Cubist Quantitative Researcher`

Reading:
- this is a real recurring cluster on the full residual, not just a sample artifact
- most observed titles are consistent with a coherent quant-finance research label
- there is some contamination from broader/cross-domain variants such as `Quantitative Researcher, Healthcare Innovations`

Decision:
- `validated_as_real_taxonomy_candidate`

Recommendation:
- keep the label proposal alive
- require narrow rule design later, because title forms are broad enough to need exclusion tests

## 2. `credit_analyst`
Measured residual candidate count:
- `28`

Representative titles observed:
- `Credit Analyst`
- `Senior Credit Analyst`
- `Associate Credit Analyst`
- `Corporate Credit Assessment - Analyst - Senior Analyst`
- `Corporate Credit Assessment - Director - Senior Director`
- `CMBS New Issuance - Associate - Associate Director`
- `CMBS Surveillance - Analyst`
- `Corporate Portfolio Finance - Analyst - Senior Analyst`

Reading:
- the cluster is smaller than `quantitative_researcher` but still real
- much of the surface area is strongly credit/risk/ratings specific
- there is some contamination from titles like `Portfolio Finance Trader`, which should not be blindly absorbed into `credit_analyst`

Decision:
- `validated_as_real_taxonomy_candidate`

Recommendation:
- keep the label proposal alive
- future rule work should focus first on explicit `Credit Analyst` / `Credit Assessment` / `CMBS` forms and leave trader variants out

## Comparison
- `quantitative_researcher` has stronger residual mass
- `credit_analyst` has stronger title-surface precision

## Final Recommendation
Both labels survive residual validation.

Priority order for any future taxonomy promotion work:
1. `quantitative_researcher`
2. `credit_analyst`

Neither should move straight into production rules yet, but both are now stronger than a pure sample-based hypothesis.

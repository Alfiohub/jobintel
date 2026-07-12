# Phase E.12 — Taxonomy Gap Review v1

## Goal
Review the highest-priority taxonomy gaps surfaced by the residual audit and decide whether they are:
- plausible new labels
- temporary map-to-existing candidates
- defer / keep-other cases

## Scope
- `quantitative_researcher`
- `credit_analyst`
- `market_access_director`

## Current Constraint
None of the three targets exists in the official title taxonomy today.

## 1. `quantitative_researcher`
Observed examples:
- `Quantitative Researcher, Trading Research`
- `Equity Quantitative Researcher`
- `Senior Quantitative Researcher Futures`
- `Quantitative Researcher`

Observed evidence:
- `trading research`
- `market microstructure`
- `systematic anomalies`
- `alpha research`
- `systematic trading`

Reading:
- this is a coherent specialist quant-finance research role
- mapping it to `financial_analyst` would underfit badly
- mapping it to `data_scientist` would also be misleading because the operating domain is quant trading research, not generic data science

Decision:
- `plausible_new_label`
- proposed label: `quantitative_researcher`
- proposed family: `finance`

Recommendation:
- keep out of production for now
- open a dedicated taxonomy proposal before any rule work

## 2. `credit_analyst`
Observed examples:
- `Corporate Portfolio Finance - Director`
- `Corporate Credit Assessment - Director - Senior Director`
- `CMBS New Issuance - Associate - Associate Director`

Observed evidence:
- `credit analysis`
- `credit ratings`
- `capital structures`
- `collateral quality`
- `cash flow dynamics`
- `CRE debt underwriting`

Reading:
- this is also coherent, but less title-uniform than `quantitative_researcher`
- some examples are title-wrapped in ratings/structured-finance department language rather than explicit `Credit Analyst`
- forcing these into `financial_analyst` would lose important meaning, but they are still closer to existing finance taxonomy than market-access roles are to sales/marketing

Decision:
- `plausible_new_label`
- proposed label: `credit_analyst`
- proposed family: `finance`

Recommendation:
- keep as taxonomy candidate, not immediate production rule
- before promotion, expand evidence beyond current 3 audited samples on the full residual

## 3. `market_access_director`
Observed examples:
- `Senior Director, Field Market Access`
- `Director ARD (MLB-Calci) - East`

Observed evidence:
- `market access`
- `access & reimbursement`
- `payers`
- `reimbursement`
- `rare disease portfolio`
- `gene therapy`

Reading:
- this is a real specialized life-sciences commercial function
- the current taxonomy has no `life_sciences` family, so this is not just a missing title label; it is a higher-level family gap
- forcing it into `sales` or `marketing` would be semantically weak

Decision:
- `defer_pending_family_decision`
- not ready as a simple title-label addition under the current taxonomy

Recommendation:
- do not patch title rules for this under current taxonomy
- revisit only if a broader `life_sciences` family expansion is approved

## Final Recommendation
### Ready for dedicated taxonomy proposal
- `quantitative_researcher`
- `credit_analyst`

### Not ready under current taxonomy
- `market_access_director`

## Next Correct Step
- `E.12.1` draft a small taxonomy proposal for the two finance-specialist labels
- keep `market_access_director` deferred until there is an explicit family-expansion decision

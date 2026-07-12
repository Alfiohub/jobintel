# Title Coverage Recovery Pass v23 — Compliance / Risk Edge Expansion

## Cluster scelto
`compliance_risk` (payroll risk/compliance, product compliance, GRC core, director compliance).

## Before / After
- `other` before (v22): `39,508` (`48.77%`)
- `other` after (v23): `39,417` (`48.66%`)
- Delta `other`: `-91`

## Nuove label introdotte
- Nessuna nuova label.

## Regole aggiunte
- `compliance_payroll_risk_compliance_explicit` -> `compliance_specialist`
- `compliance_product_compliance_managerial_explicit` -> `compliance_manager`
- `compliance_product_compliance_specialist_explicit` -> `compliance_specialist`
- `compliance_grc_core_explicit` -> `compliance_specialist`

## Coverage (nuove regole)
- totale nuovi match v23: `91`
  - payroll risk/compliance: `34`
  - product compliance managerial: `25`
  - product compliance specialist: `20`
  - grc core: `12`

## Sample titoli coperti
- `Payroll Incident & Risk Lead` (`12`)
- `Associate, Risk - Compliance` (`12`)
- `Payroll Risk & Compliance Expert - Middle East` (`9`)
- `Manager, Global Product Compliance` (`5`)
- `Director, Corporate and Regulatory Compliance` (`4`)
- `Senior Staff Analyst, GRC` (`6`)

## Guardrail / limiti
- nessun mapping generico di tutti `analyst`/`specialist`
- contesto obbligatorio su payroll+risk/compliance, product compliance, GRC esplicito
- esclusi nei test pattern ingegneristici/tech (`Manager, Software Engineering (Fraud)`, `Staff Engineer, Risk Insights`)

## Top residual `other` (post-v23)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)

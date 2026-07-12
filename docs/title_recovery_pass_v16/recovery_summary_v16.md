# Title Coverage Recovery Pass v16 — Compliance / Risk Expansion

## Scope
Pass focalizzato solo su `compliance_risk` residuale ad alto volume, con regole conservative su sottocluster compliance/risk ad alta chiarezza.

## Before / After
- Total rows: `81,011`
- `other` before (v15): `40,430` (`49.91%`)
- `other` after (v16): `40,241` (`49.67%`)
- Delta `other`: `-189`

## Compliance / Risk Cluster Delta
- `compliance_risk` residual before (v15): `636`
- `compliance_risk` residual after (v16): `510`
- Delta compliance_risk residual: `-126`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso label esistenti:
- `compliance_specialist`
- `compliance_manager`

## Regole aggiunte (sottocluster high-ROI)
- `compliance_risk_analyst_specialist_explicit` -> `compliance_specialist`
  - risk analyst, fraud analyst, aml analyst, kyc onboarding analyst, credit risk analyst, regulatory response analyst, grc/ict risk analyst, account/growth risk specialist
- `compliance_aml_kyc_fraud_investigator_explicit` -> `compliance_specialist`
  - aml investigator, fraud investigator, fraud investigations manager, kyc representative
- `compliance_internal_audit_explicit` -> `compliance_manager`
  - internal audit analyst/senior/manager, director/head of internal audit
- `compliance_risk_manager_director_explicit` -> `compliance_manager`
  - compliance officer/lead/director/head of compliance, operational/enterprise/financial/credit risk manager, senior risk manager, senior director risk management

## Guardrail rispettati
- nessun mapping generico di tutti gli `analyst`
- nessun mapping generico di tutti gli `specialist`
- pattern richiedono contesto forte (`risk/compliance/aml/kyc/fraud/audit/regulatory/grc`)
- titoli tecnici non-compliance (es. `Controls Engineer`) non vengono assorbiti da queste regole

## Coverage (nuove regole)
- `compliance_risk_analyst_specialist_explicit`: `71`
- `compliance_aml_kyc_fraud_investigator_explicit`: `13`
- `compliance_internal_audit_explicit`: `22`
- `compliance_risk_manager_director_explicit`: `83`
- totale nuovi match v16 (compliance-focused): `189`

## Sample titoli coperti
- `Third Party Risk Analyst` -> `compliance_specialist` (`5`)
- `Fraud Analyst` -> `compliance_specialist` (`5`)
- `AML Analyst` -> `compliance_specialist` (`2`)
- `Internal Audit Manager` -> `compliance_manager` (`5`)
- `Compliance Officer` -> `compliance_manager` (`6`)
- `Operational Risk Manager` -> `compliance_manager` (`3`)

## Top residual `other` (post-v16)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `sonder responder` (19)
11. `restaurant general manager` (19)
12. `manager, software engineering` (18)
13. `cultivation associate` (18)
14. `k-5th grade teacher - sy 26-27` (17)
15. `leader in training` (17)
16. `outside sales representative - roofing` (17)
17. `data science manager` (16)
18. `principal engineer` (16)
19. `bilingual member services representative (remote, spanish speaking)` (16)
20. `intelligence operations integrator` (16)

## Compliance / Risk residual ancora scoperti (top)
- `Payroll Incident & Risk Lead` (12)
- `Associate, Risk - Compliance` (12)
- `Payroll Risk & Compliance Expert - Middle East` (9)
- `Regulatory Manager - Senior Regulatory Manager - Clinical Trials` (7)
- `Manager, Global Product Compliance` (5)
- `Microsoft 365 Governance Administrator` (5)
- `Control Systems Engineer - Site Services` (5)
- `Senior Controls Engineer` (4)
- `Associate, Operational Controls` (4)
- `Director, Corporate and Regulatory Compliance` (4)

## Cluster consigliato per v17
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Compliance edge pass su payroll/compliance e regulatory compliance leadership (pattern stretti)
3. Operations/service ambiguity (`member services`, `cultivation associate`) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v16/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `30 passed`

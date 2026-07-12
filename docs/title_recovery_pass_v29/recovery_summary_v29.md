# Title Coverage Recovery Pass v29 — Compliance / Risk Edge Pass

## Cluster scelto
`compliance_risk` edge su sottocluster ad alta chiarezza:
- `regulatory affairs`
- `internal audit`
- `compliance onboarding` esplicito

## Before / After
- Total rows: `81,011`
- `other` before (v28): `39,178` (`48.36%`)
- `other` after (v29): `39,141` (`48.32%`)
- Delta `other`: `-37`

## Compliance Cluster Delta
- `compliance_risk` residual before (v28): `430`
- `compliance_risk` residual after (v29): `404`
- Delta compliance_risk residual: `-26`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `compliance_manager` -> `compliance_risk`
- `compliance_specialist` -> `compliance_risk`

## Regole aggiunte (precision)
- `compliance_regulatory_affairs_manager_edge_v29`
  - manager/director/head/vp + `regulatory affairs`
  - `regulatory licensing and affairs team lead`
- `compliance_regulatory_affairs_specialist_edge_v29`
  - `regulatory affairs analyst/advisor`
  - `senior analyst regulatory affairs`
  - `specialist I-II regulatory affairs`
  - `affiliate services licensing specialist regulatory affairs`
- `compliance_internal_audit_manager_edge_v29`
  - `manager/director/vp/vice president/internal audit lead` + `internal audit`
- `compliance_onboarding_explicit_edge_v29`
  - `director kyc and compliance onboarding`
  - `specialist onboarding compliance`
  - `risk strategist onboarding and compliance`

## Coverage (nuove regole)
- `compliance_regulatory_affairs_manager_edge_v29`: `14`
- `compliance_regulatory_affairs_specialist_edge_v29`: `5`
- `compliance_internal_audit_manager_edge_v29`: `12`
- `compliance_onboarding_explicit_edge_v29`: `6`
- totale nuovi match v29: `37`

## Sample titoli coperti
- `Director, KYC and Compliance Onboarding` (`4`)
- `Regulatory Licensing and Affairs Team Lead - North America` (`2`)
- `Senior Manager, Internal Audit` (`2`)
- `Manager, Regulatory Affairs` (`2`)
- `Senior Director, Regulatory Affairs` (`1`)
- `Director of Internal Audit & SOX Compliance` (`1`)
- `VP, Internal Audit and Controls` (`1`)
- `Specialist, Onboarding Compliance` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `analyst`
- nessun mapping generico di tutti gli `specialist`
- nessun mapping generico di tutti i `manager`
- contesto forte obbligatorio (`regulatory affairs`, `internal audit`, `compliance onboarding`, `kyc`)
- nessun allargamento su pattern tecnici/ambigui (`controls engineer`, `data governance`, `software engineering risk/fraud`)

## Top residual `other` (post-v29)
1. `General Manager` (40)
2. `Senior Market Strategy and Partnerships Manager` (36)
3. `Hair Color Bar Assistant, Licensed Cosmetologist` (32)
4. `General Application` (31)
5. `Producer` (27)
6. `Social Enterprise and Program Delivery-Evergreen` (27)
7. `Personal Care Specialist (Part Time)` (26)
8. `Quantitative Researcher` (24)
9. `Business Analyst` (20)
10. `Sonder Responder` (19)
11. `Restaurant General Manager` (19)
12. `Manager, Software Engineering` (18)
13. `Cultivation Associate` (18)
14. `Leader in Training` (17)
15. `Outside Sales Representative - Roofing` (17)
16. `Data Science Manager` (16)
17. `Principal Engineer` (16)
18. `Intelligence Operations Integrator` (16)
19. `Senior Firmware Engineer` (15)
20. `Manager, Paid Social` (15)

## Sottocluster compliance_risk ancora scoperti (top)
- `Onboarding Specialist` (13)
- `Regulatory Manager - Senior Regulatory Manager - Clinical Trials` (7)
- `Microsoft 365 Governance Administrator` (5)
- `Control Systems Engineer - Site Services` (5)
- `Senior Controls Engineer` (4)
- `Associate, Operational Controls` (4)
- `Senior Analyst, UM Regulatory Operations` (4)
- `Manager, Compliance Execution & Enablement` (3)
- `Sr Manager, InfoSec Governance Risk and Compliance (GRC)` (3)
- `eCommerce Compliance & Fraud Specialist (f - m - d)` (3)

## Cluster consigliato per v30
1. `compliance_risk` edge su `manager, compliance ...` / `regulatory operations` con pattern stretti anti-overmatch.
2. `skilled_trades` edge (tool trailer/diesel/automotive state inspector) con contesto forte non-IT.
3. `customer_service` edge (`client service associate/member services coordinator`) con guardrail forti.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v29/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v29.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `37 passed`

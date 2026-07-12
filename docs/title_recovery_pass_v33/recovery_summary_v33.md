# Title Coverage Recovery Pass v33 — Compliance / Risk Onboarding & Regulatory Ops Edge Pass

## Cluster scelto
`compliance_risk` residuale (sottocluster ad alta chiarezza: `regulatory operations` + `onboarding` con contesto `AML/KYC/CDD/risk/compliance`).

## Before / After
- Total rows: `81,011`
- `other` before (v32): `39,040` (`48.19%`)
- `other` after (v33): `39,027` (`48.18%`)
- Delta `other`: `-13`

## Compliance/Risk Cluster Delta
- `compliance_risk` residual before (v32): `404`
- `compliance_risk` residual after (v33): `394`
- Delta compliance_risk residual: `-10`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `compliance_specialist` -> `compliance_risk`

## Regole aggiunte/aggiornate (precision)
- `compliance_regulatory_operations_edge_v33`
  - match stretti su pattern espliciti:
    - `senior analyst um regulatory operations`
    - `senior analyst regulatory operations`
    - `director regulatory operations`
    - `regulatory operations lead`
    - `associate director regulatory operations and intelligence`
    - `vp/vice president regulatory affairs strategy labeling and operations`
- `compliance_onboarding_risk_context_edge_v33`
  - richiede co-occorrenza `onboarding` + uno tra `aml|kyc|cdd|risk|compliance`

Nota tecnica: fixata la regex per allinearsi alla normalizzazione (punteggiatura rimossa, `vp` -> `vice president`).

## Coverage (regole v33)
- `compliance_regulatory_operations_edge_v33`: `9`
- `compliance_onboarding_risk_context_edge_v33`: `5`
- totale nuovi match v33: `14`
- delta netto su `other`: `-13`

## Sample titoli coperti
- `Senior Analyst, UM Regulatory Operations` (`4`)
- `Senior Analyst, Regulatory Operations` (`1`)
- `Director, Regulatory Operations` (`1`)
- `Regulatory Operations Lead, APAC` (`1`)
- `Associate Director, Regulatory Operations and Intelligence` (`1`)
- `VP, Regulatory Affairs, Strategy, Labeling and Operations` (`1`)
- `AML Onboarding Analyst` (`1`)
- `Client Onboarding & KYC Specialist` (`1`)
- `CDD Onboarding Analyst` (`1`)
- `Team lead - CDD Risk, Customer Onboarding` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `analyst`
- nessun mapping generico di tutti gli `specialist`
- nessun mapping generico di tutte le `operations`
- contesto forte obbligatorio (`regulatory operations` oppure `onboarding` + `aml/kyc/cdd/risk/compliance`)
- test negativi su casi ambigui/non target:
  - `Onboarding Specialist`
  - `SaaS Onboarding Specialist`
  - `Regulatory Manager - Senior Regulatory Manager - Clinical Trials`
  - `Cloud Operations Support Engineer, Compliance`

## Top residual `other` (post-v33)
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
- `Associate, Operational Controls` (4)
- `Management Consultant - Financial Risk` (3)
- `Manager, Compliance Execution & Enablement` (3)
- `Regulatory and Site Start Up Specialist` (3)

## Cluster consigliato per v34
1. `customer_service` edge (`client service associate`, `member services coordinator`) con pattern stretti.
2. `compliance_risk` governance/controls edge con contesto forte non-engineering (`operational controls`, `compliance execution`) e anti-overmatch su engineer/manager generico.
3. `skilled_trades` edge non-IT (`tool trailer technician`, `automotive state inspector`) con guardrail conservativi.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v33/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v33.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `40 passed`

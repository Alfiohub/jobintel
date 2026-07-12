# Title Coverage Recovery Pass v39 — Customer Care Advisor / Executive Edge Pass

## Cluster scelto
Micro-cluster `customer care advisor / executive` con contesto customer-service esplicito.

## Before / After
- Total rows: `81,011`
- `other` before (v38): `38,008` (`46.92%`)
- `other` after (v39): `37,996` (`46.90%`)
- Delta `other`: `-12`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `customer_service_specialist` -> `operations`

## Regola aggiunta (precision)
- `customer_care_advisor_executive_edge_v39`
  - pattern stretto: `customer care advisor|executive`
  - non allargata a tutti gli `advisor`/`executive`

## Coverage (nuova regola)
- `customer_care_advisor_executive_edge_v39`: `12`

## Sample titoli coperti
- `Customer Care Executive` (`2`)
- `Customer Care Executive (English and German)` (`2`)
- `Customer Care Executive (Spanish, Greek and English)` (`2`)
- `Customer Care Advisor (Non-voice)` (`1`)
- `Customer Care Advisor (Voice)` (`1`)
- `UAE Customer Care Advisor (Non-voice)` (`1`)
- `UAE Customer Care Advisor (Voice)` (`1`)
- `Customer Care Advisor, Boca Raton` (`1`)
- `Customer Care Advisor, Nashville` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `advisor`
- nessun mapping generico di tutti gli `executive`
- contesto forte obbligatorio: `customer care`
- esclusi pattern IT/technical/support engineering tramite test negativi:
  - `Technical Support Engineer`
  - `Customer Support Engineer`
  - `Senior Customer Care Engineer - Federal TS SCI w - FSP`
- escluso overlap sales: `Account Executive`
- esclusi manageriali larghi: `Manager/Director/VP Customer Care`

## Varianti lasciate volutamente in `other`
- `Customer Care Specialist ...` (varie forme)
- `Customer Care Associate ...`
- `Manager, Customer Care` / `Director, Customer Care`
- `VP Customer Care & Contact Center Shared Services`

Motivo: questo pass era limitato a `advisor/executive` per massimizzare precisione e minimizzare overmatch.

## Top residual `other` (post-v39)
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

## Cluster consigliato per v40
1. `design_creative` edge su `producer` contestuale forte (`video/content/editorial`) con esclusione di `producer` nudo.
2. `customer_service` micro-edge su `customer care specialist/associate` con esclusione di manageriali/technical.
3. `compliance_risk` micro-edge finance-regulatory (`risk and compliance analyst/consultant`) con pattern chiusi.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v39/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v39.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `45 passed`

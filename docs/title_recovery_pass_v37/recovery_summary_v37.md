# Title Coverage Recovery Pass v37 — Customer Service Edge Pass

## Cluster scelto
`customer_service` edge su pattern stretti `client service associate` / `member services coordinator` / `client support specialist` non-IT.

## Before / After
- Total rows: `81,011`
- `other` before (v36): `38,705` (`47.78%`)
- `other` after (v37): `38,673` (`47.74%`)
- Delta `other`: `-32`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `customer_service_specialist` -> `operations`

## Regole aggiunte (precision)
- `customer_client_service_associate_edge_v37`
  - `client service associate`
  - `client services representative`
  - `senior client services specialist`
  - `associate - senior associate - client services`
  - `registered brokerage client service associate`
- `customer_member_services_coordinator_edge_v37`
  - `member services coordinator`
- `customer_client_support_specialist_edge_v37`
  - `client support specialist`

## Coverage (nuove regole)
- `customer_client_service_associate_edge_v37`: `24`
- `customer_member_services_coordinator_edge_v37`: `4`
- `customer_client_support_specialist_edge_v37`: `4`
- totale nuovi match v37: `32`

## Sample titoli coperti
- `Client Service Associate` (`8`)
- `Senior Client Services Specialist` (`2`)
- `Associate - Senior Associate - Client Services` (`2`)
- `Registered Brokerage Client Service Associate - APAC Timezone` (`1`)
- `Registered Brokerage Client Service Associate - Eastern Timezone` (`1`)
- `Member Services Coordinator` (`4`)
- `Client Support Specialist` (`4`)

## Guardrail rispettati
- nessun mapping generico di tutti i `support specialist`
- nessun mapping generico di tutti i `coordinator`
- nessun mapping generico di tutti gli `associate`
- contesto forte obbligatorio su `client service` / `member services` / `client support specialist`
- esclusi pattern IT/engineering via test negativi:
  - `IT Support Specialist`
  - `Technical Support Specialist - German`
  - `Customer Support Engineer`
  - `Client Support Engineer`
- esclusi manageriali (`Member Services Manager`) e coordinator generici fuori focus

## Varianti lasciate volutamente in `other`
- `Support Specialist` (`4`)
- `Product Support Specialist` (`11`)
- `Client Support Manager` (`4`)
- `Senior Client Services Manager, Enterprise` (`3`)
- `Customer Service Coordinator - Vehicle Delivery` (`3`)
- `Integration Support Specialist` (`2`)

Motivo: ambiguità alta (product/technical/managerial/logistics), rischio overmatch.

## Top residual `other` (post-v37)
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

## Cluster consigliato per v38
1. `design_creative` edge su `producer` contestuale forte (`video/content/editorial`), lasciando `producer` nudo in `other`.
2. `compliance_risk` micro-edge su GRC non-engineering (`grc analyst/consultant`) con esclusioni tecniche forti.
3. `customer_service` micro-edge su `customer care advisor/executive` con pattern molto stretti e anti-IT.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v37/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v37.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `43 passed`

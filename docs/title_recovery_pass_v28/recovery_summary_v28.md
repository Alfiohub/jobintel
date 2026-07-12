# Title Coverage Recovery Pass v28 — Skilled Trades HVAC / Plumbing Edge Pass

## Cluster scelto
`skilled_trades` edge su HVAC/plumbing/install con pattern stretti e contesto forte.

## Before / After
- Total rows: `81,011`
- `other` before (v27): `39,190` (`48.38%`)
- `other` after (v28): `39,178` (`48.36%`)
- Delta `other`: `-12`

## Skilled Trades Cluster Delta
- `skilled_trades` residual before (v27): `1,168`
- `skilled_trades` residual after (v28): `1,159`
- Delta skilled_trades residual: `-9`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `technician` -> `skilled_trades`
- `field_technician` -> `skilled_trades`

## Regole aggiunte (precision)
- `trades_hvac_install_edge_v28`
  - pattern espliciti: `hvac lead installer`, `hvac install technician`, `commercial hvac installer`, `hvac apprentice`
- `trades_plumbing_install_service_edge_v28`
  - pattern espliciti: `plumbing install lead`, `plumbing install technician`, `plumbing service technician`, `plumbing apprentice`

## Coverage (nuove regole)
- `trades_hvac_install_edge_v28`: `8`
- `trades_plumbing_install_service_edge_v28`: `4`
- totale nuovi match v28: `12`

## Sample titoli coperti
- `HVAC Lead Installer (Relocation Offered!!!)` (`5`)
- `HVAC Lead Installer` (`1`)
- `HVAC Install Technician` (`1`)
- `HVAC Apprentice` (`1`)
- `Plumbing Install Lead` (`1`)
- `Plumbing Install Technician` (`1`)
- `Plumbing Service Technician` (`1`)
- `Plumbing Apprentice` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `installer`
- nessun mapping generico di tutti i `plumber`
- nessun mapping generico di tutti i `manager`
- nessun mapping generico di tutti gli `engineer`
- contesto forte obbligatorio (`hvac` + install/apprentice, `plumbing` + install/service/apprentice)
- esclusi pattern manageriali/engineering (es. `General Manager (Pump, Power & HVAC)`, `Plumbing & Fire Protection Engineer II`)

## Top residual `other` (post-v28)
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

## Sottocluster skilled_trades ancora scoperti (top)
- `Robotics Field Service Engineer` (8)
- `General Manager (Pump, Power & HVAC)` (5)
- `Tool Trailer Technician` (5)
- `Field Service Engineer` (4)
- `Plumbing & Fire Protection Engineer II` (4)
- `Plumbing - Fire Protection - Entry Level` (3)
- `Plumbing & Fire Protection IB` (3)
- `Plumbing & Fire Protection II` (3)
- `Project Plumbing - Fire Protection Engineer IV` (3)
- `HVAC Technical Support` (3)

## Cluster consigliato per v29
1. `skilled_trades` edge su technician non-IT (tool trailer / diesel fleet / automotive state inspector) con pattern stretti.
2. `compliance_risk` edge (`regulatory/product compliance`) con contesto forte.
3. `customer_service` edge (`client service associate/member services coordinator`) con guardrail anti-overmatch.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v28/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v28.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `37 passed`

# Title Coverage Recovery Pass v31 — Skilled Trades Edge Pass

## Cluster scelto
`skilled_trades` (sottocluster ad alta chiarezza e ROI: `tool trailer technician` + `automotive ... state inspector`).

## Before / After
- Total rows: `81,011`
- `other` before (v30): `39,121` (`48.29%`)
- `other` after (v31): `39,108` (`48.28%`)
- Delta `other`: `-13`

## Skilled Trades Cluster Delta
- `skilled_trades` residual before (v30): `1,159`
- `skilled_trades` residual after (v31): `1,150`
- Delta skilled_trades residual: `-9`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `technician` -> `skilled_trades`
- `mechanic` -> `skilled_trades`

## Regole aggiunte (precision)
- `trades_tool_trailer_technician_edge_v31`
  - match esatto: `tool trailer technician`
- `trades_automotive_state_inspector_edge_v31`
  - `automotive state inspector` (incl. `(2nd shift)`)
  - `automotive technician ... state inspector`

## Coverage (nuove regole)
- `trades_tool_trailer_technician_edge_v31`: `5`
- `trades_automotive_state_inspector_edge_v31`: `8`
- totale nuovi match v31: `13`

## Sample titoli coperti
- `Tool Trailer Technician` (`5`)
- `Automotive Technician - State Inspector` (`3`)
- `Automotive State Inspector` (`2`)
- `Automotive State Inspector (2nd Shift)` (`2`)
- `Junior Automotive Technician - State Inspector` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `technician`
- nessun mapping generico di tutti i `mechanic`
- nessun mapping generico di tutti gli `engineer`
- contesto forte obbligatorio su `tool trailer technician` e `automotive ... state inspector`
- esclusi pattern ambigui/IT (`IT Services Technician`, `Data Center Technician`, `Fleet Support Engineer`, `Engineering Technician`)

## Top residual `other` (post-v31)
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
- `A&P Mechanic Instructor` (11)
- `Robotics Field Service Engineer` (8)
- `Lab Technician` (7)
- `Data Center Technician` (7)
- `Aircraft Mechanic - Instructor` (7)
- `Aircraft Mechanic Instructor` (6)
- `IT Services Technician` (5)
- `Engineering Technician` (5)
- `IT Support Technician` (5)
- `General Manager (Pump, Power & HVAC)` (5)

## Cluster consigliato per v32
1. `compliance_risk` edge su `onboarding specialist` / `regulatory operations` con pattern stretti.
2. `design_creative` edge su `creative strategist` (contesto forte, anti-overlap marketing).
3. `skilled_trades` edge su `diesel fleet technician` / `tool trailer` adjacency non-IT.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v31/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v31.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `39 passed`

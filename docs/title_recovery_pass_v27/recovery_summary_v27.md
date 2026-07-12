# Title Coverage Recovery Pass v27 — Skilled Trades Precision Pass

## Cluster scelto
`skilled_trades` (sottocluster ad alta chiarezza su auto-body / repair-detail, con contesto forte e anti-overmatch su engineer/IT).

## Before / After
- Total rows: `81,011`
- `other` before (v26): `39,273` (`48.48%`)
- `other` after (v27): `39,190` (`48.38%`)
- Delta `other`: `-83`

## Skilled Trades Cluster Delta
- `skilled_trades` residual before (v26): `1,207`
- `skilled_trades` residual after (v27): `1,168`
- Delta skilled_trades residual: `-39`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `mechanic` -> `skilled_trades`

## Regole aggiornate
- `trades_auto_repair_detail_precision_v27` (estesa)
  - aggiunti pattern espliciti per:
    - `auto body|autobody` con contesto `inspector|prep|prepper|painter|estimator|apprentice|cosmetic inspector|line lead`
    - varianti `auto/automotive interior repair ... tech|technician`
    - varianti `automotive rim repair` / `auto rim repair` anche senza suffisso `tech`

## Coverage (regola v27)
- `trades_auto_repair_detail_precision_v27`: `81`

Nota: la regola esisteva già in v26 ma era più stretta; in v27 viene estesa mantenendo guardrail conservativi.

## Sample titoli coperti
- `Mid-Level Auto Interior Repair - Glass Repair Technician - $4, 000 Bonus` (`5`)
- `Auto Body Inspector` (`4`)
- `Stellantis Certified Technician - $5, 000 Bonus` (`3`)
- `Auto Body Painter - $4, 000 Bonus` (`2`)
- `Auto Body Estimator` (`2`)
- `Automotive Wheel - Rim Repair Technician` (`2`)
- `Rim Repair Tech` (`2`)

## Guardrail rispettati
- nessun mapping generico di tutti i `technician`
- nessun mapping generico di tutti i `mechanic`
- nessun mapping generico di tutti gli `engineer`
- contesto obbligatorio su segnali auto-body/repair-detail ad alta precisione
- test negativi su:
  - `IT Services Technician`
  - `Engineering Technician`
  - `Robotics Field Service Engineer`
  - `Data Center Technician`
  - `Field Service Engineer`

## Top residual `other` (post-v27)
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
- `HVAC Lead Installer (Relocation Offered!!!)` (5)  
- `Field Service Engineer` (4)  
- `HVAC Technical Support` (3)  
- `Regional HVAC Service Trainer` (3)  
- `Field Service Representative - Mechanical (Traveling)` (3)  
- `Autobody Manager` (2)  
- `Automotive State Inspector` (2)

## Cluster consigliato per v28
1. `skilled_trades` edge su `hvac/plumbing/install` con pattern stretti e anti-manager/anti-engineer.
2. `compliance_risk` edge (`regulatory/product compliance`) con contesto forte.
3. `customer_service` edge (`client service associate/member services coordinator`) solo con pattern conservativi.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v27/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v27.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `36 passed`

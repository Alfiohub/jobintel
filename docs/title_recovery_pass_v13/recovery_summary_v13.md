# Title Coverage Recovery Pass v13 — Skilled Trades Expansion

## Scope
Pass focalizzato solo su `skilled_trades` residuale ad alto volume, con espansione pragmatica ma controllata per sottocluster chiari.

## Before / After
- Total rows: `81,011`
- `other` before (v12): `41,229` (`50.89%`)
- `other` after (v13): `40,951` (`50.55%`)
- Delta `other`: `-278`

## Skilled Trades Cluster Delta
- `skilled_trades` residual before (v12): `1,645`
- `skilled_trades` residual after (v13): `1,400`
- Delta skilled_trades residual: `-245`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistenti per massimizzare ROI senza espandere tassonomia:
- `mechanic`
- `technician`
- `field_technician`

## Regole aggiunte (sottocluster high-ROI)
- `trades_auto_body_collision_technician` -> `mechanic`
  - auto body repair tech/technician, paintless dent repair technician, auto body prepper, automotive wheel/rim repair technician
- `trades_hvac_service_technician_explicit` -> `technician`
  - commercial hvac service technician, hvac technician, lead hvac service technician
- `trades_diesel_technician_explicit` -> `mechanic`
- `trades_telematics_installer_explicit` -> `technician`
- `trades_plumber_explicit` -> `field_technician`
  - plumber / lead plumber / lead install plumber / journeyman plumber
- `trades_mechanical_electrical_tool_technician_explicit` -> `technician`
  - mechanical/electrical/tool/electro-mechanical technician

## Guardrail rispettati
- nessun mapping generico di tutti i `technician`
- nessun mapping generico di tutti gli `specialist`
- regole solo su sottocluster espliciti con contesto forte
- esempi mantenuti fuori scope: `Lab Technician`, `Engineering Technician`, `A&P Mechanic Instructor`

## Sample titoli coperti
- `Auto Body Repair Technician` -> `mechanic` (`16`)
- `Automotive Wheel Repair Technician` -> `mechanic` (`14`)
- `Commercial HVAC Service Technician` -> `technician` (`15`)
- `HVAC Technician` -> `technician` (`10`)
- `Diesel Technician` -> `mechanic` (`3`)
- `Telematics Installer` -> `technician` (`13`)
- `Lead Plumber` / `Plumber` -> `field_technician` (`17` combinati)
- `Mechanical Technician` -> `technician` (`7`)

## Top residual `other` (post-v13)
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

## Skilled Trades Residual ancora scoperti (top)
- `Specialty Pharmacy Technician` (15)
- `A&P Mechanic Instructor` (11)
- `Field Service Technician` (10)
- `Facilities Technician` (9)
- `Auto Airbrush Technician` (9)
- `Cultivation Technician` (9)
- `Robotics Field Service Engineer` (8)
- `Aircraft Maintenance Instructor` (8)
- `Lab Technician` (7)
- `Data Center Technician` (7)

## Cluster consigliato per v14
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Skilled-trades edge cleanup con guardrail (instructor/technician ambigui: aircraft/data-center/lab/facilities)
3. Service/operations ambiguity (`member services representative`, `cultivation associate`) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v13/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `27 passed`

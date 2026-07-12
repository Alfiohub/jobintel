# Title Coverage Recovery Pass v32 — Assisted Recovery v2 First Guided Pass

## Cluster scelto
`media_planning` (design/creative-adjacent, mapping pragmatico su marketing con contesto forte).

## Before / After
- Total rows: `81,011`
- `other` before (v31): `39,108` (`48.28%`)
- `other` after (v32): `39,040` (`48.19%`)
- Delta `other`: `-68`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `marketing_specialist` -> `marketing`

## Regole aggiunte
- `marketing_media_planning_edge_v32`
  - pattern stretti su:
    - `Media Manager` / `Senior Media Manager`
    - `Media Planner` / `Senior Media Planner`
    - `Programmatic Media Manager|Strategist|Supervisor`
    - `Assistant/Integrated/Traditional/Offline Media Planner/Manager`
    - `Media Associate`

## Coverage (nuova regola)
- `marketing_media_planning_edge_v32`: `68`

## Sample titoli coperti
- `Media Manager` (`13`)
- `Senior Media Manager` (`10`)
- `Senior Media Manager, (Healthcare)` (`8`)
- `Media Planner` (`6`)
- `Programmatic Media Supervisor` (`5`)
- `Programmatic Media Strategist` (`4`)
- `Senior Media Planner` (`3`)
- `Media Associate` (`3`)

## Guardrail applicati
- no mapping generico di `manager`
- no mapping generico di `designer`
- no mapping generico di `producer`
- contesto obbligatorio media/planner/programmatic
- esclusi esempi ambigui: `Director, Media`, `Brand Partnerships Manager`, `Creative Strategist`, `Media Manager, Content Operations`

## Top residual `other` (post-v32)
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

## Sottocluster design/creative ancora scoperti (top)
- `Producer` (27)
- `Designer` (11)
- `Director of Product Design` (9)
- `Senior Designer` (9)
- `Creative Strategist` (9)
- `Research Engineer` (8)
- `Head of Partnerships` (8)
- `Brand Partnerships Manager` (8)
- `Design Engineer` (8)
- `Amazon & Retail Media Strategist - Search (PPC)` (8)

## Cluster consigliato per pass successivo
1. `design_creative` edge su `creative strategist` (pattern molto stretti, anti-overlap marketing)
2. `compliance_risk` edge su `onboarding specialist` con split dominio
3. `skilled_trades` edge su `diesel fleet technician` non-IT

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v32/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v32.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `40 passed`

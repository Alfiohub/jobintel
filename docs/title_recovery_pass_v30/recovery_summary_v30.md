# Title Coverage Recovery Pass v30 — Design / Creative Precision Pass

## Cluster scelto
`design_creative` (sottocluster editoriale ad alta chiarezza: editor/content-editor/managing-editor con contesto forte).

## Before / After
- Total rows: `81,011`
- `other` before (v29): `39,141` (`48.32%`)
- `other` after (v30): `39,121` (`48.29%`)
- Delta `other`: `-20`

## Design Cluster Delta
- `design_creative` residual before (v29): `920`
- `design_creative` residual after (v30): `900`
- Delta design_creative residual: `-20`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `story_editor` -> `content`

## Regole aggiunte (precision)
- `content_editorial_editors_edge_v30`
  - pattern espliciti su:
    - `content editor`
    - `data science editor`
    - `copy editor`
    - `technical content editor`
    - `video content editor`
    - `executive editor`
    - `associate managing editor - healthcare agency`
    - `managing editor ...`
    - `senior editor editorial review`

## Coverage (nuove regole)
- `content_editorial_editors_edge_v30`: `20`

## Sample titoli coperti
- `Data Science Editor` (`3`)
- `Content Editor` (`3`)
- `Executive Editor (based in Madrid)` (`3`)
- `Executive Editor` (`2`)
- `Copy Editor` (`2`)
- `Associate Managing Editor - Healthcare Agency` (`2`)
- `Technical Content Editor` (`1`)
- `Managing Editor, Health Payer Specialist` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `producer`
- nessun mapping generico di tutti i `designer`
- nessun mapping generico di tutti gli `editor`
- contesto forte obbligatorio su pattern editoriali specifici
- esclusi pattern ambigui/overlap marketing-manageriale (`Media Manager`, `Senior Media Manager`, `Creative Strategist`, `Manager, Editorial`)

## Top residual `other` (post-v30)
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

## Sottocluster design_creative ancora scoperti (top)
- `Producer` (27)
- `Media Manager` (13)
- `Designer` (11)
- `Senior Media Manager` (10)
- `Director of Product Design` (9)
- `Senior Designer` (9)
- `Creative Strategist` (9)
- `Research Engineer` (8)
- `Brand Partnerships Manager` (8)
- `Design Engineer` (8)

## Cluster consigliato per v31
1. `design_creative` edge su `creative strategist` (solo pattern forti, anti-overlap marketing).
2. `compliance_risk` edge su `onboarding specialist` / `regulatory operations` con guardrail stretti.
3. `skilled_trades` edge su technician non-IT (tool trailer/diesel/automotive state inspector).

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v30/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v30.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `38 passed`

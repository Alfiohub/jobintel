# Title Coverage Recovery Pass v10 — Healthcare Precision Pass

## Scope
Pass focalizzato solo sul cluster healthcare residuale ad alta precisione (`board certified behavior analyst` / `bcba`) con guardrail conservativi.

## Before / After
- Total rows: `81,011`
- `other` before (v9): `41,390` (`51.09%`)
- `other` after (v10): `41,334` (`51.02%`)
- Delta `other`: `-56`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente verso `behavioral_support_specialist` (`healthcare_clinical`) per evitare espansioni tassonomiche non necessarie.

## Regole aggiunte (precision)
- `health_board_certified_behavior_analyst`
  - pattern: `board certified behavior analyst` o `bcba`
  - output: `behavioral_support_specialist` / `healthcare_clinical`

## Guardrail rispettati
- nessun mapping generico di tutti gli `analyst`
- nessun mapping generico di tutti gli `specialist`
- `business analyst` resta `other`
- `personal care specialist` resta `other` (cluster ambiguo/non-clinico nel dataset attuale)

## Sample titoli coperti
- `Board Certified Behavior Analyst` -> `behavioral_support_specialist` (`20`)
- `BCBA (Board Certified Behavior Analyst)` -> `behavioral_support_specialist` (`5`)

## Titoli mantenuti in `other` (scelta conservativa)
- `Personal Care Specialist (Part Time)` -> `other` (`26`)
- `Personal Care Specialist` -> `other` (`4`)

## Top residual `other` (post-v10)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `solution specialist` (20)
11. `sonder responder` (19)
12. `restaurant general manager` (19)
13. `story desk editor` (19)
14. `manager, software engineering` (18)
15. `cultivation associate` (18)
16. `k-5th grade teacher - sy 26-27` (17)
17. `technical writer` (17)
18. `leader in training` (17)
19. `outside sales representative - roofing` (17)
20. `technical support specialist` (16)

## Cluster consigliato per v11
1. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
2. Writer/editor precision (`technical writer`, `story desk editor`) con mapping mirato o permanenza in `other`
3. Specialist ambiguity cleanup (`solution specialist`, `technical support specialist`) con guardrail forti

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v10/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `24 passed`

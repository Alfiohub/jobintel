# Title Coverage Recovery Pass v11 — Writer / Editor Precision Pass

## Scope
Pass focalizzato solo sul cluster residuale writer/editor ad alta precisione (`technical writer`, `story desk editor`) con regole strette e guardrail anti-overmatch.

## Before / After
- Total rows: `81,011`
- `other` before (v10): `41,334` (`51.02%`)
- `other` after (v11): `41,269` (`50.94%`)
- Delta `other`: `-65`

## Nuove label introdotte
- `technical_writer` -> `content` (`17`)
- `story_editor` -> `content` (`19`)

## Regole aggiunte (precision)
- `content_technical_writer`
  - match solo su forma core: `technical writer` con opzionale seniority (`senior/staff/principal/lead/sr`) e level suffix (`I..V`)
- `content_story_desk_editor`
  - match esatto: `story desk editor`

## Guardrail rispettati
- nessun mapping generico di tutti i `writer`
- nessun mapping generico di tutti gli `editor`
- `Writer` generico non viene mappato a `technical_writer/story_editor` (`0`)

## Sample titoli coperti
- `Technical Writer` -> `technical_writer` (`17`)
- `Story Desk Editor` -> `story_editor` (`19`)

## Top residual `other` (post-v11)
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
13. `manager, software engineering` (18)
14. `cultivation associate` (18)
15. `k-5th grade teacher - sy 26-27` (17)
16. `leader in training` (17)
17. `outside sales representative - roofing` (17)
18. `technical support specialist` (16)
19. `data science manager` (16)
20. `principal engineer` (16)

## Cluster consigliato per v12
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Specialist ambiguity precision (`solution specialist`, `technical support specialist`)
3. Senior generic engineering ambiguity (`principal engineer`, `manager, software engineering`) con guardrail forti

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v11/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `25 passed`

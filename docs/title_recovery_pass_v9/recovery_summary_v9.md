# Title Coverage Recovery Pass v9 — Systems / Network Precision Pass

## Scope
Pass focalizzato solo sul cluster residuale `systems engineer` / `network engineer` con approccio precision-first.

## Before / After
- Total rows: `81,011`
- `other` before (v8): `41,526` (`51.26%`)
- `other` after (v9): `41,390` (`51.09%`)
- Delta `other`: `-136`

## Nuove label introdotte
- `systems_engineer` -> `it_operations` (`68`)
- `network_engineer` -> `it_operations` (`68`)

## Regole aggiunte (conservative)
- `infra_systems_engineer_core`
  - match solo su forma core: `systems engineer` con opzionale seniority (`senior/staff/principal/lead/sr`) e level suffix (`I..V`)
- `infra_network_engineer_core`
  - match solo su forma core: `network engineer` con stesso schema conservativo

## Guardrail rispettati
- nessun mapping generico di tutti gli `engineer`
- `senior firmware engineer` **non** mappato a `systems_engineer`/`network_engineer` (`0`)
- `business analyst` resta `other`
- `quantitative researcher` resta `other`
- `outside sales representative` resta `other`

## Sample titoli coperti
- `Senior Systems Engineer` -> `systems_engineer` (`25`)
- `Systems Engineer` -> `systems_engineer` (`18`)
- `Senior Network Engineer` -> `network_engineer` (`23`)
- `Network Engineer` -> `network_engineer` (`22`)

## Top residual `other` (post-v9)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `board certified behavior analyst` (20)
11. `solution specialist` (20)
12. `sonder responder` (19)
13. `restaurant general manager` (19)
14. `story desk editor` (19)
15. `manager, software engineering` (18)
16. `cultivation associate` (18)
17. `k-5th grade teacher - sy 26-27` (17)
18. `technical writer` (17)
19. `leader in training` (17)
20. `outside sales representative - roofing` (17)

## Cluster consigliato per pass v10
1. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
2. Residual healthcare precision (`board certified behavior analyst`, `personal care specialist`)
3. Writer/editor cluster (`technical writer`, `story desk editor`) con mapping mirato o mantenimento in `other` se ambiguo

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v9/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `24 passed`

# Title Coverage Recovery Pass v12 — Specialist Ambiguity Precision Pass

## Scope
Pass focalizzato solo sul cluster residuale specialist (`solution specialist`, `technical support specialist`) con regole strette e guardrail precision-first.

## Before / After
- Total rows: `81,011`
- `other` before (v11): `41,269` (`50.94%`)
- `other` after (v12): `41,229` (`50.89%`)
- Delta `other`: `-40`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso label esistenti per minimizzare complessità tassonomica:
- `technical support specialist` -> `it_support_specialist`
- `solution specialist` -> `sales_engineer`

## Regole aggiunte (precision)
- `it_support_specialist_core`
  - match solo su forma core: `technical support specialist` con opzionale seniority (`senior/staff/principal/lead/sr`) e suffix (`I..V`)
- `sales_solution_specialist_core`
  - match solo su forma core: `solution specialist` con opzionale seniority

## Guardrail rispettati
- nessun mapping generico di tutti gli `specialist`
- nessun allargamento largo di `it_support`
- nessun allargamento largo di `sales_engineer`
- `Support Specialist` generico non viene mappato a `it_support_specialist` (`0`)

## Sample titoli coperti
- `Technical Support Specialist` -> `it_support_specialist` (`16`)
- `Solution Specialist` -> `sales_engineer` (`20`)

## Top residual `other` (post-v12)
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
19. `auto body repair technician` (16)
20. `bilingual member services representative (remote, spanish speaking)` (16)

## Cluster consigliato per v13
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Senior engineering ambiguity (`principal engineer`, `manager, software engineering`) con guardrail forti
3. Service/operations tail (`member services representative`, `cultivation associate`) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v12/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `26 passed`

# Title Coverage Recovery Pass v4 — Education / Childcare Expansion

## Scope
Pass focalizzato solo su cluster education / childcare residuale, con regole conservative.

## Before / After
- Total rows: `81,011`
- `other` before (v3): `42,243` (`52.14%`)
- `other` after (v4): `42,186` (`52.07%`)
- Delta `other`: `-57`

## Nuove label introdotte
- Nessuna nuova label in questo pass.
- Riutilizzo label education esistenti: `teacher`, `assistant_teacher`.

## Regole aggiunte (conservative)
- `lead/preschool/infant/toddler teacher` -> `teacher`
- varianti `lead spanish preschool teacher` e `lead preschool spanish teacher` -> `teacher`
- `preschool|infant|toddler|early childhood` + `assistant teacher|teaching assistant|aide` -> `assistant_teacher`

## Guardrail precisione
- Nessun mapping largo di tutti i `teacher`
- Nessun mapping largo di tutti gli `assistant`
- Nessun mapping su `instructor`/`trainer` generici

## Sample titoli coperti
- `lead preschool teacher` -> `teacher` (25)
- `lead infant teacher` -> `teacher` (22)
- `lead spanish preschool teacher` -> `teacher` (2)
- `lead preschool spanish teacher` -> `teacher` (2)
- `infant assistant teacher` -> `assistant_teacher` (5)

## Top residual `other` (post-v4)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `social enterprise and program delivery-evergreen` (27)
7. `stylist (retail) (part-time)` (27)
8. `personal care specialist (part time)` (26)
9. `senior systems engineer` (25)
10. `floor lead (retail) (part-time)` (25)
11. `inside sales representative` (24)
12. `quantitative researcher` (24)
13. `senior network engineer` (23)
14. `network engineer` (22)
15. `mid-level automotive parts associate` (21)
16. `business analyst` (20)
17. `board certified behavior analyst` (20)
18. `field technician (mechanic) (pump, power & hvac)` (20)
19. `solution specialist` (20)
20. `senior people business partner` (19)

## Cluster consigliato per pass v5
1. Retail/service operations (`stylist retail`, `floor lead`, `restaurant manager`)
2. Industrial tail specifico (`field technician (mechanic) pump/power/hvac`, `automotive parts associate`)
3. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
4. Business/sales support residuo (`inside sales representative`, `business analyst`) con eventuale pass precisione dedicato

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v4/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `19 passed`

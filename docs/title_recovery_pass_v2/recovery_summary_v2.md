# Title Coverage Recovery Pass v2 — Industrial / Skilled Trades Expansion

## Scope
Pass focalizzato solo su cluster industrial / skilled trades / engineering non-software.

## Before / After
- Total rows: `81,011`
- `other` before (v1.1): `43,533` (`53.74%`)
- `other` after (v2): `42,514` (`52.48%`)
- Delta `other`: `-1,019`

## New labels introdotte
- `electrical_engineer` -> `industrial_engineering` (`198`)
- `mechanical_engineer` -> `industrial_engineering` (`273`)
- `manufacturing_engineer` -> `industrial_engineering` (`167`)

## Regole aggiunte (conservative)
- `electrical engineer` (+ senior/staff/principal/sr)
- `mechanical engineer` (+ senior/staff/principal/project/launch e suffix I..V)
- `manufacturing engineer` (+ senior/staff/principal/sr)
- `production technician`
- `auto technician / auto mechanic / automotive mechanic` (incluse varianti entry/mid/senior/master/lead e `brake and tire`)
- `maintenance technician` (incluse varianti `industrial/facilities/equipment/field service`)

## Sample titoli coperti
- `senior electrical engineer` -> `electrical_engineer` (28)
- `electrical engineer` -> `electrical_engineer` (24)
- `senior mechanical engineer` -> `mechanical_engineer` (26)
- `mechanical engineer` -> `mechanical_engineer` (21)
- `production technician` -> `technician` (27)
- `entry-level auto technician` -> `mechanic` (23)
- `brake and tire auto technician` -> `mechanic` (19)
- `maintenance technician` -> `technician` (18)
- `manufacturing engineer` -> `manufacturing_engineer` (18)

## Top residual `other` (post-v2)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `social enterprise and program delivery-evergreen` (27)
7. `stylist (retail) (part-time)` (27)
8. `personal care specialist (part time)` (26)
9. `licensed mental health therapist - remote` (26)
10. `senior systems engineer` (25)
11. `lead preschool teacher` (25)
12. `floor lead (retail) (part-time)` (25)
13. `per diem clinical research nurse - home visits` (25)
14. `inside sales representative` (24)
15. `quantitative researcher` (24)
16. `behavioral interventionist` (23)
17. `senior network engineer` (23)
18. `licensed practical nurse (lpn)` (23)
19. `network engineer` (22)
20. `medical assistant` (22)

## Next cluster consigliato (v3)
1. Healthcare support (`LPN`, `medical assistant`, `behavioral interventionist`, therapist variants)
2. Education / childcare (`lead preschool`, `lead infant`, aides)
3. Retail/service operations (`floor lead`, `stylist retail`, `restaurant manager`)
4. Industrial tail residuo specifico (`field technician (mechanic) pump/power/hvac`, `automotive parts associate`)

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v2/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `17 passed`

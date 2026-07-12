# Title Coverage Recovery Pass v3 — Healthcare Support Expansion

## Scope
Pass focalizzato solo su cluster healthcare support residuale, con regole conservative.

## Before / After
- Total rows: `81,011`
- `other` before (v2): `42,514` (`52.48%`)
- `other` after (v3): `42,243` (`52.14%`)
- Delta `other`: `-271`

## Nuove label introdotte
- `licensed_practical_nurse` -> `healthcare_clinical` (`67`)
- `medical_assistant` -> `healthcare_clinical` (`76`)

## Regole aggiunte (conservative)
- `licensed practical nurse` / `lpn` / `lvn` -> `licensed_practical_nurse`
- `clinical research nurse` -> `registered_nurse`
- `medical assistant` (escluso `medical assistant instructor`) -> `medical_assistant`
- `behavioral interventionist` -> `behavioral_support_specialist`
- `licensed mental health therapist` -> `psychotherapist`

## Sample titoli coperti
- `licensed practical nurse (lpn)` -> `licensed_practical_nurse` (23)
- `licensed practical nurse` -> `licensed_practical_nurse` (5)
- `medical assistant` -> `medical_assistant` (22)
- `behavioral interventionist` -> `behavioral_support_specialist` (23)
- `licensed mental health therapist - remote` -> `psychotherapist` (26)
- `licensed mental health therapist` -> `psychotherapist` (6)
- `per diem clinical research nurse - home visits` -> `registered_nurse` (25)

## Guardrail precisione
- Nessun mapping generico di tutti i `therapist`
- Nessun mapping generico di tutti gli `assistant`
- Nessun mapping generico di tutti i `nurse`

## Top residual `other` (post-v3)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `social enterprise and program delivery-evergreen` (27)
7. `stylist (retail) (part-time)` (27)
8. `personal care specialist (part time)` (26)
9. `senior systems engineer` (25)
10. `lead preschool teacher` (25)
11. `floor lead (retail) (part-time)` (25)
12. `inside sales representative` (24)
13. `quantitative researcher` (24)
14. `senior network engineer` (23)
15. `network engineer` (22)
16. `lead infant teacher` (22)
17. `mid-level automotive parts associate` (21)
18. `business analyst` (20)
19. `board certified behavior analyst` (20)
20. `field technician (mechanic) (pump, power & hvac)` (20)

## Cluster consigliato per pass v4
1. Education / childcare (`lead preschool`, `lead infant`, aide/instructor variants)
2. Retail/service operations (`stylist retail`, `floor lead`, `restaurant manager`)
3. Industrial tail specifico (`field technician (mechanic) pump/power/hvac`, `automotive parts associate`)
4. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v3/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `18 passed`

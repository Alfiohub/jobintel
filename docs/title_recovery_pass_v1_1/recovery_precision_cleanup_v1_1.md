# Title Coverage Recovery Pass v1.1 — Precision Cleanup

## Scope
Precision-only cleanup del recovery v1:
- riduzione overmatch
- mantenimento match ad alta confidenza
- nessuna espansione aggressiva

## Before / After (cleanup)
- Total rows: `81,011`
- `other` prima cleanup (v1): `42,487` (`52.45%`)
- `other` dopo cleanup (v1.1): `43,533` (`53.74%`)
- Delta netto cleanup: `+1,046` `other`

Nota: aumento di `other` atteso e voluto per recupero precisione.

## Regole ristrette/rimosse (overmatch)
1. `sales_management_cluster`
- rimosso mapping automatico di `inside sales representative` / `outside sales representative`

2. `data_quant_and_analyst_variants`
- rimossi:
  - `business analyst`
  - `quantitative researcher`
  - `data science manager`

3. `eng_systems_network_platform`
- rimossi:
  - `systems engineer` / `senior systems engineer`
  - `network engineer` / `senior network engineer`
  - `firmware engineer`

4. `sales_solution_specialist_consultant`
- rimosso `solution specialist`
- mantenuto `solutions consultant`

## Match sicuri mantenuti
- `solution architect` -> `solutions_architect` (23)
- `sales manager` -> `sales_manager` (18)
- `territory sales manager` -> `sales_manager` (18)
- `regional sales director` -> `sales_manager` (14)
- `platform engineer` -> `software_engineer` (17)
- `senior platform engineer` -> `software_engineer` (18)
- `cloud engineer` -> `software_engineer` (15)
- `senior infrastructure engineer` -> `software_engineer` (15)
- `servicenow developer` -> `software_engineer` (18)
- `operations manager` -> `operations_specialist` (24)
- `team lead, market operations` -> `operations_specialist` (21)
- `implementation consultant` -> `operations_specialist` (17)

## Top residual `other` (v1.1)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `senior electrical engineer` (28)
7. `production technician` (27)
8. `social enterprise and program delivery-evergreen` (27)
9. `stylist (retail) (part-time)` (27)
10. `senior mechanical engineer` (26)
11. `personal care specialist (part time)` (26)
12. `licensed mental health therapist - remote` (26)
13. `senior systems engineer` (25)
14. `lead preschool teacher` (25)
15. `floor lead (retail) (part-time)` (25)
16. `per diem clinical research nurse - home visits` (25)
17. `inside sales representative` (24)
18. `electrical engineer` (24)
19. `quantitative researcher` (24)
20. `behavioral interventionist` (23)

## Next expansion pass consigliato (non in questo cleanup)
1. Industrial / skilled trades (`electrical/mechanical/manufacturing/maintenance/auto technician`)
2. Healthcare support (`LPN`, `medical assistant`, `behavioral interventionist`, therapist variants)
3. Education/childcare (`lead preschool`, `lead infant`, aides)
4. Retail/service operations (`floor lead`, `stylist retail`, `restaurant manager`)

## Files changed in v1.1
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v1_1/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `16 passed`

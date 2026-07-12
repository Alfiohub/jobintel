# Title Coverage Recovery Pass v7 — Business / Sales Support Precision Expansion

## Scope
Pass focalizzato solo su business / sales support residuale, con priorità alla precisione.

## Before / After
- Total rows: `81,011`
- `other` before (v6): `41,968` (`51.81%`)
- `other` after (v7): `41,628` (`51.39%`)
- Delta `other`: `-340`

## Nuove label introdotte
- `people_business_partner` -> `people_operations` (`170`)

## Regole aggiunte (precision)
- `inside sales representative` (incluse varianti chiare) -> `account_executive`
- `solution engineer` (singolare) -> `sales_engineer`
- `people business partner` / `hr business partner` / `hrbp` -> `people_business_partner`

## Guardrail rispettati
- `business analyst` resta `other`
- `quantitative researcher` resta `other`
- `outside sales representative` resta `other`
- nessun allargamento di `sales_manager`
- nessun allargamento eccessivo di `sales_engineer`

## Sample titoli coperti
- `inside sales representative` -> `account_executive` (24)
- `inside sales representative (remote)` -> `account_executive` (6)
- `solution engineer` -> `sales_engineer` (19)
- `senior solution engineer` -> `sales_engineer` (5)
- `senior people business partner` -> `people_business_partner` (19)
- `people business partner` -> `people_business_partner` (14)
- `hr business partner` -> `people_business_partner` (14)

## Top residual `other` (post-v7)
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
11. `quantitative researcher` (24)
12. `senior network engineer` (23)
13. `network engineer` (22)
14. `business analyst` (20)
15. `board certified behavior analyst` (20)
16. `field technician (mechanic) (pump, power & hvac)` (20)
17. `solution specialist` (20)
18. `sonder responder` (19)
19. `restaurant general manager` (19)
20. `story desk editor` (19)

## Cluster consigliato per pass v8
1. Generic managerial/program titles (`general manager`, strategy/program evergreen) con regole conservative
2. Residual engineering ambiguity (`systems/network`) con pass precisione dedicato
3. Retail contextual recovery (dipende da conservazione del contesto pre-normalization)
4. Industrial contextual residual (`field technician (mechanic) (pump/power/hvac)`) se si preservano i token tra parentesi

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v7/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `22 passed`

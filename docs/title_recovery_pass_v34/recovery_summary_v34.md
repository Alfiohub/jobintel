# Title Coverage Recovery Pass v34 — Software Development Engineer Variants Pass

## Cluster scelto
`software_development_engineer_variants` (forme core `software development engineer` / `software development engineer in test` / `sdet`, con varianti strette di seniority/level).

## Before / After
- Total rows: `81,011`
- `other` before (v33): `39,027` (`48.18%`)
- `other` after (v34): `38,811` (`47.91%`)
- Delta `other`: `-216`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: mapping su label esistente:
- `software_engineer` -> `software_engineering`

## Regole aggiunte (precision)
- `eng_software_development_engineer_variants_v34`
  - pattern stretti su:
    - `software development engineer`
    - `software development engineer in test`
    - varianti seniority (`senior|staff|principal|lead|junior|sr|jr`)
    - level suffix (`I..V`, `L*`)
    - `sdet` (incluse varianti con suffisso, es. `SDET-Playwright`)

## Coverage (nuova regola)
- `eng_software_development_engineer_variants_v34`: `216`
- totale nuovi match v34: `216`

## Sample titoli coperti
- `Software Development Engineer in Test` (`12`)
- `Staff Software Development Engineer` (`10`)
- `Principal Software Development Engineer` (`8`)
- `Senior Software Development Engineer` (`6`)
- `Software Development Engineer III` (`5`)
- `Software Development Engineer in Test (SDET)` (`4`)
- `SDET` (`3`)
- `SDET-Playwright` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `engineer`
- nessun allargamento su `systems engineer` / `network engineer` / `firmware engineer`
- contesto obbligatorio su `software development engineer`/`sdet`
- esclusi pattern manageriali/ambigui (es. `Manager - Software Development Engineering`)

## Varianti lasciate volutamente in `other`
- `Manager - Software Development Engineering` (`2`)
- `Manager, Software Development Engineering` (`1`)
- `Senior Manager, Software Development Engineering` (`1`)
- `Director, Software Development Engineering ...` (`1`)
- `Sr Staff Software Development Engineering` (`1`)

Motivo: out-of-scope rispetto al cluster engineer individual contributor; rischio overlap con leadership/manageriali.

## Top residual `other` (post-v34)
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

## Cluster consigliato per v35
1. `support_engineer_it_support` (IT support engineer/support specialist) con pattern stretti e anti-overlap su support engineer tecnico di prodotto.
2. `freelance_ai_trainer_specialists` (alto ROI) con scelta esplicita se creare label dedicata o mantenere `other` per policy prodotto.
3. `compliance_risk` edge su governance/controls non-engineering (pattern molto conservativi).

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v34/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v34.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `41 passed`

# Title Coverage Recovery Pass v45 — Systems Administrator Variants

## Cluster scelto
`systems administrator` variants (`Systems Administrator`, `System Administrator`, varianti seniority/IT/Linux).

## Before / After
- Total rows: `81,011`
- `other` before (v44): `37,031` (`45.71%`)
- `other` after (v45): `36,950` (`45.61%`)
- Delta `other`: `-81`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `it_support_specialist` -> `it_operations`

## Regola aggiunta (precision)
- `it_systems_administrator_core_v45`
  - pattern core: `system administrator` / `systems administrator`
  - include varianti strette (seniority, IT/Linux/cloud/business/clinical)
  - esclusione esplicita manageriale: nessun match se presente `manager`

## Coverage (nuova regola)
- `it_systems_administrator_core_v45`: `82` hit
- varianti systems-admin in `other` prima: `83`
- varianti systems-admin in `other` dopo: `2`

## Sample titoli coperti
- `Systems Administrator` (`6`)
- `System Administrator` (`5`)
- `Lead System Administrator` (`4`)
- `Senior Systems Administrator` (`3`)
- `IT Systems Administrator, Launch` (`3`)
- `Linux Systems Administrator` (`2`)
- `Cloud System Administrator` (`1`)
- `Business Systems Administrator II` (`1`)
- `Clinical System Administrator II` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `administrator`
- contesto obbligatorio su `system(s) administrator`
- esclusi per regola i casi manageriali (`manager` nel titolo)
- test negativi su:
  - `Database Administrator`
  - `Network Administrator`
  - `Office Administrator`
  - `Project Administrator`
  - `Manager, Salesforce & Systems Administrator`

## Varianti lasciate volutamente in `other`
- `Manager, Salesforce & Systems Administrator` (`1`) — contiene componente manageriale
- `System Administrator - Asset Manager` (`1`) — contiene contesto manageriale ambiguo

## Top residual `other` (post-v45)
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

## Cluster consigliato per il pass successivo
1. `producer` event-edge (`Sr. Producer, General Session`, `Sr. Producer, Trade Shows`) con pattern stretti.
2. `support engineer` con contesto IT stretto, evitando customer/product support ambiguo.
3. `business systems` edge (solo pattern altamente disambiguati) se ROI confermato.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v45/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v45.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `51 passed`

# Title Coverage Recovery Pass v38 — Tech Lead Core Product Cluster

## Cluster scelto
`tech_lead_core_product_cluster` con pattern stretto su:
- `Tech Lead, Android Core Product`
- `Tech Lead, Web Core Product & Chrome Extension`
- varianti con suffisso location (`- City, Country`).

## Before / After
- Total rows: `81,011`
- `other` before (v37): `38,673` (`47.74%`)
- `other` after (v38): `38,008` (`46.92%`)
- Delta `other`: `-665`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `software_engineer` -> `software_engineering`

## Regola aggiunta (precision)
- `eng_tech_lead_core_product_v38`
  - core richiesto: `tech lead` + `(android|web|mobile)` + `core product`
  - opzionale: `& chrome extension`
  - opzionale: coda location (`- ...`)

## Coverage (nuova regola)
- `eng_tech_lead_core_product_v38`: `647`

## Sample titoli coperti
- `Tech Lead, Android Core Product` (`2`)
- `Tech Lead, Android Core Product - Berlin, Germany` (`2`)
- `Tech Lead, Android Core Product - Bangkok, Thailand` (`2`)
- `Tech Lead, Web Core Product & Chrome Extension` (`2`)
- `Tech Lead, Web Core Product & Chrome Extension - Concord, USA` (`2`)

## Guardrail rispettati
- nessun mapping generico di tutti i `tech lead`
- contesto forte obbligatorio: `android|web|mobile` + `core product`
- esclusi pattern generici `team lead`, `technical lead`, `lead engineer`
- test negativi specifici su:
  - `Team Lead, Android Core Product`
  - `Technical Lead, Web Core Product`
  - `Lead Engineer, Web Core Product & Chrome Extension`
  - `Tech Lead, Data Platform`
  - `Tech Lead, Android`

## Varianti lasciate volutamente in `other`
- `Staff Engineer - Web Tech Lead, GeminiApp - Mountain View`
- `Tech Lead - Web Platform`
- `Staff Engineer, Mobile - Tech Lead`
- `Tech Lead Manager - Mobile`

Motivo: non rispettano il pattern core `tech lead + ... core product` oppure sono ruoli manageriali/strutturati diversi.

## Top residual `other` (post-v38)
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
1. `design_creative` edge su `producer` contestuale forte (`video/content/editorial`), mantenendo `producer` nudo in `other`.
2. `customer_service` micro-edge su `customer care advisor/executive` con esclusione IT/technical.
3. `compliance_risk` micro-edge finance-regulatory (`grc analyst/consultant`) con pattern chiusi.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v38/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v38.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `44 passed`

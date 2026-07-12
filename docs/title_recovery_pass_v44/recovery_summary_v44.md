# Title Coverage Recovery Pass v44 — Human Resources Business Partner Variants

## Cluster scelto
`human_resources_business_partner` variants (`Human Resources Business Partner` e varianti strette).

## Before / After
- Total rows: `81,011`
- `other` before (v43): `37,068` (`45.76%`)
- `other` after (v44): `37,031` (`45.71%`)
- Delta `other`: `-37`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `people_business_partner` -> `people_operations`

## Regola aggiornata
- `people_business_partner`
  - estesa con pattern: `human resources? business partner`
  - mantiene match esistenti su `people business partner`, `hr business partner`, `hrbp`

## Coverage (v44)
- varianti HRBP in `other` prima: `37`
- varianti HRBP in `other` dopo: `0`
- hit cluster HRBP via regola `people_business_partner`: `37`

## Sample titoli coperti
- `Human Resources Business Partner` (`12`)
- `Senior Human Resources Business Partner` (`6`)
- `Human Resource Business Partner, IL` (`4`)
- `Sr. Human Resources Business Partner` (`2`)
- `Human Resources Business Partner (HRBP), GTM` (`1`)
- `Director, Human Resources Business Partner` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `business partner`
- contesto forte obbligatorio: `human resource(s)` / `hr`
- nessun allargamento a business partner non-HR
- test negativi su:
  - `Finance Business Partner`
  - `Commercial Business Partner`
  - `Business Partner`

## Varianti lasciate volutamente in `other`
- cluster manageriali generici (es. `General Manager`)
- cluster analitici ambigui (`Business Analyst`, `Quantitative Researcher`)
- producer nudo e producer ambigui non contestuali

## Top residual `other` (post-v44)
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
2. `systems administrator` (`system(s) administrator`) con decisione tassonomica conservativa.
3. `support engineer` variants con contesto IT forte, evitando customer/product support ambiguo.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v44/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v44.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `50 passed`

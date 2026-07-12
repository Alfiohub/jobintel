# Title Coverage Recovery Pass v43 — Insurance Producer Geo Cluster

## Cluster scelto
`insurance_producer_geo_cluster` (pattern uniforme `Insurance Producer - <city/state>`).

## Before / After
- Total rows: `81,011`
- `other` before (v42): `37,279` (`46.02%`)
- `other` after (v43): `37,068` (`45.76%`)
- Delta `other`: `-211`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `account_executive` -> `sales`

## Regola aggiunta (precision)
- `sales_insurance_producer_geo_edge_v43`
  - forma core: `insurance producer`
  - supporta varianti location-tail (`- city, state`) e prefisso `Copy of ...`
  - non allargata a `producer` generico

## Coverage (nuova regola)
- `sales_insurance_producer_geo_edge_v43`: `211`
- `insurance producer` in `other` prima: `211`
- `insurance producer` in `other` dopo: `0`

## Sample titoli coperti
- `Insurance Producer - Atlanta, GA` (`1`)
- `Insurance Producer - Tucson, AZ` (`2`)
- `Insurance Producer - Grand Rapids, MN` (`2`)
- `Insurance Producer- Alexandria, LA` (`1`)
- `Insurance Producer -Asheboro, NC` (`1`)
- `Copy of Insurance Producer -Asheville, NC` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `producer`
- contesto forte obbligatorio: `insurance producer`
- esclusi per costruzione:
  - `producer` nudo
  - `content/creative/news producer`
  - `insurance sales manager` / titoli manageriali non equivalenti

## Varianti lasciate volutamente in `other`
- `Producer` (`27`) (nudo e ambiguo)
- `Senior Outsourcing Producer` (`2`) (ambiguità funzione)
- `Staff Technical Producer` (`1`) (ambiguità tech/content)
- `Insurance Sales Manager` e affini (manageriale, non `producer` core)

## Top residual `other` (post-v43)
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
1. `human_resources_business_partner` variant edge (`Human Resources Business Partner`) -> mapping stretto su `people_business_partner`.
2. `producer` event-edge (`general session`, `trade shows`) con pattern stretti e anti-overmatch.
3. `systems administrator` cluster (`system(s) administrator`) con decisione tassonomica conservativa.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v43/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v43.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `49 passed`

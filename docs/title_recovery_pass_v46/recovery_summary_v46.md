# Title Coverage Recovery Pass v46 — Mobile Engineer Android/iOS

## Cluster scelto
`mobile_engineer_android_ios` (`Android Engineer`, `iOS Engineer`, `Mobile Engineer` e varianti strette).

## Before / After
- Total rows: `81,011`
- `other` before (v45): `36,950` (`45.61%`)
- `other` after (v46): `36,788` (`45.41%`)
- Delta `other`: `-162`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `software_engineer` -> `software_engineering`

## Regola aggiunta (precision)
- `eng_mobile_engineer_android_ios_v46`
  - pattern forte: presenza di `android|ios|mobile` in combinazione con `engineer`
  - include varianti strette d’ordine (`mobile iOS engineer`, `engineer, mobile`)
  - non allargata a `engineer` generico

## Coverage
- hit regola nuova: `523`
- cluster mobile in `other` prima: `145`
- cluster mobile in `other` dopo: `0`

Nota: molti hit erano già classificati come `software_engineer` da altre regole; il delta netto su `other` è `-162`.

## Sample titoli coperti
- `Android Engineer` (`13`)
- `Senior Android Engineer` (`11`)
- `iOS Engineer` (`7`)
- `Senior iOS Engineer` (`10`)
- `Mobile Engineer (LATAM)` (`8`)
- `Senior Mobile Engineer (React Native)` (`4`)
- `Mobile iOS Engineer` (`2`)
- `(1368) Lead iOS Mobile Engineer` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti gli `engineer`
- contesto obbligatorio `android|ios|mobile`
- esclusi nei test:
  - `Principal Engineer`
  - `Senior Engineer`
  - `Senior Firmware Engineer`
  - `Network Engineer`
  - `Systems Engineer`
  - `Mobile Product Manager`

## Varianti lasciate volutamente in `other`
- Nessuna variante del cluster target (`android|ios|mobile engineer`) resta in `other`.
- Restano in `other` i cluster generici/ambigui non in scope (es. manageriali generici, business analyst, producer nudo).

## Top residual `other` (post-v46)
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
1. `support_engineer` con contesto IT stretto (`Support Engineer`, `L2/L3`) e guardrail anti customer/product support.
2. `producer` event-edge (`Sr. Producer, General Session`, `Sr. Producer, Trade Shows`) con pattern chiusi.
3. `corporate_paralegal` (cluster piccolo ma semanticamente pulito) con decisione tassonomica conservativa.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v46/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v46.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `52 passed`

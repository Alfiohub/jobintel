# Title Coverage Recovery Pass v19 — Customer Service / Member Services Expansion

## Scope
Pass focalizzato solo su `customer_service` residuale, con espansione pragmatica e controllata su sottocluster customer/member service espliciti.

## Before / After
- Total rows: `81,011`
- `other` before (v18): `39,984` (`49.36%`)
- `other` after (v19): `39,892` (`49.24%`)
- Delta `other`: `-92`

## Customer Service Cluster Delta
- `customer_service` residual before (v18): `197`
- `customer_service` residual after (v19): `130`
- Delta customer_service residual: `-67`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `customer_service_specialist` -> `operations`

## Regole aggiunte (sottocluster high-ROI)
- `customer_member_services_representative` -> `customer_service_specialist`
  - `member service(s) representative|advocate`
- `customer_service_frontline_representative` -> `customer_service_specialist`
  - `customer service advisor|associate|specialist|executive`
  - `client service representative`
  - `call center representative|agent`
- `customer_support_frontline_representative` -> `customer_service_specialist`
  - `customer support agent|associate|advocate`

## Guardrail rispettati
- nessun mapping generico di tutti i `representative`
- nessun mapping generico di tutti i `support`
- contesto richiesto forte (`customer service`, `member services`, `customer support`, `call center`, `client service representative`)
- esclusi pattern ambigui/tecnici su `support` (es. `Customer Support Engineer`, `Customer Support Manager`, `Director, Customer Support`)

## Coverage (nuove regole)
- `customer_support_frontline_representative`: `43`
- `customer_service_frontline_representative`: `30`
- `customer_member_services_representative`: `19`
- totale nuovi match v19 (customer-service focused): `92`

## Sample titoli coperti
- `Bilingual Member Services Representative (Remote, Spanish Speaking)` -> `customer_service_specialist` (`16`)
- `Member Services Representative (Temporary) (Bilingual Spanish)` -> `customer_service_specialist` (`2`)
- `Customer Service Advisor` -> `customer_service_specialist` (`5`)
- `Client Service Representative` -> `customer_service_specialist` (`4`)
- `Customer Support Agent - Freelance Project` -> `customer_service_specialist` (`5`)
- `Customer Support Associate, Bilingual - Greek (Starlink)` -> `customer_service_specialist` (`3`)
- `Customer Support Advocate (French Speaking)` -> `customer_service_specialist` (`1`)
- `Call Center Representative (Appointment Setter)` -> `customer_service_specialist` (`1`)

## Top residual `other` (post-v19)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `sonder responder` (19)
11. `restaurant general manager` (19)
12. `manager, software engineering` (18)
13. `cultivation associate` (18)
14. `leader in training` (17)
15. `outside sales representative - roofing` (17)
16. `data science manager` (16)
17. `principal engineer` (16)
18. `intelligence operations integrator` (16)
19. `senior firmware engineer` (15)
20. `manager, paid social` (15)

## Customer-service residual ancora scoperti (top)
- `Client Service Associate` (8)
- `Customer Support Engineer` (7)
- `Customer Support L2 Project - Freelance Project` (5)
- `Customer Support Manager` (4)
- `Member Services Coordinator` (4)
- `Client Services Manager` (4)
- `Customer Service Coordinator - Vehicle Delivery` (3)
- `Technical Customer Support Engineer - EMEA` (3)
- `Senior Client Services Manager, Enterprise` (3)
- `Senior Client Services Manager, Growth` (3)

## Cluster consigliato per v20
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Customer-service edge precision (`client service associate`, `member services coordinator`) con regole strette
3. Engineering-leadership ambiguity (`manager, software engineering`, `principal engineer`) con guardrail forti

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v19/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v19.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `33 passed`

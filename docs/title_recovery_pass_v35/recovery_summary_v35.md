# Title Coverage Recovery Pass v35 — Support Engineer / IT Support Pass

## Cluster scelto
`support_engineer_it_support` (sottocluster ad alta chiarezza su `IT support engineer/specialist/analyst/technician` con contesto IT esplicito).

## Before / After
- Total rows: `81,011`
- `other` before (v34): `38,811` (`47.91%`)
- `other` after (v35): `38,728` (`47.81%`)
- Delta `other`: `-83`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `it_support_specialist` -> `it_operations`

## Regole aggiunte (precision)
- `it_support_engineer_it_context_v35`
  - pattern stretti su: `it support engineer`, `desktop support engineer`, `linux support engineer`, `network support engineer`
- `it_support_specialist_it_context_v35`
  - pattern stretti su: `it support specialist`, `it support analyst`, `it support technician`, `it support lead/team lead`, `executive it support`

## Coverage (nuove regole)
- `it_support_engineer_it_context_v35`: `31`
- `it_support_specialist_it_context_v35`: `52`
- totale nuovi match v35: `83`

## Sample titoli coperti
- `IT Support Engineer` (`13`)
- `Desktop Support Engineer` (`3`)
- `Network Support Engineer` (`2`)
- `IT Support Specialist` (`12`)
- `IT Support Technician` (`5`)
- `IT Support Analyst` (`4`)
- `IT Support Team Lead` (`2`)
- `Executive IT Support` (`2`)

## Guardrail rispettati
- nessun mapping generico di tutti i `support engineer`
- nessun mapping generico di tutti i `support specialist`
- contesto IT forte obbligatorio (`it`, `desktop`, `linux`, `network` + support)
- nessun allargamento su `customer support` / `product support` generici
- nessun allargamento su manageriali (`IT Support Manager` resta fuori)

## Varianti lasciate volutamente in `other`
- `Support Engineer` (`11`)
- `Senior Support Engineer` (`9`)
- `Customer Support Engineer` (`7`)
- `Product Support Specialist` (`11`)
- `Product Support Engineer` (`3`)
- `Support Specialist` (`4`)
- `IT Support Manager` (`5`)
- `Senior Manager, Technical Services & IT Support` (`3`)

Motivo: pattern troppo ambigui o manageriali; rischio overlap con customer support/product support.

## Top residual `other` (post-v35)
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

## Cluster consigliato per v36
1. `customer_service` edge su `client support specialist` / `support specialist` contestuali non-IT con guardrail anti-overmatch.
2. `compliance_risk` governance/controls edge (`operational controls`, `compliance execution`) con pattern stretti non-engineering.
3. `design_creative` edge su `producer` contestuale forte (video/content/editorial), lasciando `producer` nudo in `other`.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v35/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v35.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `42 passed`

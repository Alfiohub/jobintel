# Title Coverage Recovery Pass v17 — Logistics Expansion

## Scope
Pass focalizzato solo su `logistics` residuale ad alto volume, con espansione pragmatica e controllata su sottocluster logistici espliciti.

## Before / After
- Total rows: `81,011`
- `other` before (v16): `40,241` (`49.67%`)
- `other` after (v17): `40,073` (`49.47%`)
- Delta `other`: `-168`

## Logistics Cluster Delta
- `logistics` residual before (v16): `503`
- `logistics` residual after (v17): `414`
- Delta logistics residual: `-89`

## Nuove label introdotte
- `logistics_coordinator` -> `logistics`
- `warehouse_associate` -> `logistics`
- `supply_chain_specialist` -> `logistics`
- `logistics_manager` -> `logistics`

## Regole aggiunte (sottocluster high-ROI)
- `logistics_core_coordinator_specialist` -> `logistics_coordinator`
  - logistics coordinator/specialist/associate, dispatcher, transportation administrator
- `logistics_warehouse_inventory_materials` -> `warehouse_associate`
  - warehouse associate/specialist/manager/technician, inventory associate/specialist/coordinator/lead, material handler/planner/specialist/technician, receiving associate
- `logistics_supply_chain_explicit` -> `supply_chain_specialist`
  - supply chain specialist/manager/intern, director/head of supply chain, staff supply chain planner
- `logistics_manager_explicit` -> `logistics_manager`
  - logistics manager/global logistics manager, warehouse & fleet manager, selected delivery management titles

## Guardrail rispettati
- nessun mapping generico di tutti i `coordinator`
- nessun mapping generico di tutti gli `associate`
- contesto richiesto forte (`logistics`, `warehouse`, `inventory`, `material`, `supply chain`, `dispatch`, `transportation`)
- esclusi pattern ambigui/tech su `delivery` (es. `Technical Delivery Manager`, `Project Delivery Lead`)

## Coverage (nuove regole)
- `logistics_warehouse_inventory_materials`: `91`
- `logistics_core_coordinator_specialist`: `35`
- `logistics_supply_chain_explicit`: `30`
- `logistics_manager_explicit`: `12`
- totale nuovi match v17 (logistics-focused): `168`

## Sample titoli coperti
- `Logistics Coordinator` -> `logistics_coordinator` (`10`)
- `Warehouse Associate` -> `warehouse_associate` (`13`)
- `Inventory Specialist` -> `warehouse_associate` (`3`)
- `Supply Chain Specialist` -> `supply_chain_specialist` (`8`)
- `Supply Chain Manager` -> `supply_chain_specialist` (`5`)
- `Dispatcher` -> `logistics_coordinator` (`5`)

## Top residual `other` (post-v17)
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
14. `k-5th grade teacher - sy 26-27` (17)
15. `leader in training` (17)
16. `outside sales representative - roofing` (17)
17. `data science manager` (16)
18. `principal engineer` (16)
19. `bilingual member services representative (remote, spanish speaking)` (16)
20. `intelligence operations integrator` (16)

## Logistics residual ancora scoperti (top)
- `Technical Delivery Manager` (9)
- `Staff Cloud Architect (Delivery) - EMEA` (6)
- `AVP, Delivery Partnerships` (5)
- `Delivery Manager` (5)
- `Inventory Technician` (4)
- `Licensed Transportation Engineer - Roadway` (4)
- `Senior Construction Materials Testing Technician` (4)
- `Transportation Engineer (EIT) - Roadway` (4)
- `Senior Transportation Project Engineer` (4)
- `Manager, Delivery Excellence` (3)

## Cluster consigliato per v18
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Logistics edge pass su delivery-business vs delivery-engineering (pattern stretti)
3. Engineering leadership ambiguity (`manager, software engineering`, `principal engineer`) con guardrail forti

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v17/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `31 passed`

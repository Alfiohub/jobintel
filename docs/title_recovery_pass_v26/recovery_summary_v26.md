# Title Coverage Recovery Pass v26 — Creative Production / Producer Context Pass

## Cluster scelto
`design_creative` / `content` residuale su titoli `producer` con contesto forte.

## Before / After
- Total rows: `81,011`
- `other` before (v25): `39,364` (`48.59%`)
- `other` after (v26): `39,273` (`48.48%`)
- Delta `other`: `-91`

## Nuove label introdotte
- `content_producer` -> `content`

## Regole aggiunte
- `content_producer_context_core`
  - producer con contesto `video|content|digital|social|news|newscast|story|web|anime|gaming|localization|sports|comm`
- `content_producer_creative_event_core`
  - producer con contesto `creative|event|live event|live experience`
- `content_producer_senior_exec_core`
  - forme core `executive producer` / `senior producer` (incluse varianti con suffisso)

## Coverage (nuove regole)
- `content_producer_context_core`: `54`
- `content_producer_creative_event_core`: `22`
- `content_producer_senior_exec_core`: `17`
- totale nuovi match v26: `93`

## Sample titoli coperti
- `Editing AI Content Producer` (`6`)
- `Executive Producer` (`6`)
- `News Producer` (`5`)
- `Creative Producer` (`4`)
- `Associate Event Producer` (`3`)
- `Social Video Producer` (`2`)
- `Newscast Producer` (`2`)
- `Video Producer, Product Launches` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `producer`
- nessun mapping generico di tutti gli `editor`
- contesto forte richiesto per matching producer
- test negativi su `Producer` generico e `Insurance Producer ...`

## Nota esplicita sui producer generici rimasti in `other`
- `Producer` (titolo nudo): **27** occorrenze, volutamente mantenute in `other`.
- `producer` residuali totali in `other`: `374 -> 283` (delta `-91`).

## Top residual `other` (post-v26)
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

## Cluster consigliato per v27
1. `skilled_trades` precision su sottocluster tecnici non-IT ad alta frequenza
2. `compliance_risk` edge (KYC/compliance onboarding, internal audit specific)
3. `customer_service` edge (client service associate / member services coordinator con contesto forte)

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v26/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v26.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `35 passed`

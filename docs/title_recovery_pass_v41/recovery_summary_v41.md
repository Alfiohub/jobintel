# Title Coverage Recovery Pass v41 — Freelance AI Trainer Non-Specialist Edge

## Cluster scelto
`freelance_ai_trainer` non-specialist (`... - Freelance AI Trainer Project` senza token `specialist`).

## Before / After
- Total rows: `81,011`
- `other` before (v40): `37,408` (`46.18%`)
- `other` after (v41): `37,301` (`46.04%`)
- Delta `other`: `-107`

## Nuove label introdotte
- `ai_trainer_generalist` -> `operations`

## Modellazione scelta (compatta)
Scelta: mantenere famiglia `freelance_ai_trainer` in **2 sole label**:
- `ai_trainer_specialist` (v40)
- `ai_trainer_generalist` (v41)

Razionale:
- i non-specialist hanno pattern uniforme e forte (`freelance ai trainer project`)
- evitare mapping forzati verso ruoli classici non coerenti
- tassonomia compatta, leggibile, testabile

## Regola aggiunta
- `ops_ai_trainer_non_specialist_family_v41`
  - pattern: presenza di `freelance ai trainer project`
  - esclusione esplicita: `specialist` (già coperto dalla regola v40)
  - output: `ai_trainer_generalist`

## Coverage
- hit regola nuova: `107`
- `freelance ai trainer` non-specialist in `other` (v40): `107`
- `freelance ai trainer` non-specialist in `other` (v41): `0`

## Sample titoli coperti
- `Social Media Annotation - Freelance AI Trainer Project` (`6`)
- `Voice Actor - Freelance AI Trainer Project` (`5`)
- `American Sign Language (ASL) - Freelance AI Trainer Project` (`3`)
- `Japanese Translator - Freelance AI Trainer Project` (`3`)
- `Armenian Language Expert - Freelance AI Trainer Project` (`2`)
- `AI Generalist (No Experience Required) - Freelance AI Trainer Project` (`1`)

## Guardrail rispettati
- nessuna label per singola lingua/micro-dominio
- nessun mapping forzato a `translator`/`teacher`/`engineer`
- contesto obbligatorio: `freelance ai trainer project`
- esclusione esplicita dei `specialist` (coperti separatamente)

## Varianti lasciate volutamente in `other`
- Nessuna variante `freelance ai trainer` non-specialist resta in `other`.
- Rimangono invece i cluster storicamente ambigui/non-prioritari (es. manageriali generici, analyst generici).

## Top residual `other` (post-v41)
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

## Cluster consigliato per v42
1. `design_creative` edge su `producer` contestuale forte (evitando `producer` nudo).
2. `skilled_trades` edge non-IT ad alta frequenza con pattern stretti.
3. `compliance_risk` micro-edge ad alta precisione (solo pattern forti).

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v41/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v41.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `47 passed`

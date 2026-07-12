# Title Coverage Recovery Pass v40 — Freelance AI Trainer Specialists Family

## Cluster scelto
`freelance_ai_trainer_specialists` (pattern forte: `... Specialist - Freelance AI Trainer Project`).

## Before / After
- Total rows: `81,011`
- `other` before (v39): `37,996` (`46.90%`)
- `other` after (v40): `37,408` (`46.18%`)
- Delta `other`: `-588`

## Nuove label introdotte
- `ai_trainer_specialist` -> `operations`

## Modellazione scelta (compatta)
Scelta: **1 sola label di famiglia** (`ai_trainer_specialist`), invece di decine/centinaia di label per lingua o dominio.

Razionale:
- cluster altamente uniforme (stesso suffix `Freelance AI Trainer Project` + `Specialist`)
- forte volume (`587` righe in `other` su baseline v39)
- tassonomia leggibile e stabile
- evita mapping forzati a ruoli classici non corretti (`translator`, `teacher`, `engineer`)

## Regola aggiunta
- `ops_ai_trainer_specialist_family_v40`
  - pattern stretto: `freelance ai trainer project` + `specialist` (in qualunque ordine)
  - output: `ai_trainer_specialist`

## Coverage
- hit regola nuova: `596`
- titoli della famiglia in `other` (baseline v39): `587`
- titoli della famiglia in `other` (v40): `0`

Nota: parte degli hit (`9`) era già classificata come non-`other`; per questo il delta netto su `other` è `-588`.

## Sample titoli coperti
- `Garment Manufacturing QC Specialist - Freelance AI Trainer Project` (`12`)
- `Geospatial Reasoning Specialist (Senior) - Freelance AI Trainer Project` (`11`)
- `German Language Specialist - Freelance AI Trainer Project` (`9`)
- `Pavement Condition Index (PCI) Survey & Annotation Specialist - Freelance AI Trainer Project` (`8`)
- `Kotlin Coding Specialist - Freelance AI Trainer Project` (`7`)
- `Audio Editing Specialist - Freelance AI Trainer Project` (`4`)

## Guardrail rispettati
- nessuna label per singola lingua/dominio
- nessun mapping generico di tutti i `specialist`
- contesto obbligatorio: `freelance ai trainer project`
- nessun forcing verso family errate (`translator`/`teacher`/`engineer`)

## Varianti lasciate volutamente in `other`
Rimangono `other` le varianti **senza** token `specialist`.

Esempi:
- `Social Media Annotation - Freelance AI Trainer Project` (`6`)
- `Voice Actor - Freelance AI Trainer Project` (`5`)
- `American Sign Language (ASL) - Freelance AI Trainer Project` (`3`)
- `Japanese Translator - Freelance AI Trainer Project` (`3`)
- `AI Generalist (No Experience Required) - Freelance AI Trainer Project` (`1`)

## Top residual `other` (post-v40)
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

## Cluster consigliato per v41
1. `freelance_ai_trainer` **non-specialist edge** (`voice actor`, `annotation`, `language expert`) con regole strette e family compatta.
2. `design_creative` edge su `producer` contestuale forte (non `producer` nudo).
3. `skilled_trades` edge non-IT ad alta frequenza (solo pattern stretti).

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v40/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v40.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `46 passed`

# Title Coverage Recovery Pass v42 — Producer Contextual Cluster

## Cluster scelto
`producer` contestuale in area content/creative (broadcast/video/game/commercial), con pattern stretti.

## Before / After
- Total rows: `81,011`
- `other` before (v41): `37,301` (`46.04%`)
- `other` after (v42): `37,279` (`46.02%`)
- Delta `other`: `-22`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `content_producer` -> `content`

## Regola aggiunta (precision)
- `content_producer_contextual_edge_v42`
  - richiede `producer` + contesto forte (`morning|show|streaming|commercial|videographer|video|host|casting|conference|shoot|editor|game|live operations|features|central desk`)
  - esclusioni esplicite: `insurance`, `p&c`, `sales`

## Coverage (nuova regola)
- `content_producer_contextual_edge_v42`: `22`
- `producer` in `other` prima: `283`
- `producer` in `other` dopo: `261`

## Sample titoli coperti
- `Morning Executive Producer` (`2`)
- `Lead Producer, Live Operations` (`1`)
- `Streaming Producer, TEGNA Central Desk` (`1`)
- `Morning Show Producer` (`1`)
- `Commercial Producer` (`1`)
- `Videographer - Producer` (`1`)
- `Producer - Editor` (`1`)
- `Senior Conference Producer` (`1`)
- `Lead Game Producer` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `producer`
- contesto forte obbligatorio per il match
- esclusi esplicitamente `insurance producer` e producer sales-oriented (`p&c sales producer`)
- `producer` nudo resta `other`

## Varianti lasciate volutamente in `other`
- `Producer` (`27`) (nudo, ambiguo)
- `Insurance Producer ...` (serie location-based, fuori scope content)
- `Senior Outsourcing Producer` (`2`) (ambiguità funzione)
- `Staff Technical Producer` (`1`) (ambiguità tech/content)
- `Sr. Producer, General Session` / `Sr. Producer, Trade Shows` (event cluster da trattare separatamente se serve)

## Top residual `other` (post-v42)
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

## Cluster consigliato per v43
1. `producer` event-edge (`general session`, `trade shows`) con pattern stretti e anti-overmatch.
2. `skilled_trades` non-IT edge ad alta chiarezza.
3. `compliance_risk` micro-edge ad alta precisione.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v42/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v42.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `48 passed`

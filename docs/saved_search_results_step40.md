# Saved Search Results Surface / Daily Workflow v1 (Step 40)

## Obiettivo
Trasformare la singola saved search in una superficie operativa quotidiana, non solo CRUD.

## Nuova pagina Admin
Endpoint UI:
- `GET /admin/saved-searches/{search_id}`

La pagina mostra:
- metadata saved search (`name`, `query_type`, `enabled`, `pack_name`/`filters_json`, `created_at`, `updated_at`, `last_run_at`)
- count risultati correnti (`current_count`)
- count nuovi match (`new_count`, quando in modalità new)
- risultati paginati con:
  - `job_state`
  - azioni rapide: `Seen`, `Save`, `Dismiss`, `Reset`

## Modalità risultati
Query param principali:
- `mode=current|new`
- `limit`
- `offset`
- `scan_limit` (usato in `mode=new`)

Comportamento:
- `mode=current`: mostra risultati correnti della saved search
- `mode=new`: mostra solo i job non ancora visti (`saved_search_seen`) senza mutare stato seen

## API di supporto (nuova)
Endpoint:
- `GET /saved-searches/{search_id}/results`

Parametri:
- `mode=current|new`
- `limit`
- `offset`
- `scan_limit`

Response include:
- `saved_search`
- `mode`
- `current_count`
- `new_count`
- `results` (con `job_state`)
- `returned_count`, `limit`, `offset`

## Integrazione UI lista Saved Searches
Aggiornata lista `GET /admin/saved-searches` con action/link `Open` verso la nuova superficie:
- `/admin/saved-searches/{search_id}`

## Workflow consigliato
1. Apri `/admin/saved-searches` e clicca `Open` sulla search target.
2. In `mode=current`, triagia i risultati con stato/azioni rapide.
3. Passa a `mode=new` per focus sui match non ancora visti.
4. Usa `Save/Dismiss/Seen` per mantenere la search come inbox tematica.

## Test aggiunti/aggiornati
- API risultati saved search:
  - `tests/api/test_saved_searches_api_step27.py`
- UI dettaglio saved search + azioni stato + link Open:
  - `tests/api/test_admin_ui_step30.py`

## Limiti noti
- single-user only
- `mode=new` usa confronto URL visto/non visto (no dedup semantica)
- nessun ranking avanzato o semantic search in questa fase

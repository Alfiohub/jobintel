# Job State UX Expansion / Inbox v1 (Step 39)

## Obiettivo
Espandere il job state single-user oltre il solo alert detail, introducendo una inbox operabile nel flusso quotidiano.

## Superfici aggiornate

### API jobs list / count
Endpoint aggiornati:
- `GET /jobs`
- `GET /jobs/count`

Novità:
- ogni risultato include `job_state`
- filtri stato aggiunti:
  - `job_state` (`new|seen|saved|dismissed`)
  - `include_dismissed` (`true|false`, default `true` lato API)

### API query packs
Endpoint aggiornati:
- `GET /packs/{pack_name}`
- `GET /packs/{pack_name}/count`

Novità:
- ogni risultato pack include `job_state`
- supporto filtri stato (`job_state`, `include_dismissed`) anche sui pack

### Admin UI
- nuova pagina: `GET /admin/inbox`
- stato e azioni rapide mantenute su:
  - `GET /admin/alerts/{run_id}` (step38)
  - `GET /admin/inbox` (step39)

## Inbox (`/admin/inbox`)

### Cosa mostra
- conteggi per stato (`new`, `seen`, `saved`, `dismissed`)
- lista job filtrabile
- stato corrente per job
- azioni rapide per job:
  - `Seen`
  - `Save`
  - `Dismiss`
  - `Reset`

### Filtri principali inbox
- `state` (`new|saved|seen|dismissed|all`)
- `include_dismissed` (checkbox)
- `role_family`
- `normalized_title`
- `limit`, `offset`

## Workflow consigliato
1. Apri `/admin/inbox?state=new` per triage iniziale.
2. Marca rapidamente i job utili con `Save`.
3. Marca i non rilevanti con `Dismiss`.
4. Usa `state=saved` come shortlist operativa.
5. Usa `Reset` se vuoi riportare un job a `new`.

## Test aggiunti/aggiornati
- API stato + filtri lista/pack:
  - `tests/api/test_job_state_api_step38.py`
- Admin UI inbox render + azioni stato:
  - `tests/api/test_admin_ui_step30.py`

## Limiti noti
- single-user only (no auth/multi-user)
- filtri stato applicati in modo pragmatico lato API dopo enrich dello stato
- inbox v1 è operativa ma non include ancora ricerca full-text o ranking avanzato

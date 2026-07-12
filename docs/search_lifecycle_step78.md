# Saved Search Lifecycle / Archive v1 (Step 78)

## Obiettivo
Introdurre un lifecycle semplice per saved searches per separare working portfolio e storico, oltre al solo toggle enable/disable.

## Stati lifecycle
Stati supportati:
- `active`
- `disabled`
- `archived`

Significato operativo:
- `active`: search nel working set, partecipa a `run-all`, `run-due`, coverage/portfolio/hygiene
- `disabled`: search temporaneamente spenta ma ancora nel working set
- `archived`: search fuori dal working portfolio, mantenuta come storico/reference

## Compatibilità con `is_enabled`
`is_enabled` resta disponibile per compatibilità pragmatica ma viene allineato al lifecycle:
- `active` -> `is_enabled=true`
- `disabled` / `archived` -> `is_enabled=false`

## Storage / service aggiornati
File:
- `src/jobintel_next/product/saved_searches/service.py`

Aggiornamenti principali:
- schema `saved_searches` esteso con colonna `lifecycle` (+ migration)
- `create_saved_search(...)` supporta lifecycle coerente
- `update_saved_search(...)` supporta lifecycle
- `list_saved_searches(..., lifecycle=...)` con filtro (`all|active|disabled|archived`)
- nuove operazioni:
  - `archive_saved_search(...)`
  - `restore_saved_search(...)` (restore -> `disabled`)
- `is_saved_search_due(...)` ignora search non `active`

## Runner / scheduling
File:
- `src/jobintel_next/product/saved_searches/runner.py`

Aggiornamenti:
- `run_enabled_saved_searches(...)` considera solo search `active`
- `run_due_saved_searches(...)` già delega a `is_saved_search_due(...)`, quindi esclude `archived`

## API / UI aggiornate
API:
- `GET /saved-searches` supporta filtro `lifecycle`
- nuovi endpoint:
  - `POST /saved-searches/{search_id}/archive`
  - `POST /saved-searches/{search_id}/restore`

Admin UI:
- `/admin/saved-searches`:
  - badge lifecycle per riga
  - filtri lifecycle (`all`, `active`, `disabled`, `archived`)
  - azioni lifecycle:
    - `Enable`
    - `Disable`
    - `Archive`
    - `Restore`
- `/admin/saved-searches/{search_id}`:
  - lifecycle visibile
  - azioni lifecycle rapide

## Regole operative
1. Usa `disable` per pause temporanee.
2. Usa `archive` per search sperimentali/obsolete da togliere dal working portfolio.
3. Usa `restore` per riportare una search archived nel set operativo (stato `disabled`, poi `enable` se serve).

## Test aggiunti/aggiornati
Product:
- `tests/product/test_saved_searches_step24.py`
  - persistenza lifecycle
  - archive/restore flow
  - list filter per lifecycle
- `tests/product/test_scheduling_step47.py`
  - `run-due` ignora search archived

API/UI:
- `tests/api/test_admin_ui_step30.py`
  - render badge/filtri lifecycle
  - archive/restore dalla lista
- `tests/api/test_saved_searches_api_step27.py`
  - isolamento job_state test locale (job_state_db_path dedicato) + compatibilità lifecycle

## Limiti noti
- nessun versioning storico avanzato
- nessuna archive policy automatica
- nessun optimizer AI
- restore volutamente semplice (`archived` -> `disabled`)

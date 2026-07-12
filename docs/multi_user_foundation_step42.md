# Multi-user Foundation v1 (Step 42)

## Obiettivo
Introdurre un boundary utente minimale e pragmatico, separando i dati principali del workflow (saved searches + job state) senza implementare ancora auth enterprise.

## Cosa è stato reso per-user

### 1) Saved Searches
Storage aggiornato in `saved_searches.db`:
- tabella `users` minimale:
  - `user_id`
  - `email`
  - `created_at`
  - `is_active`
- `saved_searches` ora include `user_id`
- `saved_search_seen` ora include `user_id`

Service aggiornati con `user_id`:
- `create_saved_search`
- `list_saved_searches`
- `get_saved_search`
- `update_saved_search`
- `delete_saved_search`
- `run_saved_search`
- `check_new_matches`
- `get_saved_search_results`

### 2) Job State
Storage aggiornato in `job_state.db`:
- tabella `users` minimale
- tabella `job_state` migrata a chiave composta:
  - `PRIMARY KEY(user_id, job_url)`

Service aggiornati con `user_id`:
- `set_job_state`
- `get_job_state`
- `get_many_job_states`
- `clear_job_state`

## Current user foundation (simple/fake auth)
Introduzione di `CurrentUser` minimale lato API:
- default da env:
  - `JOBINTEL_DEFAULT_USER_ID`
  - `JOBINTEL_DEFAULT_USER_EMAIL`
- override per request via header:
  - `X-JobIntel-User-Id`
  - `X-JobIntel-User-Email`

Comportamento:
- senza header usa utente default (single-user fallback)
- con header isola dati per utente

## API/UI aggiornate
- API jobs state e saved searches ora usano sempre `current_user`
- anche run/check-new/results e run-all alerts sono scoperte per utente
- Admin UI usa lo stesso `current_user` (default o header) per leggere/scrivere dati utente

## Cosa resta ancora globale
- history artifact degli alert run su filesystem (`data/alerts/runs`) resta globale
- nessun login/logout reale
- nessuna gestione sessione persistente browser
- nessuna policy ruoli/permessi

## Test aggiunti/aggiornati

Isolamento saved searches tra utenti:
- `tests/api/test_saved_searches_api_step27.py`
- `tests/product/test_saved_searches_step24.py`

Isolamento job state tra utenti:
- `tests/api/test_job_state_api_step38.py`
- `tests/product/test_job_state_step38.py`

Current user minimale:
- test con header `X-JobIntel-User-Id` per verificare separazione dati

## Limiti noti
- niente OAuth/password flow
- niente auth UI reale (solo default user + header override)
- niente ruoli, billing, invite system
- non è ancora una multi-tenant architecture enterprise

## Prossimi passi naturali verso auth vera
1. login minimale con session cookie locale
2. binding esplicito user-session su Admin UI
3. separazione per-user degli artifact alert run o metadata indice per user
4. hardening security (CSRF/session lifetime) prima di esposizione pubblica

# Job State Management (Step 38)

## Obiettivo
Introdurre un workflow single-user reale sui job trovati, con stato utente persistente e azioni operative via API + Admin UI.

## Stati supportati
- `new` (default implicito)
- `seen`
- `saved`
- `dismissed`

## Modello dati / Storage
Modulo: `src/jobintel_next/product/job_state/service.py`

Storage SQLite dedicato (default): `data/jobs/job_state.db`

Tabella:
- `job_state`
  - `job_url` (PK)
  - `state` (`new|seen|saved|dismissed`)
  - `updated_at`

Note:
- Non viene creata una riga per lo stato `new` di default.
- Se un job non ha record, lo stato restituito è `new`.

## Operazioni implementate
Service layer:
- `set_job_state(...)`
- `get_job_state(...)`
- `get_many_job_states(...)`
- `clear_job_state(...)`

API HTTP:
- `GET /jobs/state?job_url=...`
- `POST /jobs/state`
  - body: `{ "job_url": "...", "state": "seen|saved|dismissed|new" }`
- `POST /jobs/state/clear?job_url=...`

Error handling:
- `422` su input invalidi (`job_url` mancante, stato non valido)

## Integrazione Admin UI
- Nella pagina `GET /admin/alerts/{run_id}` i `sample_new_matches` ora mostrano:
  - stato corrente (`new/seen/saved/dismissed`)
  - azioni rapide: `Seen`, `Save`, `Dismiss`, `Reset`
- Azioni UI:
  - `POST /admin/jobs/state`
  - `POST /admin/jobs/state/clear`

## Come entra nel workflow prodotto
1. L’utente lancia `run-all` alert.
2. Apre il dettaglio run (`/admin/alerts/{run_id}`).
3. Marca i job nuovi come `seen/saved/dismissed` direttamente dalla tabella campione.
4. Lo stato resta persistente su SQLite e rientra nel loop operativo quotidiano.

## Test aggiunti
- Storage stato: `tests/product/test_job_state_step38.py`
- API stato: `tests/api/test_job_state_api_step38.py`
- UI minima (azioni stato da alert detail): estensione in `tests/api/test_admin_ui_step30.py`

## Limiti noti
- Single-user only (niente auth/multi-user).
- Stato agganciato a `job_url` (nessuna dedup entity-level).
- In questa fase lo stato è integrato soprattutto nel workflow alert detail (non ancora su tutte le liste jobs).

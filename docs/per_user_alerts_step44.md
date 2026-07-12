# Per-user Alert Ownership v1 (Step 44)

## Obiettivo
Rendere per-user la ownership degli alert run, allineandola ad auth/session e al boundary già introdotto su saved searches/job state.

## Cosa è diventato per-user

### Alert run artifacts
Gli artifact non sono più condivisi globalmente per default.

Nuova struttura filesystem:
- `data/alerts/runs/<user_id>/<run_id>.json`
- `data/alerts/runs/<user_id>/<run_id>.md`

`<user_id>` viene normalizzato in modo sicuro per path filesystem.

### API alert (scope utente)
I seguenti endpoint ora lavorano sul `current_user`:
- `POST /alerts/run-all`
- `GET /alerts/runs`
- `GET /alerts/runs/{run_id}`
- `GET /alerts/summary`

Effetto:
- ogni utente vede solo la propria history
- dettaglio run di altro utente risulta `404`
- summary è calcolata solo sui run dell’utente corrente

### Admin UI alerts
Le superfici admin ora mostrano run per-user:
- `/admin` (summary + recent runs)
- `/admin/alerts` (history)
- `/admin/alerts/{run_id}` (detail)

## Moduli aggiornati
- `src/jobintel_next/product/alerts/history.py`
  - supporto `user_id` su list/detail/summary
  - helper `per_user_runs_dir(...)`
- `src/jobintel_next/product/saved_searches/runner.py`
  - scrittura artifact nel path per-user
- `src/jobintel_next/app/api/router.py`
  - endpoint alert scoped al `current_user`
- `src/jobintel_next/app/admin_ui/router.py`
  - admin alerts scoped al `current_user`

## Workflow aggiornato
1. utente loggato (sessione) o header override API
2. `run-all` scrive artifact nella cartella utente
3. list/detail/summary leggono solo da quella cartella
4. niente leakage tra utenti sulla history alert

## Compatibilità pragmatica
- fallback locale/dev resta disponibile via `X-JobIntel-User-Id` / default user
- single-user locale continua a funzionare (path tipico: `.../runs/local-user/...`)

## Test aggiunti
Nuovo test:
- `tests/api/test_per_user_alerts_step44.py`

Coperture:
- isolamento history tra utenti
- run detail non accessibile cross-user (`404`)
- summary per-user
- `run-all` scrive nel path utente corretto

Regression alert/UI ancora verdi:
- `tests/api/test_alert_runs_api_step28.py`
- `tests/api/test_alert_ops_polish_step29.py`
- `tests/api/test_admin_ui_step30.py`
- `tests/api/test_smoke_e2e_step37.py`

## Limiti noti
- ACL/ruoli avanzati non presenti
- shared workspace non supportato
- cleanup artifact resta semplice e non fa policy multi-user avanzate
- nessuna preferences/delivery routing complessa

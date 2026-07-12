# Alert / Digest UX Observability v1 (Step 49)

## Obiettivo
Rendere trasparente il workflow alert quotidiano (saved searches, scheduling due, run history, digest delivery) dal punto di vista utente.

## Superfici migliorate

### `/admin` (overview)
- KPI più utili:
  - saved searches totali
  - saved searches abilitate
  - saved searches `due now`
  - latest run id
  - latest run total new matches
- Latest digest outcome (se disponibile):
  - sent/skipped/error
  - attempted/sent/skipped/error counts
  - destination email

### `/admin/saved-searches` (lista)
Per ogni saved search ora sono visibili:
- `frequency`
- `due / not due`
- `enabled`
- `last_run_at`
- `last new matches count` (ultimo run trovato per quella search)

### `/admin/saved-searches/{search_id}` (detail workspace)
Indicatori principali resi espliciti:
- `frequency`
- `due / not due`
- `last_run_at`
- `current_count`
- `new_count`
- ultimo outcome run (quando presente in history): run id, status, new/current count, timestamp

### `/admin/alerts` (history)
Run history arricchita con digest visibility:
- digest status: `sent` / `skipped` / `error`
- destination email
- digest counts: attempted/sent/skipped/errors

### `/admin/alerts/{run_id}` (run detail)
Dettaglio run più osservabile:
- blocco `Digest delivery` con status + counts + destination
- breakdown per search con colonna `frequency` oltre a status/new/current

## Moduli aggiornati
- `src/jobintel_next/app/admin_ui/router.py`
  - calcolo `due` con `is_saved_search_due(...)`
  - latest outcomes per saved search da run history
  - KPI overview estesi
- `src/jobintel_next/product/alerts/history.py`
  - `list_alert_runs(...)` include `digest_delivery` e `email_delivery`
- Templates:
  - `index.html`
  - `saved_searches.html`
  - `saved_search_detail.html`
  - `alerts.html`
  - `alert_detail.html`
  - `base.html` (badge CSS)

## Workflow utente consigliato
1. Apri `/admin` per vedere quante search sono `due now` e l’ultimo esito digest.
2. Vai in `/admin/saved-searches` per identificare search da monitorare (due/not due + last new).
3. Apri `/admin/saved-searches/{id}` per lavorare sul dettaglio e sui risultati.
4. Controlla `/admin/alerts` e `/admin/alerts/{run_id}` per audit delivery digest e qualità run.

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - frequency + due status in saved searches list
  - due status / last run in saved search detail
  - digest metadata render in alert detail
  - overview KPI labels

## Limiti noti
- nessun scheduler distribuito (foundation cron-friendly)
- nessun notification center in-app
- nessuna analytics avanzata su delivery trend
- niente ranking/semantic features in questo step

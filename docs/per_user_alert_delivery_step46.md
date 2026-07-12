# Per-user Alert Delivery Polish v1 (Step 46)

## Obiettivo
Rendere la delivery email alert più coerente con il prodotto multi-user, sfruttando le preferences utente e migliorando rendering + feedback delivery.

## Cosa è stato migliorato

### 1) Fallback naturale su `default_alert_email`
Su `POST /alerts/run-all`:
- se `send_email=true` e `email_to` non è passato,
- il backend prova automaticamente `default_alert_email` dell’utente corrente,
- se manca anche quello, ritorna `422` con errore chiaro.

Questo riduce il setup manuale ad ogni run.

### 2) Rendering email migliorato
In `src/jobintel_next/product/alerts/email.py`:
- subject più pulito:
  - `[JobIntel] <N> new match(es) · <saved_search_name>`
- body text più leggibile
- body HTML leggero aggiunto (multipart text + html)

Contenuti inclusi:
- saved search name
- new matches count
- run timestamp
- sample match (title + URL)

### 3) Delivery metadata più chiari
`send_email_alerts_from_run(...)` ora restituisce anche:
- `attempted_count`
- `sent_count`
- `skipped_count`
- `skipped_zero_count`
- `skipped_status_count`
- `error_count`
- `email_attempted`
- `email_sent`
- `email_skipped`
- `email_error`

### 4) Persistenza delivery nel run artifact
Dopo run con email attiva, il metadata delivery viene salvato nel JSON artifact del run (`email_delivery`).

Effetto:
- `GET /alerts/runs/{run_id}` può mostrare info delivery anche dopo il run.

### 5) UI alerts più chiara
`/admin/alerts`:
- campo email precompilato da `default_alert_email`
- hint esplicito sul fallback default

`/admin/alerts/{run_id}`:
- se presente, mostra riepilogo delivery email (attempted/sent/skipped/errors + destinatario)

## Moduli aggiornati
- `src/jobintel_next/product/alerts/email.py`
- `src/jobintel_next/product/alerts/__init__.py`
- `src/jobintel_next/app/api/router.py`
- `src/jobintel_next/app/api/schemas.py`
- `src/jobintel_next/app/admin_ui/router.py`
- `src/jobintel_next/app/admin_ui/templates/alerts.html`
- `src/jobintel_next/app/admin_ui/templates/alert_detail.html`

## Test aggiunti/aggiornati
- `tests/api/test_alert_ops_polish_step29.py`
  - fallback su `default_alert_email`
  - metadata delivery nel run response + run detail
- `tests/product/test_email_alerts_step26.py`
  - rendering subject/body text/html
  - skip su zero new
  - metadata delivery coerenti

## Limiti noti
- niente scheduler distribuito
- niente canali Telegram/push
- niente preferences avanzate (digest/time windows)
- delivery SMTP resta semplice/sincrona

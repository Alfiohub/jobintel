# Delivery History / Retry-Minimum v1 (Step 51)

## Obiettivo
Rendere la delivery email più governabile operativamente:
- history metadata più chiara nei run artifact
- resend/retry manuale minimale del digest

## Metadata delivery migliorati
Sia `email_delivery` sia `digest_delivery` ora includono campi coerenti:
- `attempted_at`
- `delivery_timestamp`
- `to_email`
- `email_attempted`
- `email_sent`
- `email_skipped`
- `email_error`
- `attempted_count`
- `sent_count`
- `skipped_count`
- `error_count`

Campi specifici restano disponibili:
- `skip_reason` (quando skip)
- `errors` (lista errori)
- digest: `total_new_matches`, `searches_with_new_matches`

## Resend digest manuale (CLI)
Nuovo comando:

```bash
uv run jobintel-next alerts resend-digest \
  --run-json data/alerts/runs/<user_id>/<run_id>.json \
  --to alerts@example.com
```

`--to` è opzionale:
- se assente, usa `digest_delivery.to_email` già salvato nel run artifact
- se manca anche quello: errore chiaro e exit code `1`

SMTP config:
- usa env (`JOBINTEL_SMTP_HOST`, `JOBINTEL_SMTP_FROM`, ecc.) via `SMTPConfig.from_env()`

Comportamento resend:
1. legge il run artifact
2. ricostruisce digest dal contenuto run
3. invia a `--to` o fallback metadata
4. persiste nuovo `digest_delivery` nel run JSON (`resend=true`, `resend_of_run_id=...`)
5. se `total_new_matches=0`: skip coerente (`skip_reason=no_new_matches`)

## UI/Operatività minima
In `/admin/alerts/{run_id}`:
- metadata delivery mostrano anche `attempted_at` e `delivery_timestamp`
- hint comando CLI per resend manuale digest con `--run-json` già precompilato

## Moduli aggiornati
- `src/jobintel_next/product/alerts/email.py`
- `src/jobintel_next/product/alerts/digest.py`
- `src/jobintel_next/product/alerts/__init__.py`
- `src/jobintel_next/cli.py`
- `src/jobintel_next/app/admin_ui/templates/alert_detail.html`

## Test aggiunti/aggiornati
Nuovi:
- `tests/product/test_delivery_history_step51.py`
  - resend da run artifact valido
  - skip se no new matches
  - errore chiaro se manca destinatario

Aggiornati:
- `tests/product/test_digest_email_step48.py`
- `tests/product/test_email_alerts_step26.py`

## Workflow operativo consigliato
1. Esegui `alerts run-due` (con o senza digest automatico).
2. Controlla `/admin/alerts/{run_id}`:
   - status digest
   - attempted/sent/skipped/errors
   - destination + timestamp
3. Se necessario, rilancia manualmente:
   - `alerts resend-digest --run-json ... [--to ...]`

## Limiti noti
- nessun retry automatico/backoff
- nessuna queue distribuita
- nessun scheduler distribuito
- nessun canale Telegram/push

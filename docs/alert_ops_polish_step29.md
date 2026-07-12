# Alert Ops Polish Step 29

## Obiettivo
Rendere il workflow alert più operativo e governabile:
- run-all con invio email opzionale
- summary rapido dello stato alert
- cleanup semplice degli artifact storici

## 1) `POST /alerts/run-all` con email opzionale
Nuovi query params:
- `send_email` (`true|false`, default `false`)
- `email_to` (richiesto se `send_email=true`)

Comportamento:
- esegue run batch come Step 28
- se `send_email=true`, legge il JSON artifact appena creato e invia email solo per search con `new_matches_count > 0`
- SMTP letto da env (`JOBINTEL_SMTP_*`) via `SMTPConfig.from_env()`

Error handling:
- `422` se `send_email=true` ma manca `email_to`
- `422` se SMTP non configurato correttamente

Response:
- campo aggiuntivo `email_delivery` (`null` quando `send_email=false`)

## 2) `GET /alerts/summary`
Endpoint nuovo per overview operativa.

Campi principali:
- `runs_count`
- `latest_run_id`
- `latest_run_total_new_matches`
- `recent_error_runs_count`
- `recent_ok_runs_count`
- `recent_searches_with_new_matches` (sample breve)

Query params:
- `recent_limit` (default `20`)
- `sample_new_searches` (default `5`)

## 3) Cleanup artifact
Aggiunta retention pragmatica su file artifact.

CLI:

```bash
uv run jobintel-next alerts cleanup --outdir data/alerts/runs --keep-last 20
```

Effetto:
- mantiene gli ultimi `N` run (`*.json` + `*.md`)
- rimuove i più vecchi

## Esempi

Run-all senza email:

```bash
curl -X POST "http://127.0.0.1:8000/alerts/run-all?send_email=false"
```

Run-all con email:

```bash
curl -X POST "http://127.0.0.1:8000/alerts/run-all?send_email=true&email_to=alerts@example.com"
```

Summary:

```bash
curl "http://127.0.0.1:8000/alerts/summary"
```

## Limiti noti
- nessun scheduler distribuito
- nessuna auth/multi-user
- nessuna retry queue sofisticata
- email delivery resta SMTP semplice e sincrono

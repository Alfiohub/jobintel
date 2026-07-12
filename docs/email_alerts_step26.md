# Email Alerts Step 26

## Obiettivo
Aggiungere un primo canale reale di delivery per gli alert delle saved searches, partendo da email SMTP semplice.

## Moduli
- `src/jobintel_next/product/alerts/email.py`
  - rendering subject/body
  - invio SMTP
  - invio batch da artifact JSON del runner
- integrazione CLI in `src/jobintel_next/cli.py`
  - comando: `jobintel-next alerts send-email`

## Configurazione SMTP
Supportata via parametri CLI:
- `--smtp-host`
- `--smtp-port` (default `587`)
- `--smtp-user` (opzionale)
- `--smtp-password` (opzionale)
- `--from-email`
- `--no-tls` (opzionale, di default usa STARTTLS)

Supportata anche via env con `SMTPConfig.from_env()`:
- `JOBINTEL_SMTP_HOST`
- `JOBINTEL_SMTP_PORT`
- `JOBINTEL_SMTP_USER`
- `JOBINTEL_SMTP_PASSWORD`
- `JOBINTEL_SMTP_FROM`
- `JOBINTEL_SMTP_USE_TLS`

## Comando operativo
Esegue invio email leggendo un artifact JSON prodotto da `saved-search run-all`.

```bash
uv run jobintel-next alerts send-email \
  --run-json data/alerts/runs/20260330T120000Z.json \
  --to alerts@example.com \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --smtp-user smtp_user \
  --smtp-password smtp_password \
  --from-email noreply@example.com
```

Output JSON del comando:
- `sent_count`
- `skipped_zero_count`
- `error_count`
- `errors`

## Policy di invio
- invia email solo per search con `status=ok` e `new_matches_count > 0`
- se `new_matches_count = 0`, la search viene saltata
- subject formato:
  - `[JobIntel] <N> new matches for saved search: <search_name>`

## Esempio email
Subject:

```text
[JobIntel] 4 new matches for saved search: high confidence tech
```

Body (testuale):

```text
JobIntel Saved Search Alert

Saved search: high confidence tech
New matches: 4
Run timestamp: 2026-03-30T10:00:00+00:00

Sample new matches:
- Software Engineer
  https://example.com/jobs/1
- Data Engineer
  https://example.com/jobs/2
```

## Test coperti
- rendering subject/body
- skip su `new_matches_count = 0`
- sender mockato con errore SMTP
- integrazione minima comando CLI `alerts send-email`

## Limiti noti
- nessun retry/backoff sofisticato
- nessuna queue di delivery
- nessuna preferenza multi-user
- nessuna integrazione Telegram/push in questo step

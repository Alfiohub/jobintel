# Per-user Digest Email v1 (Step 48)

## Obiettivo
Ridurre rumore nella delivery alert introducendo un digest email per-user sui run dovuti.

## Cosa è stato introdotto
- Nuovo modulo: `src/jobintel_next/product/alerts/digest.py`
- Rendering digest email:
  - `build_digest_subject(...)`
  - `build_digest_body_text(...)`
  - `build_digest_body_html(...)`
- Invio digest da artifact run:
  - `send_digest_email_from_run(...)`
- Persistenza metadata digest nel run artifact:
  - `persist_digest_delivery_to_run(...)`

## Struttura digest
Per ogni saved search con `new_matches_count > 0`:
- nome search
- count nuovi match
- sample match (`title_raw + url`)

Summary globale:
- `searches_total`
- `searches_processed`
- `searches_with_new_matches`
- `total_new_matches`
- `run_timestamp`

Subject esempio:
- `[JobIntel] Daily digest · 7 new matches across 3 searches`

## Integrazione con run-due
Comando aggiornato:

```bash
uv run jobintel-next alerts run-due \
  --saved-db data/jobs/saved_searches.db \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db \
  --outdir data/alerts/runs \
  --user-id local-user \
  --user-email local@example.com \
  --send-digest-email
```

Opzioni nuove:
- `--send-digest-email`
- `--email-to` (opzionale)

Fallback destinatario:
1. `--email-to` se passato
2. `default_alert_email` da account settings utente
3. se manca anche quello: skip chiaro (`missing_default_alert_email`)

SMTP:
- usa `SMTPConfig.from_env()` (`JOBINTEL_SMTP_*`)
- se non configurato: skip/error metadata coerente nel run

## Metadata nel run output
Quando il digest è attivato, il run JSON include:
- `digest_delivery`
  - `attempted_count`
  - `sent_count`
  - `skipped_count`
  - `error_count`
  - `email_attempted`
  - `email_sent`
  - `email_skipped`
  - `email_error`
  - `skip_reason` (se applicabile)

## Compatibilità
- La delivery per-search esistente (`send_email_alerts_from_run`) resta invariata.
- Il digest è un path aggiuntivo orientato a `run-due`.

## Test aggiunti
- `tests/product/test_digest_email_step48.py`
  - render subject/body digest
  - skip se `no_new_matches`
  - fallback su `default_alert_email`
  - metadata `digest_delivery` persistiti nel run artifact

## Limiti noti
- nessun scheduler distribuito
- nessuna finestra oraria avanzata per digest
- nessun canale Telegram/push
- nessun notification center in-app

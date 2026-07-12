# Operational Runbook / Developer UX Step 32

## Obiettivo
Guida operativa unica per avviare e dimostrare il backend MVP end-to-end con attrito minimo.

Questa guida copre:
- ingestione
- build index SQLite
- API + Admin UI
- saved searches
- alert runs
- email alerts

## Prerequisiti
- Python `>=3.11`
- `uv` installato
- repository `joballert2`

Setup rapido:

```bash
cd joballert2
make setup
```

## Variabili env principali
- `JOBINTEL_INDEXED_INPUT` (default: `data/jobs/jobs_indexed_en.jsonl`)
- `JOBINTEL_SQLITE_PATH` (default usato nei target: `data/jobs/jobs_indexed_en.db`)
- `JOBINTEL_SAVED_DB_PATH` (default: `data/jobs/saved_searches.db`)
- `JOBINTEL_ALERT_RUNS_DIR` (default: `data/alerts/runs`)

SMTP (per email alerts):
- `JOBINTEL_SMTP_HOST`
- `JOBINTEL_SMTP_PORT` (default `587`)
- `JOBINTEL_SMTP_USER`
- `JOBINTEL_SMTP_PASSWORD`
- `JOBINTEL_SMTP_FROM`
- `JOBINTEL_SMTP_USE_TLS` (`true|false`)

## Comandi principali (Makefile)
Lista target:

```bash
make help
```

Target operativi chiave:
- `make ingest-export BOARD=found INGEST_OUT=data/jobs/found_raw.jsonl`
- `make ingest-run CONFIG=config/default.yml INGEST_OUT=data/jobs/jobs_raw.jsonl`
- `make build-index INDEXED_JSON=data/jobs/jobs_indexed_en.jsonl INDEXED_DB=data/jobs/jobs_indexed_en.db`
- `make run-api`
- `make run-alerts`
- `make cleanup-alerts KEEP_LAST=20`

## Ingestione dati
Board singola:

```bash
make ingest-export BOARD=found INGEST_OUT=data/jobs/found_raw.jsonl
```

Run strutturato YAML:

```bash
make ingest-run CONFIG=config/default.yml INGEST_OUT=data/jobs/jobs_raw.jsonl
```

Nota: pipeline intermedia (language/cleaning/extraction/titles/indexed) resta disponibile via `jobintel-next ...`.

## Build SQLite index
Da indexed JSONL:

```bash
make build-index INDEXED_JSON=data/jobs/jobs_indexed_en.jsonl INDEXED_DB=data/jobs/jobs_indexed_en.db
```

## Avvio API + Admin UI

```bash
make run-api
```

Se la porta `8000` è occupata:

```bash
make run-api APP_PORT=8010
```

URL utili:
- API docs: `http://127.0.0.1:8000/docs`
- Admin UI: `http://127.0.0.1:8000/admin`

## Saved Search (API/UI/CLI)
Da Admin UI:
- `/admin/saved-searches/new` per creare
- `/admin/saved-searches` per edit/enable/disable/run/delete

Da API:
- `POST /saved-searches`
- `GET /saved-searches`
- `POST /saved-searches/{id}/update`
- `POST /saved-searches/{id}/delete`

Da CLI:

```bash
uv run jobintel-next saved-search list
```

## Alert runs
Batch run di tutte le saved searches abilitate:

```bash
make run-alerts
```

History via API:
- `GET /alerts/runs`
- `GET /alerts/runs/{run_id}`
- `GET /alerts/summary`

Artifact locali:
- `data/alerts/runs/<run_id>.json`
- `data/alerts/runs/<run_id>.md`

## Email alerts
Invio email da artifact run:

```bash
make send-alert-email RUN_JSON=data/alerts/runs/<run_id>.json EMAIL_TO=alerts@example.com
```

Oppure API con invio opzionale:
- `POST /alerts/run-all?send_email=true&email_to=alerts@example.com`

## Demo flow MVP (rapido)
1. Build index

```bash
make build-index
```

2. Avvia API/UI

```bash
make run-api
```

Su porta alternativa:

```bash
make run-api APP_PORT=8010
```

3. Crea saved search in UI (`/admin/saved-searches/new`)
4. Esegui run-all in UI (`/admin/alerts`)
5. Apri dettaglio run e verifica `new_matches_count`
6. (Opzionale) invia email dal run artifact

## Troubleshooting minimo
- `422 email_to is required`: su `/alerts/run-all`, impostare `email_to` se `send_email=true`.
- `missing SMTP env config`: impostare `JOBINTEL_SMTP_HOST` e `JOBINTEL_SMTP_FROM`.
- API non parte per dataset mancante: verificare `JOBINTEL_INDEXED_INPUT` o percorso file.
- SQLite non trovato: verificare `JOBINTEL_SQLITE_PATH` e build index.
- Form Admin UI non funziona: verificare installazione dipendenze (`python-multipart`, `jinja2`) con `make setup`.

## Stato: production-like vs MVP-only
### Già production-like (base)
- pipeline deterministica e testata
- storage SQLite e API HTTP con validazione
- saved searches CRUD + alert run history
- admin UI operativa server-rendered

### Ancora MVP/local-only
- no auth/multi-user
- no scheduler distribuito
- no retry queue sofisticata
- no semantic search/ranking avanzato
- no hardening enterprise osservabilità/deployment

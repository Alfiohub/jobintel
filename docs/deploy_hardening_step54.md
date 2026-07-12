# Deploy Hardening v1 (Step 54)

## Obiettivo
Rendere il deploy Docker/compose più robusto per uso VPS/container minimo reale, senza introdurre orchestration enterprise.

## Cosa è stato hardenizzato

### 1) Startup container più robusto
Nuovo entrypoint:
- `scripts/container_start.sh`

Comportamento:
- valida path dataset (`JOBINTEL_INDEXED_INPUT`) prima di avviare
- valida path SQLite (`JOBINTEL_SQLITE_PATH`) se configurato
- crea directory necessarie per:
  - saved DB (`JOBINTEL_SAVED_DB_PATH`)
  - job state DB (`JOBINTEL_JOB_STATE_DB_PATH`)
  - alert runs (`JOBINTEL_ALERT_RUNS_DIR`)
- avvia `uvicorn` con `APP_HOST`/`APP_PORT`

Se i path critici sono errati, startup fallisce subito con errore chiaro (`[startup-error] ...`).

### 2) Dockerfile migliorato
- include script di startup dedicato
- aggiunge variabili env esplicite anche per:
  - `JOBINTEL_JOB_STATE_DB_PATH`
  - session cookie config
- aggiunge `HEALTHCHECK` su `/health`

### 3) docker-compose più production-like
`docker-compose.yml` aggiornato con:
- env session/auth esplicite
- `JOBINTEL_REQUIRE_SESSION_SECRET` (default compose: `true`)
- `healthcheck` applicativo
- mapping porta coerente con `APP_PORT`

### 4) Session secret hardening (runtime)
In `dependencies.py`:
- nuovo flag env: `JOBINTEL_REQUIRE_SESSION_SECRET`
- se `true` e `JOBINTEL_SESSION_SECRET` resta default dev, l'app fallisce in startup con errore esplicito

Questo evita deploy con secret di sessione debole per sbaglio.

## Env principali (deploy)
Richieste/consigliate:
- `APP_HOST`, `APP_PORT`
- `JOBINTEL_INDEXED_INPUT`
- `JOBINTEL_SQLITE_PATH`
- `JOBINTEL_SAVED_DB_PATH`
- `JOBINTEL_JOB_STATE_DB_PATH`
- `JOBINTEL_ALERT_RUNS_DIR`
- `JOBINTEL_SESSION_SECRET`
- `JOBINTEL_REQUIRE_SESSION_SECRET`
- `JOBINTEL_SESSION_MAX_AGE`
- `JOBINTEL_SESSION_COOKIE_NAME`
- `JOBINTEL_SESSION_HTTPS_ONLY`
- `JOBINTEL_SESSION_SAME_SITE`

SMTP opzionali:
- `JOBINTEL_SMTP_HOST`, `JOBINTEL_SMTP_PORT`, `JOBINTEL_SMTP_USER`, `JOBINTEL_SMTP_PASSWORD`, `JOBINTEL_SMTP_FROM`, `JOBINTEL_SMTP_USE_TLS`

## File env
- `.env.example` (dev/demo locale)
- `.env.production.example` (profilo prod-like minimo)

Nota: in prod-like usare sempre `JOBINTEL_REQUIRE_SESSION_SECRET=true` e un secret reale.

## Volumi/path persistenti consigliati
Mount host->container:
- `./data:/app/data`

Persisti così:
- dataset/index (`data/demo` o `data/jobs`)
- saved searches DB
- job state DB
- alert run artifacts

## Comandi pratici
Build:
```bash
make docker-build
```

Run singolo con env locale:
```bash
make docker-run ENV_FILE=.env APP_PORT=8000
```

Run singolo prod-like:
```bash
make run-prod-like PROD_ENV_FILE=.env.production.example APP_PORT=8000
```

Compose prod-like (detached):
```bash
make deploy-local PROD_ENV_FILE=.env.production.example
```

Stop compose:
```bash
make docker-compose-down ENV_FILE=.env
```

## Dev vs prod-like
Dev (`.env.example`):
- secret permissivo default
- `JOBINTEL_REQUIRE_SESSION_SECRET=false`
- rapido per demo locale

Prod-like (`.env.production.example`):
- secret obbligatorio
- `JOBINTEL_REQUIRE_SESSION_SECRET=true`
- `JOBINTEL_SESSION_HTTPS_ONLY=true`
- path persistenti esplicitati

## Smoke/check minimi aggiunti
Test nuovo:
- `tests/api/test_deploy_hardening_step54.py`

Copertura:
- validazione secret richiesta (`JOBINTEL_REQUIRE_SESSION_SECRET=true`)
- startup config app con env/path prod-like ragionevoli

## Limiti noti
- nessun reverse proxy/TLS termination integrato
- nessun scheduler distribuito/queue
- nessun CI/CD pipeline completa
- nessun managed DB esterno in questo step

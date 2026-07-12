# Deploy minimale v1 (Step 35)

## Obiettivo
Rendere il backend MVP avviabile in modo riproducibile fuori dalla macchina locale usando Docker come path principale demo/deploy.

## Asset introdotti
- `Dockerfile` (API + Admin UI nella stessa app)
- `docker-compose.yml` minimale
- `.env.example` con env principali
- target Makefile:
  - `make docker-build`
  - `make docker-run`
  - `make docker-compose-up`
  - `make docker-compose-down`

## Build immagine
```bash
make docker-build
```

Oppure:
```bash
docker build -t jobintel-next:demo .
```

## Run container (singolo)
```bash
make docker-run
```

Apre API/UI su `http://127.0.0.1:8000`.

Il comando monta `./data` in `/app/data` per persistenza.

## Run con docker compose
1. Copia env di esempio:
```bash
cp .env.example .env
```
2. Avvia:
```bash
make docker-compose-up
```
3. Stop:
```bash
make docker-compose-down
```

## Env vars principali
- `APP_HOST` (default `0.0.0.0`)
- `APP_PORT` (default `8000`)
- `JOBINTEL_INDEXED_INPUT`
- `JOBINTEL_SQLITE_PATH`
- `JOBINTEL_SAVED_DB_PATH`
- `JOBINTEL_ALERT_RUNS_DIR`

SMTP opzionali:
- `JOBINTEL_SMTP_HOST`
- `JOBINTEL_SMTP_PORT`
- `JOBINTEL_SMTP_USER`
- `JOBINTEL_SMTP_PASSWORD`
- `JOBINTEL_SMTP_FROM`
- `JOBINTEL_SMTP_USE_TLS`

## Path persistenti / volumi
Con compose:
- host: `./data`
- container: `/app/data`

Questo preserva:
- DB SQLite
- saved searches DB
- artifact alert runs

## Flow deploy demo
1. `make docker-build`
2. `make docker-run` (oppure `make docker-compose-up`)
3. Apri:
   - `http://127.0.0.1:8000/admin`
   - `http://127.0.0.1:8000/docs`

## Limiti noti
- nessun reverse proxy avanzato
- nessun orchestration layer (Kubernetes)
- nessun CI/CD in questo step
- nessuna auth/multi-user

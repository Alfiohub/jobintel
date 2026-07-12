# Alert Runs API Step 28

## Obiettivo
Esporre via HTTP API il loop operativo alert:
- esecuzione batch delle saved searches abilitate
- lista history run
- dettaglio run specifico

## Endpoint
- `POST /alerts/run-all`
- `GET /alerts/runs`
- `GET /alerts/runs/{run_id}`

## Behavior
### `POST /alerts/run-all`
- esegue `run_enabled_saved_searches(...)`
- genera artifact locali in `data/alerts/runs/<run_id>.json|.md` (o directory configurata)
- ritorna summary completo del run

Query params supportati:
- `scan_limit` (default `5000`)
- `limit` (default `200`)
- `sample_size` (default `5`)

### `GET /alerts/runs`
- legge gli artifact `*.json` nella directory runs
- ritorna lista run in ordine più recente prima (per `run_id` filename)

### `GET /alerts/runs/{run_id}`
- ritorna il JSON completo del run richiesto
- `404` se `run_id` non esiste

## Esempi

Run batch:

```bash
curl -X POST "http://127.0.0.1:8000/alerts/run-all?scan_limit=5000&limit=200&sample_size=5"
```

List history:

```bash
curl "http://127.0.0.1:8000/alerts/runs"
```

Run detail:

```bash
curl "http://127.0.0.1:8000/alerts/runs/20260330T120000Z"
```

## Config
- dataset indexed: `JOBINTEL_INDEXED_INPUT` (già esistente)
- saved searches DB: `JOBINTEL_SAVED_DB_PATH`
- alert runs dir: `JOBINTEL_ALERT_RUNS_DIR` (default `data/alerts/runs`)

## Limiti noti
- history basata su artifact file locali (no DB history dedicato)
- nessun scheduler distribuito
- nessuna auth/multi-user
- email non orchestrata direttamente da questi endpoint in step28

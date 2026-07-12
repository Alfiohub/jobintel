# Saved Searches API Step 27

## Obiettivo
Esporre saved searches e workflow alert via HTTP API, riusando la foundation già esistente (service + runner).

## Endpoint
- `GET /saved-searches`
- `POST /saved-searches`
- `POST /saved-searches/{search_id}/enable`
- `POST /saved-searches/{search_id}/disable`
- `POST /saved-searches/{search_id}/run`
- `POST /saved-searches/{search_id}/check-new`

## Payload `POST /saved-searches`
Request body:
- `name` (string, required)
- `query_type` (`filters` | `pack`, required)
- `filters_json` (string JSON object, opzionale; richiesto se `query_type=filters`)
- `pack_name` (string, opzionale; richiesto se `query_type=pack`)
- `is_enabled` (bool, opzionale, default `true`)

Esempio `filters`:

```json
{
  "name": "python remote jobs",
  "query_type": "filters",
  "filters_json": "{\"skills_contains\":[\"python\"],\"location_type\":\"remote\",\"title_is_other\":false}",
  "is_enabled": true
}
```

Esempio `pack`:

```json
{
  "name": "high confidence tech",
  "query_type": "pack",
  "pack_name": "high_confidence_tech_jobs"
}
```

## Behavior
- `GET /saved-searches`: lista completa saved searches.
- `POST /saved-searches/{id}/enable|disable`: toggle `is_enabled`.
- `POST /saved-searches/{id}/run`: ritorna risultati correnti della search.
- `POST /saved-searches/{id}/check-new`: ritorna risultati correnti + delta `new_results`, aggiornando stato seen.

Parametri query:
- `run`: `limit`, `offset`
- `check-new`: `scan_limit`, `limit`, `offset`

## Error cases
- `404`: search inesistente (`saved search not found: ...`).
- `422`: payload invalido (es. `query_type=pack` senza `pack_name`, o body non valido).

## Config
L'API usa un DB saved searches configurabile:
- env: `JOBINTEL_SAVED_DB_PATH`
- override app factory: `create_app(saved_db_path=...)`
- default: `data/jobs/saved_searches.db`

## Esempi cURL

```bash
curl http://127.0.0.1:8000/saved-searches
```

```bash
curl -X POST http://127.0.0.1:8000/saved-searches \
  -H "Content-Type: application/json" \
  -d '{"name":"python remote jobs","query_type":"filters","filters_json":"{\"skills_contains\":[\"python\"],\"location_type\":\"remote\",\"title_is_other\":false}"}'
```

```bash
curl -X POST "http://127.0.0.1:8000/saved-searches/<search_id>/run?limit=50&offset=0"
```

```bash
curl -X POST "http://127.0.0.1:8000/saved-searches/<search_id>/check-new?scan_limit=5000&limit=100&offset=0"
```

## Limiti noti
- Nessuna auth/multi-user.
- Nessun scheduler distribuito.
- Nessun canale delivery orchestrato via API in questo step (solo foundation locale già presente).

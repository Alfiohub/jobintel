# Scheduling / Daily Digest Foundation v1 (Step 47)

## Obiettivo
Ridurre la manualità del workflow alert introducendo una base di scheduling semplice, cron-friendly e per-user.

## Frequenze supportate
Ogni saved search ora ha il campo `frequency`:
- `manual`
- `daily`
- `twice_daily`

Default: `daily`.

## Modello / Storage aggiornato
`saved_searches` ora include:
- `frequency TEXT NOT NULL DEFAULT 'daily'`

Migrazione pragmatica:
- se colonna assente viene aggiunta
- valori null/invalidi vengono normalizzati a `daily`

Modulo: `src/jobintel_next/product/saved_searches/service.py`

## Due logic
Funzione: `is_saved_search_due(saved_search, now=...)`

Regole:
1. `is_enabled=false` -> non dovuta
2. `frequency=manual` -> non dovuta
3. `frequency=daily` -> dovuta se:
   - `last_run_at` assente, oppure
   - sono passate almeno 24h
4. `frequency=twice_daily` -> dovuta se:
   - `last_run_at` assente, oppure
   - sono passate almeno 12h

## Runner due-only
Nuova funzione:
- `run_due_saved_searches(...)`

Comportamento:
- legge le saved searches dell’utente
- esegue solo quelle dovute
- produce artifact run per-user come gli altri runner
- summary con:
  - `searches_total`
  - `searches_due`
  - `searches_skipped_not_due`
  - `processed_ok`
  - `processed_error`
  - `total_new_matches`

Modulo: `src/jobintel_next/product/saved_searches/runner.py`

## Command cron-friendly
Nuovo comando:

```bash
uv run jobintel-next alerts run-due \
  --saved-db data/jobs/saved_searches.db \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db \
  --outdir data/alerts/runs \
  --user-id local-user \
  --user-email local@example.com
```

Output:
- `run_id`
- `searches_total`
- `searches_due`
- `searches_skipped_not_due`
- `total_new_matches`
- path artifact JSON/MD

## Integrazione CRUD API/UI
`frequency` è ora gestita in:
- API request/response saved searches
  - `POST /saved-searches`
  - `POST /saved-searches/{search_id}/update`
- Admin UI create/edit/list saved searches
  - `/admin/saved-searches/new`
  - `/admin/saved-searches/{search_id}/edit`
  - `/admin/saved-searches`

## Esempio cron locale
Esecuzione ogni ora (cron):

```cron
0 * * * * cd /path/to/joballert2 && uv run jobintel-next alerts run-due --saved-db data/jobs/saved_searches.db --input data/jobs/jobs_indexed_en.jsonl --sqlite data/jobs/jobs_indexed_en.db --outdir data/alerts/runs --user-id local-user --user-email local@example.com
```

La due-logic evita esecuzioni troppo frequenti sulle search `daily`/`twice_daily`.

## Test aggiunti
- `tests/product/test_scheduling_step47.py`
  - due logic (`manual`, `daily`, `twice_daily`)
  - `run_due_saved_searches` esegue solo le search dovute

Test aggiornati:
- `tests/product/test_saved_searches_step24.py`
- `tests/api/test_saved_searches_api_step27.py`
- `tests/api/test_admin_ui_step30.py`

## Limiti noti
- nessun scheduler distribuito
- nessuna queue/retry avanzata
- nessuna finestra oraria sofisticata per utente
- digest multi-canale non incluso in questo step

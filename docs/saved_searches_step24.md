# Saved Searches / Alerts Foundation Step 24

## Obiettivo
Introdurre la base interna per saved searches/alerts:
- definizione query salvata
- persistenza
- esecuzione
- rilevazione nuovi match

Senza canali di delivery esterni (email/telegram/push) in questo step.

## Modulo
- `src/jobintel_next/product/saved_searches/service.py`
- `src/jobintel_next/product/saved_searches/__init__.py`

## Modello SavedSearch (v1)
Campi:
- `search_id`
- `name`
- `query_type` (`filters` | `pack`)
- `filters_json` (solo per `filters`)
- `pack_name` (solo per `pack`)
- `is_enabled`
- `created_at`
- `updated_at`
- `last_run_at` (opzionale)
- `last_seen_job_url` (opzionale)

Storage:
- SQLite dedicato (default): `data/jobs/saved_searches.db`
- Tabelle:
  - `saved_searches`
  - `saved_search_seen` (set URL visti per delta detection)

## Operazioni implementate
- `create_saved_search(...)`
- `list_saved_searches()`
- `enable_saved_search(search_id)`
- `disable_saved_search(search_id)`
- `run_saved_search(search_id)`
- `check_new_matches(search_id)`

## Strategia delta (new matches)
`check_new_matches`:
1. esegue la search corrente (`filters` o `pack`)
2. confronta gli URL correnti con `saved_search_seen`
3. `new_matches = current_urls - seen_urls`
4. aggiorna `saved_search_seen`, `last_run_at`, `last_seen_job_url`

Approccio semplice e deterministico, senza scheduler/canali di notifica.

## Command CLI
Create (filters):

```bash
uv run jobintel-next saved-search create \
  --name "python remote jobs" \
  --query-type filters \
  --filters-json '{"skills_contains":["python"],"location_type":"remote","title_is_other":false}'
```

Create (pack):

```bash
uv run jobintel-next saved-search create \
  --name "high confidence tech" \
  --query-type pack \
  --pack-name high_confidence_tech_jobs
```

List:

```bash
uv run jobintel-next saved-search list
```

Enable/Disable:

```bash
uv run jobintel-next saved-search disable --id <search_id>
uv run jobintel-next saved-search enable --id <search_id>
```

Run:

```bash
uv run jobintel-next saved-search run \
  --id <search_id> \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db \
  --limit 100 --offset 0
```

Check new:

```bash
uv run jobintel-next saved-search check-new \
  --id <search_id> \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db \
  --scan-limit 5000 --limit 100 --offset 0
```

## Limiti noti
- Nessun scheduler automatico.
- Nessun canale di delivery (email/telegram/push).
- Nessun multi-user/auth.
- Delta basato su URL visti (pragmatico, non event sourcing completo).

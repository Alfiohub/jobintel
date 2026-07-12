# Saved Search Runner / Local Alerts Step 25

## Obiettivo
Eseguire in batch tutte le saved searches abilitate, calcolare i nuovi match e produrre artifact locali (JSON/MD) senza canali notifiche esterni.

## Modulo
- `src/jobintel_next/product/saved_searches/runner.py`

Funzione principale:
- `run_enabled_saved_searches(...)`

## Come funziona
1. legge tutte le saved searches da DB
2. filtra solo `is_enabled = true`
3. per ogni search esegue `check_new_matches(...)`
4. raccoglie summary run + dettaglio per search
5. scrive artifact locali:
   - `data/alerts/runs/<timestamp>.json`
   - `data/alerts/runs/<timestamp>.md`

Per ogni search include:
- `search_id`
- `name`
- `query_type`
- `enabled`
- `total_current_matches`
- `new_matches_count`
- `sample_new_matches`
- `run_timestamp`

## Command CLI

```bash
uv run jobintel-next saved-search run-all \
  --saved-db data/jobs/saved_searches.db \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db \
  --outdir data/alerts/runs \
  --scan-limit 5000 \
  --limit 200 \
  --sample-size 5
```

Output CLI:
- `run_id`
- `searches_enabled`
- `processed_ok`
- `processed_error`
- `total_new_matches`
- path report JSON/MD

## Esempio artifact JSON (shape)

```json
{
  "run_id": "20260330T120000Z",
  "searches_total": 3,
  "searches_enabled": 2,
  "searches_disabled": 1,
  "processed_ok": 2,
  "processed_error": 0,
  "total_new_matches": 4,
  "results": [
    {
      "search_id": "...",
      "name": "high confidence tech",
      "query_type": "pack",
      "enabled": true,
      "total_current_matches": 8677,
      "new_matches_count": 2,
      "sample_new_matches": [{ "url": "...", "title_raw": "..." }]
    }
  ]
}
```

## Limiti noti
- Nessun scheduler automatico.
- Nessuna delivery (email/telegram/push).
- Nessuna gestione multi-user/auth.
- Batch locale sincrono.

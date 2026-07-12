# Storage Step 22 (SQLite v1)

## Obiettivo
Introdurre uno storage operativo minimo per `IndexedJob` usando SQLite, così serving/API possono usare backend persistente senza scan JSONL completo.

## Moduli introdotti
- `src/jobintel_next/storage/schema.py`
- `src/jobintel_next/storage/build.py`
- `src/jobintel_next/storage/query.py`
- `src/jobintel_next/storage/__init__.py`

## Schema SQLite (`jobs_indexed`)
Colonne principali:
- `url` (PK)
- `source`, `source_org`, `company_name`
- `title_raw`, `title_clean`
- `normalized_title`, `role_family`
- `classification_status`, `match_method`, `confidence`
- `language_bucket`, `language_reason`, `language_code`, `language_confidence`
- `published_at`, `updated_at`
- `seniority`, `employment_type`, `location_type`
- `city`, `region`, `country`
- `salary_min`, `salary_max`, `salary_currency`, `salary_period`
- `has_salary`, `has_skills`, `has_location`, `title_is_other` (int bool)
- `skills_json` (JSON array serializzato)

Indici:
- `normalized_title`, `role_family`, `language_bucket`
- `location_type`, `employment_type`
- `has_salary`, `has_skills`, `title_is_other`
- `salary_currency`
- `published_at`, `updated_at`

## Command operativo
Build/rebuild index SQLite da JSONL:

```bash
uv run jobintel-next storage build-index \
  --input data/jobs/jobs_indexed_en.jsonl \
  --sqlite data/jobs/jobs_indexed_en.db
```

## Query supportate su SQLite
- `list_jobs(filters..., limit, offset)`
- `count_jobs(filters...)`
- `run_pack(pack_name, limit, offset)`
- `count_pack(pack_name)`

Filtri supportati:
- `normalized_title`
- `role_family`
- `language_bucket`
- `location_type`
- `employment_type`
- `has_salary`
- `has_skills`
- `title_is_other`
- `skills_contains` (match su `skills_json`)
- `salary_currency`

## Integrazione serving/API
- Serving layer ora supporta backend swappable:
  - default JSONL
  - SQLite se passato `sqlite_path`
- CLI `serve` supporta `--sqlite`:
  - `serve query/count/pack/pack-count --sqlite data/jobs/jobs_indexed_en.db`
- API supporta SQLite via env:
  - `JOBINTEL_SQLITE_PATH=data/jobs/jobs_indexed_en.db`
  - fallback JSONL se env non impostata

## Limiti noti
- Nessun full-text search
- Nessuna semantic search
- Nessun ranking avanzato
- Nessuna auth
- `skills_contains` usa matching su stringa JSON (pragmatico, non semantico)

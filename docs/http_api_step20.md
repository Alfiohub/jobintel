# HTTP API Step 20

Base: FastAPI app in `src/jobintel_next/app/api/app.py` (in-memory/local on `jobs_indexed_en.jsonl`).

## Endpoints
- `GET /health`
- `GET /jobs`
- `GET /jobs/count`
- `GET /packs`
- `GET /packs/{pack_name}`
- `GET /packs/{pack_name}/count`

## Query Params
`GET /jobs` and `GET /jobs/count` support:
- `normalized_title`
- `role_family`
- `language_bucket`
- `location_type`
- `employment_type`
- `has_salary`
- `has_skills`
- `title_is_other`
- `skills_contains` (repeatable)
- `salary_currency`

Only `GET /jobs` supports also:
- `sort_by`: `published_at_desc | updated_at_desc | url`
- `limit` (default `20`)
- `offset` (default `0`)

`GET /packs/{pack_name}` supports:
- `limit` (default `20`)
- `offset` (default `0`)

## Response Shape
`GET /jobs`:
- `operation`
- `query`
- `total_count`
- `limit`
- `offset`
- `returned_count`
- `results`

`GET /jobs/count`:
- `operation`
- `query`
- `count`

`GET /packs`:
- `packs` with `name`, `description`, `quality`, `tradeoff`

`GET /packs/{pack_name}`:
- `operation`
- `pack_name`
- `description`
- `quality`
- `tradeoff`
- `clauses`
- `total_count`
- `limit`
- `offset`
- `returned_count`
- `results`

`GET /packs/{pack_name}/count`:
- `operation`
- `pack_name`
- `count`

## Examples
Run local API:

```bash
uv run uvicorn jobintel_next.app.api.app:app --reload
```

Jobs list:

```bash
curl "http://127.0.0.1:8000/jobs?normalized_title=account_executive&limit=5&offset=0"
```

Jobs count:

```bash
curl "http://127.0.0.1:8000/jobs/count?role_family=marketing&has_salary=true"
```

Pack run:

```bash
curl "http://127.0.0.1:8000/packs/high_confidence_tech_jobs?limit=5&offset=0"
```

Pack count:

```bash
curl "http://127.0.0.1:8000/packs/python_tech_jobs/count"
```

## Known Limits
- Local JSONL scan (no persistent DB/index yet).
- No auth.
- No advanced ranking.
- No semantic search.
- No caching layer yet.

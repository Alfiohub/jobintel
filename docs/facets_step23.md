# Facets / Aggregations Step 23

## Obiettivo
Aggiungere aggregazioni/facet utili al frontend UX sopra serving/storage attuali.

## Moduli introdotti
- `src/jobintel_next/serving/facets.py`
- estensione SQLite facets in `src/jobintel_next/storage/query.py`
- endpoint API `GET /facets` in `src/jobintel_next/app/api/router.py`

## Facet disponibili
- `role_family`
- `normalized_title`
- `location_type`
- `employment_type`
- `language_bucket`
- `has_salary`
- `has_skills`
- `title_is_other`
- `salary_currency`

## Come funziona
- Facet globali: nessun filtro passato.
- Facet su subset: si passano gli stessi filtri di `/jobs`.
- Il backend applica i filtri prima di aggregare.

Filtri supportati su `/facets`:
- `normalized_title`
- `role_family`
- `language_bucket`
- `location_type`
- `employment_type`
- `has_salary`
- `has_skills`
- `title_is_other`
- `skills_contains`
- `salary_currency`

## Endpoint API
- `GET /facets`

Esempio:

```bash
curl "http://127.0.0.1:8000/facets?role_family=marketing&has_salary=true"
```

Risposta (shape):

```json
{
  "operation": "get_facets",
  "input_path": "data/jobs/jobs_indexed_en.db",
  "backend": "sqlite",
  "query": {...},
  "total_count": 1584,
  "facets": {
    "role_family": [{"value": "marketing", "count": 1584}],
    "location_type": [{"value": "remote", "count": 700}, ...],
    "has_salary": [{"value": true, "count": 1584}],
    "salary_currency": [{"value": "USD", "count": 1300}, ...]
  }
}
```

## Backend support
- SQLite: supportato e consigliato (path principale).
- JSONL: fallback disponibile nel serving layer.

## Limiti noti
- Nessun caching aggregazioni.
- Nessuna semantic search/ranking.
- `skills_contains` su SQLite usa match su `skills_json` (pragmatico).

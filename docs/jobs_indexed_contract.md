# jobs_indexed Data Contract (MVP Stable)

Questo documento definisce il contratto logico stabile della vista/tabella `jobs_indexed`.
Serve per evitare regressioni tra pipeline, API e frontend.

## Contract Version
- `jobs_indexed_contract_version = v2`

## Stable Fields

### Identità e sorgente
- `id` (INTEGER): id record indicizzato
- `clean_job_id` (INTEGER): FK logica verso `jobs_clean`
- `source` (TEXT): sorgente (`greenhouse`, ...)
- `source_job_id` (TEXT): id annuncio sorgente
- `source_org` (TEXT): slug org/board
- `url` (TEXT): URL annuncio

### Company / title
- `company_name` (TEXT)
- `title_raw` (TEXT)
- `title_clean` (TEXT)
- `normalized_title` (TEXT)
- `role_family` (TEXT)
- `occupation_group` (TEXT)

### Attributi job
- `seniority` (TEXT | NULL)
- `employment_type` (TEXT | NULL)
- `location_type` (TEXT | NULL)
- `city` (TEXT | NULL)
- `region` (TEXT | NULL)
- `country` (TEXT | NULL)

### Compensation
- `salary_min` (INTEGER | NULL)
- `salary_max` (INTEGER | NULL)
- `salary_currency` (TEXT | NULL)

### Experience / education (v0.2 foundations)
- `experience_years_min` (INTEGER | NULL)
- `experience_years_max` (INTEGER | NULL)
- `experience_required` (INTEGER 0/1 | NULL)
- `experience_text_raw` (TEXT | NULL)
- `education_level` (TEXT | NULL)
- `degree_required` (INTEGER 0/1 | NULL)
- `education_text_raw` (TEXT | NULL)

### Skills / tags
- `skills_json` (TEXT JSON array, never NULL; default `[]`)
- `tags_json` (TEXT JSON object, never NULL; default `{}`)

### Embedding / quality
- `embedding_json` (TEXT JSON array | NULL)
- `embedding_model` (TEXT | NULL)
- `tagger_version` (TEXT | NULL)
- `tag_confidence` (REAL | NULL)

### Metadata
- `indexed_at` (TEXT ISO datetime)
- `content_hash` (TEXT | NULL)
- `processing_state` (TEXT | NULL)
- `first_seen_at` (TEXT ISO datetime | NULL)
- `last_seen_at` (TEXT ISO datetime | NULL)
- `processing_version` (TEXT | NULL)
- `extraction_version` (TEXT | NULL)

## Allowed values (MVP)
- `location_type`: `remote | hybrid | onsite`
- `employment_type`: `full_time | part_time | contract | internship | temporary`
- `salary_currency`: ISO uppercase (`USD`, `EUR`, ...)

## API Coupling
Questo contratto alimenta:
- `GET /v1/indexed/jobs`
- `GET /v1/indexed/filters/options`
- `GET /ui-indexed`

Ogni breaking change a `jobs_indexed` richiede:
1. update di questo file
2. update API/frontend
3. update test/benchmark.

## Non-goals in MVP
- campi enterprise avanzati (es. `salary_period`, degree major taxonomy) non sono parte del contratto stabile MVP.
- eventuali campi aggiuntivi sono backward-compatible solo se opzionali.

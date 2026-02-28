# Project Structure

This file is the source of truth for where things belong.

## Runtime application
- `src/jobintel/`
  - current production/runtime code
  - ingestion, enrichment, scoring, API, storage, UI

## Monorepo target modules (incremental migration)
- `modules/ingestion/`
- `modules/intelligence-runtime/`
- `modules/api-saas/`
- `modules/frontend/`
- `modules/ner-training/`
- `modules/shared-contracts/`

Notes:
- During migration, runtime remains in `src/jobintel/*`.
- New code should respect module ownership and boundaries.

## Data and artifacts
- `data/`: local datasets and DB files (ignored by git)
- `artifacts/`: model artifacts and outputs

## Config and scripts
- `config/`: source and generated configuration
- `scripts/`: operational scripts and data/NER tooling

## Tests
- `tests/`: automated tests
- `test_Api.py`: legacy ad-hoc test script (keep for now, consider moving under `tests/`)

## Contracts and architecture
- `openapi_v1.yaml`
- `db_schema_v1.sql`
- `architecture_v1.md`

## Rule
If a file does not clearly belong to a section above, document it before committing.

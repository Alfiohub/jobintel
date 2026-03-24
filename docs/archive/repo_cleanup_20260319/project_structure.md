# Project Structure

This file is the source of truth for where things belong.

## Primary Product Flow (current priority)
- `ingest -> clean -> normalize_title -> tag -> embed -> index -> search`
- Keep this flow in runtime code under `src/jobintel/*`.
- Keep NER experiments isolated from this path.

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
- `automation/`: operational scripts and tooling
  - `automation/microsaas/`: primary product-flow automation (batch indexing, export)
  - `automation/legacy_ner/`: archived/experimental NER helpers
  - root-level `automation/*.py` only for generic ops not tied to a specific pipeline

## Tests
- `tests/`: automated tests
- `test_Api.py`: legacy ad-hoc test script (keep for now, consider moving under `tests/`)

## Contracts and architecture
- `openapi_v1.yaml`
- `db_schema_v1.sql`
- `architecture_v1.md`

## Rule
If a file does not clearly belong to a section above, document it before committing.

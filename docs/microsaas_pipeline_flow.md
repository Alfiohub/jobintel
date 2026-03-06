# Micro-SaaS Pipeline Flow

This document is the single operational flow to follow from now on.

## Goal
Produce searchable and filterable jobs for a micro-SaaS with:
- deterministic tags for filtering
- semantic vectors for similarity search
- incremental processing for new jobs only

## End-to-End Flow
1. `ingest`
- Fetch jobs from ATS/API pages.
- Save raw payloads unchanged.

2. `clean`
- Strip HTML/boilerplate.
- Keep compact text sections (title, requirements, responsibilities).
- Compute `content_hash` for dedup/reuse.

3. `normalize_title`
- Map `title_raw` to `normalized_title`.
- Derive `role_family` and `occupation_group`.

4. `tag`
- Extract: `skills`, `seniority`, `location_type`, `employment_type`, `salary`.
- Use deterministic rules first, LLM fallback only when confidence is low.

5. `embed`
- Compute embedding on cleaned compact text.
- Store vector once per unique content hash.

6. `index`
- Build indexed records for query (`jobs_indexed`-style view/table).
- Keep tag fields queryable and normalized.

7. `search`
- Hybrid retrieval:
  - SQL filters on normalized fields/tags
  - vector similarity for semantic search

## Data Model (minimum)
- `raw_jobs`: source payload and fetch metadata
- `jobs_clean`: cleaned text + hash
- `jobs_indexed`: normalized title + tags + embedding + URL/company metadata
- optional cache table keyed by `content_hash` for tags/embedding reuse

## Rules of Execution
- Never reprocess all jobs if not needed.
- Reuse by `content_hash` first.
- Process deltas in background batches.
- Keep one canonical output schema for indexed jobs.

## Immediate Checkpoints
1. Freeze and archive NER experiments from the critical path.
2. Add one batch command to run: `ingest -> clean -> normalize_title -> tag -> embed -> index`.
3. Add smoke test on a small sample (`10-50` jobs).

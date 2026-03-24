# Micro-SaaS Data Contracts

This file defines stable I/O contracts between pipeline stages.

## Canonical Stage Contracts

### 1) `ingest` output (`raw_job`)
```json
{
  "source": "greenhouse",
  "source_job_id": "9930",
  "source_org": "justworks",
  "url": "https://boards.greenhouse.io/justworks/jobs/9930?gh_jid=9930",
  "title_raw": "Account Executive - NYC - Hybrid",
  "company_raw": "Justworks",
  "location_raw": "New York, NY",
  "description_raw": "<html or text>",
  "language_hint": "en",
  "payload_json": {},
  "fetched_at": "2026-03-05T10:00:00Z"
}
```

### 2) `clean` output (`clean_job`)
```json
{
  "raw_job_id": 123,
  "title_clean": "Account Executive",
  "description_clean": "Responsible for full sales cycle ...",
  "requirements_clean": "3+ years ...",
  "responsibilities_clean": "Prospect, close, ...",
  "location_clean": "New York, NY",
  "language": "en",
  "content_hash": "sha256-hex",
  "content_fingerprint": "optional-near-dup",
  "cleaned_at": "2026-03-05T10:01:00Z"
}
```

### 3) `normalize_title` output (partial enrichment)
```json
{
  "normalized_title": "account_executive",
  "role_family": "sales",
  "occupation_group": "business"
}
```

### 4) `tag` output (partial enrichment)
```json
{
  "seniority": "mid",
  "employment_type": "full_time",
  "location_type": "hybrid",
  "city": "New York",
  "region": "NY",
  "country": "US",
  "salary_min": 100000,
  "salary_max": 140000,
  "salary_currency": "USD",
  "skills": ["crm", "pipeline_management", "sales"],
  "tags": {
    "seniority": "mid",
    "remote": false
  },
  "tagger_version": "rules_v1",
  "tag_confidence": 0.92
}
```

### 5) `embed` output
```json
{
  "embedding": [0.0123, -0.044, 0.981],
  "embedding_model": "text-embedding-3-small"
}
```

### 6) `index` output (`indexed_job`)
```json
{
  "clean_job_id": 456,
  "source": "greenhouse",
  "source_job_id": "9930",
  "source_org": "justworks",
  "url": "https://boards.greenhouse.io/justworks/jobs/9930?gh_jid=9930",
  "company_name": "Justworks",
  "title_raw": "Account Executive - NYC - Hybrid",
  "title_clean": "Account Executive",
  "normalized_title": "account_executive",
  "role_family": "sales",
  "occupation_group": "business",
  "seniority": "mid",
  "employment_type": "full_time",
  "location_type": "hybrid",
  "city": "New York",
  "region": "NY",
  "country": "US",
  "salary_min": 100000,
  "salary_max": 140000,
  "salary_currency": "USD",
  "skills": ["crm", "pipeline_management", "sales"],
  "tags": {
    "seniority": "mid",
    "remote": false
  },
  "embedding": [0.0123, -0.044, 0.981],
  "embedding_model": "text-embedding-3-small",
  "tagger_version": "rules_v1",
  "tag_confidence": 0.92,
  "indexed_at": "2026-03-05T10:03:00Z"
}
```

## Normalization Notes
- `normalized_title`, `role_family`, `occupation_group` must come from controlled vocabularies.
- `employment_type` allowed values:
  - `full_time`, `part_time`, `contract`, `internship`, `temporary`
- `location_type` allowed values:
  - `remote`, `hybrid`, `onsite`
- `salary_currency` must be ISO uppercase (`USD`, `EUR`, ...).

## Execution Guarantees
- Every `jobs_clean` row must have one `content_hash`.
- `extraction_cache` is keyed by `content_hash` to skip repeated expensive calls.
- `jobs_indexed` is the only table/API source used by search endpoints.

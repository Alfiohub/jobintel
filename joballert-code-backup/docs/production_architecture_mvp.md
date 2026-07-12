# Production Architecture (MVP)

## 1) System Overview
```mermaid
flowchart LR
    A[Job Sources\nGreenhouse/ATS exports] --> B[Ingestion Pipeline\nautomation/microsaas/run_microsaas_pipeline.py]
    B --> C[(SQLite MVP DB\ndata/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite)]

    C --> D[Search API\nautomation/microsaas/search_api.py]
    D --> E[Web UI / Landing\nMVP client]

    C --> F[Batch QA / Eval Tools\nautolabel, review_analysis, labelstudio export]
    F --> G[Taxonomy Ops\nauto_expand_taxonomy.py\napply_map_existing_safe.py\nvalidate_and_promote_taxonomy.py]
    G --> H[title_normalization.py\nTITLE_RULES update]
    H --> B
```

## 2) Runtime Query Path (User Search)
```mermaid
sequenceDiagram
    participant U as User
    participant UI as MVP UI
    participant API as Search API
    participant DB as SQLite DB

    U->>UI: Search (title/country/location_type)
    UI->>API: HTTP request
    API->>DB: SQL query + ranking filters
    DB-->>API: Matching jobs
    API-->>UI: JSON results
    UI-->>U: Ranked job list
```

## 3) Data Build / Refresh Path
```mermaid
sequenceDiagram
    participant SRC as Source files (JSONL)
    participant PIPE as run_microsaas_pipeline.py
    participant DB as SQLite DB
    participant API as Search API

    SRC->>PIPE: New/updated raw jobs
    PIPE->>PIPE: cleaning + enrichment + normalization
    PIPE->>DB: upsert raw_jobs/jobs_clean/jobs_indexed
    API->>DB: reads latest indexed jobs
```

## 4) Taxonomy Improvement Loop (Controlled)
```mermaid
flowchart TD
    A[Production data with some 'other'] --> B[auto_expand_taxonomy.py\ncreates candidates]
    B --> C[apply_map_existing_safe.py\nauto-safe mappings]
    C --> D[validate_and_promote_taxonomy.py\nquality gates]
    D -->|pass| E[Promote patch to TITLE_RULES]
    D -->|fail| F[Keep as other + report]
    E --> G[Re-run pipeline on validation sample]
    G --> H[If metrics improve -> release]
```

## 5) Deployment View (MVP)
```mermaid
flowchart LR
    subgraph Container_or_VM[Single host (Docker/VM)]
      API[Search API process]
      DB[(SQLite file volume)]
      CRON[Scheduled batch jobs\n(optional cron)]
    end

    API <--> DB
    CRON --> DB
```

## 6) Branching Model
```mermaid
flowchart LR
    M[main/stable] --> P[mvp/prod-hardening]
    M --> R[research/taxonomy-and-model]
    R -->|small validated patches| P
    P -->|release| M
```

## Notes
- MVP production now is intentionally simple: `Search API + SQLite + batch pipeline`.
- No external queue/cache is required for first customer tests.
- Taxonomy/model improvements stay isolated in research branch and are promoted only after checks.

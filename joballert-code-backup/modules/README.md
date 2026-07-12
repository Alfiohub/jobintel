# Monorepo Modules

1. `ingestion`
2. `intelligence-runtime`
3. `api-saas`
4. `frontend`
5. `ner-training`
6. `shared-contracts`

Stato attuale: transizione. Il codice runtime attuale resta in `src/jobintel/*` e viene migrato per step.

Ownership rapida:
- `ingestion`: connettori ATS + normalizzazione
- `intelligence-runtime`: enrichment/scoring/matching runtime
- `api-saas`: API HTTP, auth boundary, ops, billing readiness
- `frontend`: UI che consuma solo API
- `ner-training`: annotazione + train/eval
- `shared-contracts`: OpenAPI, schema DB, schema annotation

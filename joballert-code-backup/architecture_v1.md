# Architecture v1 - Joballert

## Obiettivo
Separare il progetto in moduli chiari per sviluppare in parallelo senza regressioni.

## Moduli
1. Data layer (ATS ingestion)
2. Intelligence runtime (enrichment/scoring/matching)
3. API/SaaS layer
4. Frontend layer
5. NER training layer
6. Shared contracts

## Monorepo layout
La repository usa `modules/` con i 6 moduli, mentre il runtime attuale resta in `src/jobintel/*` durante la migrazione.

## Contratti
- API contract: `openapi_v1.yaml`
- DB contract: `db_schema_v1.sql`
- NER schema: `docs/ner_annotation_schema.md`

## Regole di migrazione
- no big-bang rewrite
- compatibilita' endpoint legacy fino a completamento migrazione frontend
- ogni refactor deve mantenere test verdi

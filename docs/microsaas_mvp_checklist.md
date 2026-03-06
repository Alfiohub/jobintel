# Micro-SaaS MVP Checklist

Obiettivo: consegnare una prima versione stabile con indicizzazione job, filtri affidabili e ricerca semantica.

## Scope bloccato (MVP)
- Ingestion + indexing batch su dataset Greenhouse EN
- API filtri: `/v1/indexed/jobs`
- API opzioni filtri: `/v1/indexed/filters/options`
- Semantic search con `semantic_query` (`hash` default, `openai/gemini` opzionale)
- Nessun nuovo esperimento NER nel percorso principale

## Step 1 - Data pipeline stabile
- Esegui pipeline:
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/run_microsaas.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run \
  data/jobintel_microsaas.sqlite
```
- Verifica output:
  - `data/microsaas/run/raw_jobs.jsonl`
  - `data/microsaas/run/jobs_clean.jsonl`
  - `data/microsaas/run/jobs_indexed.jsonl`
  - `data/jobintel_microsaas.sqlite`

Definition of Done:
- Run senza errori
- Tabelle DB popolate: `raw_jobs`, `jobs_clean`, `jobs_indexed`, `extraction_cache`

## Step 2 - Qualità regole (hardening)
- Esegui test regole:
```bash
PYTHONPATH=. uv run --active pytest -q tests/test_microsaas_pipeline_rules.py
```
- Esegui test collegati:
```bash
PYTHONPATH=. uv run --active pytest -q tests/test_build_ner_subset.py tests/test_weak_label_greenhouse_phase2.py
```

Definition of Done:
- Tutti i test passano
- Nessuna regressione su salary/location_type/seniority/skills

## Step 3 - API pronta per frontend
- Avvia API:
```bash
uv run --active uvicorn jobintel.api:app --reload --port 8001
```
- Test manuale endpoint:
  - `GET /v1/indexed/jobs?db_path=data/jobintel_microsaas.sqlite`
  - `GET /v1/indexed/filters/options?db_path=data/jobintel_microsaas.sqlite`
  - `GET /v1/indexed/jobs?db_path=data/jobintel_microsaas.sqlite&semantic_query=data+engineer`

Definition of Done:
- Endpoint rispondono `200`
- Filtri principali funzionano (`role_family`, `seniority`, `location_type`, `employment_type`, `skill`)

## Step 4 - Decisione costi embedding
- Modalità default: `hash` (zero costo)
- Opzione premium:
  - `semantic_provider=openai` con `OPENAI_API_KEY`
  - `semantic_provider=gemini` con `GOOGLE_API_KEY`

Definition of Done:
- Scelta documentata: `hash-only` oppure `hybrid (hash + provider)`
- Limiti operativi decisi (quando usare provider)

## Step 5 - Frontend integration (minimo)
- Collegare UI a:
  - `GET /v1/indexed/jobs`
  - `GET /v1/indexed/filters/options`
- Mostrare:
  - lista lavori
  - filtri base
  - box ricerca semantica

Definition of Done:
- Utente riesce a filtrare e cercare semanticamente senza comandi manuali

## Non fare in MVP
- Nuovo training NER
- Nuove tassonomie grandi non validate
- Refactor estesi fuori `automation/microsaas` e `src/jobintel/api.py`

## Dopo MVP
- Vedi roadmap: `docs/microsaas_post_mvp_steps.md`

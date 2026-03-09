# jobintel

Pipeline di job intelligence per micro-SaaS: ingestione annunci, normalizzazione ruolo, tagging e indicizzazione per filtri/ricerca.

## Stato Del Repo
- `src/jobintel/*`: runtime attuale del prodotto
- `modules/*`: target architecture del monorepo, ancora in migrazione
- percorso principale: `ingest -> clean -> normalize_title -> tag -> embed -> index`
- NER/docs annotazione: archivio sperimentale (vedi `docs/ner_experiments_archive.md`)

## Mappa Progetto
- Runtime attuale: `src/jobintel/*`
- Moduli target (monorepo): `modules/*`
- Contratti:
  - `openapi_v1.yaml`
  - `db_schema_v1.sql`
  - `architecture_v1.md`
- Documentazione operativa: `docs/README.md`

## Cosa fa (primary path)
- Colleziona job da Greenhouse
- Pulisce testo e deduplica via hash contenuto
- Normalizza i job title in tassonomia interna
- Estrae tag utili (`skills`, `seniority`, `location_type`, `employment_type`, `salary`)
- Produce `jobs_indexed` pronto per filtri e ricerca semantica

Checklist esecuzione MVP: `docs/microsaas_mvp_checklist.md`
Checklist go-live MVP: `docs/mvp_go_live_checklist.md`
Documentazione tecnica MVP: `docs/mvp_technical_documentation.md`
Title taxonomy: `docs/title_taxonomy.md`
Data contract `jobs_indexed`: `docs/jobs_indexed_contract.md`
Skills taxonomy v1: `docs/skills_taxonomy_v1.md`
Template PR v0.2: `docs/pr_v0.2_template.md`
Roadmap post-MVP: `docs/microsaas_post_mvp_steps.md`
Policy embeddings/provider: `docs/embedding_policy.md`

## Requisiti
- Python 3.13
- `uv`

## Installazione
```bash
uv venv .venv --python 3.13
source .venv/bin/activate
uv pip install -e .
```

## Comando Unico (Micro-SaaS indexing)
Esegue pipeline batch locale end-to-end e produce:
- `raw_jobs.jsonl`
- `jobs_clean.jsonl`
- `jobs_indexed.jsonl`
- `pipeline_report.json` (KPI run: processed/skipped/updated/failed/cache_hits/runtime)
- SQLite (`raw_jobs`, `jobs_clean`, `jobs_indexed`, `extraction_cache`, `pipeline_runs`)

```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/run_microsaas.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run \
  data/jobintel_microsaas.sqlite
```

Retry per-riga (transient failures) via variabile ambiente:
```bash
ROW_MAX_RETRIES=2 MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/run_microsaas.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run \
  data/jobintel_microsaas.sqlite
```

Embedding reali:

```bash
# OpenAI
OPENAI_API_KEY=... EMBEDDING_MODE=openai \
OPENAI_EMBEDDING_MODEL=text-embedding-3-small \
./automation/microsaas/run_microsaas.sh

# Gemini
GOOGLE_API_KEY=... EMBEDDING_MODE=gemini \
GEMINI_EMBEDDING_MODEL=text-embedding-004 \
./automation/microsaas/run_microsaas.sh
```

Per smoke test rapido:
```bash
MAX_ROWS=50 ./automation/microsaas/run_microsaas.sh
```

Smoke E2E completo (test + pipeline + quality gates + API):
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/smoke_e2e_mvp.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run_smoke \
  data/jobintel_microsaas_smoke.sqlite
```
Il smoke verifica anche la presenza/consistenza di `pipeline_report.json`.

Benchmark qualità search (manual eval top-3):
```bash
uv run --active python automation/microsaas/report_search_eval.py \
  --csv docs/semantic_eval_top3_prefilled.csv \
  --out docs/search_benchmark_results_v1.md
```

Build gold eval set stratificato (Settimana 2):
```bash
uv run --active python automation/microsaas/build_gold_eval_set.py \
  --db data/jobintel_microsaas.sqlite \
  --out docs/gold_eval_set_v1.csv \
  --size 800 \
  --seed 42
```
Schema annotazione: `docs/gold_eval_annotation_schema.md`

Nota pratica su chiamate utente:
- Non è necessario chiamare OpenAI/Gemini a ogni request utente.
- Flusso consigliato: embedding annunci calcolati offline in indexing; in runtime utente fai SQL filtri.
- Chiama provider solo per query semantica (`semantic_query`) per generare embedding query, oppure usa fallback locale/hash per zero-costo.

## API (per frontend)
Avvia un’API HTTP per filtrare i job dal frontend.
```bash
uv run --active uvicorn jobintel.api:app --reload --port 8001
```

Esempi:
- `http://127.0.0.1:8001/jobs`
- `http://127.0.0.1:8001/v1/jobs`
- `http://127.0.0.1:8001/v1/indexed/jobs`
- `http://127.0.0.1:8001/v1/indexed/filters/options`
- `http://127.0.0.1:8001/v1/indexed/jobs?semantic_query=python+data+engineer` (default `semantic_provider=hash`)
- `http://127.0.0.1:8001/v1/indexed/jobs?semantic_query=python+data+engineer&semantic_provider=openai` (`OPENAI_API_KEY` richiesto)
- `http://127.0.0.1:8001/v1/indexed/jobs?semantic_query=python+data+engineer&semantic_provider=gemini` (`GOOGLE_API_KEY` richiesto)
- `http://127.0.0.1:8001/jobs?min_score=80`
- `http://127.0.0.1:8001/jobs?remote=true`
- `http://127.0.0.1:8001/jobs?location=Europe`
- `http://127.0.0.1:8001/jobs?date_from=2026-02-01&date_to=2026-02-12`

Per usare il DB micro-SaaS:
- `http://127.0.0.1:8001/v1/indexed/jobs?db_path=data/jobintel_microsaas.sqlite`

## Config (opzionale)
Esempi:
- `config/default.yml`
- `config/examples/data_analyst.yml`
- `config/examples/local.example.yml`

## Dove finiscono i dati
- runtime storico: `data/jobintel.sqlite`
- pipeline micro-SaaS: file in `data/microsaas/*` e DB in `data/jobintel_microsaas.sqlite`

## Test rapidi
```bash
uv run --active pytest -q
```

Baseline qualità (2000 annunci EN):
- `other_like`: `10.75%`
- `salary_outlier_gt1M`: `0`

## Sicurezza
- Non committare chiavi/API token.
- Usa variabili ambiente per script locali e non versionare config/secrets locali.

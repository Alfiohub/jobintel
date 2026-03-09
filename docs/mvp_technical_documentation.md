# MVP Technical Documentation (v0.1.0-mvp)

Questo documento descrive in modo completo cosa fa il codice MVP, come funziona, cosa è incluso e cosa no.

## Summary
This PR delivers MVP `v0.1.0-mvp` for the micro-SaaS job intelligence flow.

## Included
- End-to-end batch pipeline: ingest -> clean -> normalize_title -> tag -> embed -> index
- Dataset run on 2000 Greenhouse EN jobs
- Indexed API endpoints:
  - `/v1/indexed/jobs`
  - `/v1/indexed/filters/options`
- Semantic search providers:
  - `hash`, `openai`, `gemini`
- Hybrid semantic rerank with:
  - `semantic_score`
  - `hybrid_score`
  - `mismatch_penalty`
- Title normalization hardening and salary parsing fixes
- Benchmark/eval tooling:
  - semantic benchmark report
  - top-3 eval CSV (+ prefilled)

## Quality checks
- Pipeline run successful on 2000 rows
- `other_like` reduced to ~10.75%
- salary outliers (`>1,000,000`) reduced to 0
- API smoke checks passed
- tests passed for microsaas rules (`23 passed`)

## Docs
- `docs/release_notes_v0.1.0-mvp.md`
- `docs/mvp_go_live_checklist.md`
- `docs/embedding_policy.md`
- `docs/title_taxonomy.md`
- `docs/jobs_indexed_contract.md`
- `docs/skills_taxonomy_v1.md`

## Release
- Tag pushed: `v0.1.0-mvp`

---

## 1) System overview
Il sistema ha due blocchi principali:
- **Batch indexing** (offline): trasforma annunci grezzi in record strutturati e ricercabili.
- **Search API** (runtime): espone filtri + ricerca semantica per frontend.

### Input/Output principali
- Input: `data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl`
- Output:
  - `data/microsaas/run/raw_jobs.jsonl`
  - `data/microsaas/run/jobs_clean.jsonl`
  - `data/microsaas/run/jobs_indexed.jsonl`
  - `data/jobintel_microsaas.sqlite`

---

## 2) Batch pipeline
Script principale:
- `automation/microsaas/run_microsaas_pipeline.py`

Runner:
- `automation/microsaas/run_microsaas.sh`

Fasi:
1. **Ingest raw**: salva payload e metadati sorgente.
2. **Clean**: normalizza testo, HTML strip, sezioni.
3. **Normalize title**: mappa varianti titolo su tassonomia interna.
4. **Tag extraction (rules_v1)**:
   - `seniority`
   - `employment_type`
   - `location_type`
   - `skills`
   - `salary_*` con regole anti-false-positive.
5. **Embedding**:
   - `none` / `hash` / `openai` / `gemini`
6. **Index & cache**:
   - scrive `jobs_indexed`
   - cache per `content_hash` in `extraction_cache`.

### 2.1) Incremental, idempotency e retry policy (v0.2 foundation)
- Processing incrementale per job:
  - `new` se non esiste precedente record con stesso `source+url`
  - `skipped` se `content_hash` invariato
  - `updated` se `content_hash` cambiato
  - `failed` su errore non recuperabile
- Retry per-riga:
  - savepoint DB per singolo record
  - rollback/release savepoint su errore
  - nessuna scrittura parziale in caso di failure di una riga
  - tentativi configurabili con `ROW_MAX_RETRIES`
- Osservabilità run:
  - tabella `pipeline_runs` con contatori (`processed/skipped/updated/failed/cache_hits`)
  - artifact `pipeline_report.json` generato a ogni run

---

## 3) Database model (MVP)
Schema:
- `db_schema_microsaas.sql`
- Data contract:
  - `docs/jobs_indexed_contract.md`

Tabelle usate nel flusso MVP:
- `raw_jobs`
- `jobs_clean`
- `jobs_indexed`
- `extraction_cache`

Obiettivo design:
- separare `raw` da `normalized/indexed`
- permettere reprocessing senza perdere origine.

---

## 4) API model (MVP)
File:
- `src/jobintel/api.py`

Endpoint principali:
- `GET /v1/indexed/jobs`
- `GET /v1/indexed/filters/options`

Endpoint UI:
- `GET /ui-indexed` (frontend MVP utente)

### Parametri chiave `/v1/indexed/jobs`
- Filtri: `role_family`, `seniority`, `location_type`, `employment_type`, `skill`, `country`, ecc.
- Semantica: `semantic_query`
- Provider: `semantic_provider=hash|openai|gemini`

### Campi score (quando `semantic_query` presente)
- `semantic_score`
- `hybrid_score`
- `mismatch_penalty`

---

## 5) Hybrid semantic rerank
Motivazione:
- embedding puro produce falsi positivi su query specialistiche.

Strategia:
- score finale ibrido = semantica + segnali lessicali (title/skills) - penalità mismatch token critici.

Effetto:
- risultati più coerenti su query tipo:
  - `ml engineer llm`
  - `technical recruiter contract`
  - `frontend react typescript`.

---

## 6) Title normalization
Implementata con:
- `TITLE_RULES` + fallback intelligenti in `run_microsaas_pipeline.py`.
- Tassonomia e policy mapping:
  - `docs/title_taxonomy.md`

Risultato misurato:
- `other_like` ridotto a ~10.75% (su 2000 record).

Nota:
- tassonomia ancora estendibile post-MVP.

---

## 7) Salary extraction hardening
Fix principali:
- contesto positivo richiesto (`salary`, `compensation`, `base pay`, ecc.)
- esclusione contesto funding (`backed by`, `raised`, `series`, `valuation`, ecc.)
- sanity check su valori non plausibili.

Risultato:
- outlier `salary_max > 1,000,000` ridotti a 0 (su run MVP).

---

## 8) Embedding policy
Riferimento:
- `docs/embedding_policy.md`

Decisione operativa:
- default runtime: `hash`
- semantic query: `openai` preferito
- fallback: `hash`
- provider esterni non usati per filtri SQL.

---

## 9) Evaluation and benchmarks
Files:
- `docs/semantic_benchmark_hash_vs_openai.md`
- `docs/semantic_eval_top3.csv`
- `docs/semantic_eval_top3_prefilled.csv`
- `docs/title_normalization_eval.md`
- `docs/title_normalization_unmatched_top50.csv`
- `docs/skills_taxonomy_eval.md`
- `automation/microsaas/benchmark_semantic.py`
- `automation/microsaas/export_semantic_eval_csv.py`
- `automation/microsaas/eval_title_normalization.py`
- `automation/microsaas/eval_skills_taxonomy.py`
- `automation/microsaas/skills_aliases_v1.json`

Uso:
- confronto hash/openai su corpus comune
- validazione top-3 rilevanza per query.
- eval title normalization (coverage, role family distribution, top unmatched).
- eval skills taxonomy (unique skills, top skills, alias normalization).

---

## 10) Frontend MVP
Files:
- `src/jobintel/ui/indexed.html`
- `src/jobintel/ui/indexed.js`

Caratteristiche:
- search bar unica
- filtri essenziali
- cards leggibili (titolo, meta, salary se presente, skills)
- nessuna scelta tecnica esposta all’utente.

---

## 11) Runbook rapido
Pipeline:
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/run_microsaas.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run \
  data/jobintel_microsaas.sqlite
```

API:
```bash
uv run --active uvicorn jobintel.api:app --reload --port 8001
```

UI utente:
- `http://127.0.0.1:8001/ui-indexed`

---

## 12) Test and acceptance
Smoke E2E (pipeline + quality gates + API):
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/smoke_e2e_mvp.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run_smoke \
  data/jobintel_microsaas_smoke.sqlite
```

Unit test principale:
```bash
PYTHONPATH=. uv run --active pytest -q tests/test_microsaas_pipeline_rules.py
```

Unit/integration incrementale (lifecycle + pipeline_runs):
```bash
PYTHONPATH=. uv run --active pytest -q tests/test_microsaas_incremental_lifecycle.py
```

Go-live checklist:
- `docs/mvp_go_live_checklist.md`

MVP checklist:
- `docs/microsaas_mvp_checklist.md`

---

## 13) Known limitations (MVP)
- tassonomia ruoli ancora incompleta
- review umana non integrata in UI
- ranking semantico migliorabile iterativamente
- query cache embeddings non ancora introdotta.

---

## 14) Post-MVP directions
Riferimento:
- `docs/microsaas_post_mvp_steps.md`

Direzioni:
- tassonomia estesa
- confidence per campo
- human-in-the-loop
- metriche qualità continue
- ottimizzazione costi/query cache.

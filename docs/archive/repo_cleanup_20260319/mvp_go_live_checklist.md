# MVP Go-Live Checklist

Usa questa checklist per chiudere il rilascio MVP senza riaprire scope.

## 1) Freeze scope
- [ ] Nessuna nuova feature in coda MVP
- [ ] Solo bugfix/stabilità/integration
- [ ] Policy embedding confermata (`docs/embedding_policy.md`)

## 2) Smoke E2E (consigliato)
- [ ] Eseguito smoke script unico:
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/smoke_e2e_mvp.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run_smoke \
  data/jobintel_microsaas_smoke.sqlite
```

## 3) Data pipeline (2000 annunci)
- [ ] Eseguito run ufficiale:
```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/run_microsaas.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run \
  data/jobintel_microsaas.sqlite
```
- [ ] Output presenti:
  - `data/microsaas/run/raw_jobs.jsonl`
  - `data/microsaas/run/jobs_clean.jsonl`
  - `data/microsaas/run/jobs_indexed.jsonl`
  - `data/jobintel_microsaas.sqlite`
- [ ] KPI minimi verificati:
  - `other_like <= 12%`
  - `salary_outlier_gt1M = 0` (con regole correnti)

## 4) API readiness
- [ ] Avvio API:
```bash
uv run --active uvicorn jobintel.api:app --reload --port 8001
```
- [ ] Endpoint rispondono `200`:
  - [ ] `/v1/indexed/jobs?db_path=data/jobintel_microsaas.sqlite`
  - [ ] `/v1/indexed/filters/options?db_path=data/jobintel_microsaas.sqlite`
  - [ ] `/v1/indexed/jobs?db_path=data/jobintel_microsaas.sqlite&semantic_query=senior+data+engineer`
- [ ] `semantic_query` restituisce:
  - [ ] `semantic_score`
  - [ ] `hybrid_score`
  - [ ] `mismatch_penalty`

## 5) Frontend MVP integration
- [ ] Frontend usa `/v1/indexed/jobs`
- [ ] Frontend usa `/v1/indexed/filters/options`
- [ ] Filtri base funzionano (role/seniority/location/employment/skills)
- [ ] Ricerca semantica funzionante da UI

## 6) Qualità semantica
- [ ] CSV eval compilato (manuale o prefill + review):
  - `docs/semantic_eval_top3.csv`
  - `docs/semantic_eval_top3_prefilled.csv`
- [ ] Decisione policy finale validata con risultati (`hash` vs `openai`)

## 7) Sicurezza e config
- [ ] Nessuna API key committata
- [ ] Variabili ambiente impostate localmente (`OPENAI_API_KEY`, opzionale `GOOGLE_API_KEY`)
- [ ] `.gitignore` copre `data/` e `*.sqlite`

## 8) Tag/release MVP
- [ ] Branch pulita e commit finale
- [ ] Tag creato (es. `v0.1.0-mvp`)
- [ ] Note rilascio con:
  - dataset (2000 annunci)
  - endpoint supportati
  - policy embedding
  - limiti noti post-MVP

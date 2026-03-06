# Release Notes - v0.1.0-mvp

## Scope
MVP micro-SaaS per job intelligence su corpus Greenhouse EN (2000 annunci).

## Cosa include
- Pipeline batch end-to-end:
  - ingest -> clean -> normalize_title -> tag -> embed -> index
- Output:
  - `data/microsaas/run/raw_jobs.jsonl`
  - `data/microsaas/run/jobs_clean.jsonl`
  - `data/microsaas/run/jobs_indexed.jsonl`
  - `data/jobintel_microsaas.sqlite`
- API:
  - `GET /v1/indexed/jobs`
  - `GET /v1/indexed/filters/options`
- Semantic search:
  - provider `hash` + `openai` + `gemini`
  - rerank ibrido (`semantic_score`, `hybrid_score`, `mismatch_penalty`)

## Qualità raggiunta (MVP)
- `other_like` ridotto a ~21.5% su 2000 record
- outlier salary (`salary_max > 1,000,000`) ridotti a 0 con regole aggiornate
- benchmark semantic hash vs openai eseguito e valutazione top-3 disponibile

## Policy embedding
- default runtime: `hash`
- semantic query: `openai` preferito (fallback `hash`)
- riferimento: `docs/embedding_policy.md`

## Documentazione operativa
- `docs/microsaas_mvp_checklist.md`
- `docs/mvp_go_live_checklist.md`
- `docs/microsaas_post_mvp_steps.md`
- `docs/semantic_benchmark_hash_vs_openai.md`
- `docs/semantic_eval_top3.csv`
- `docs/semantic_eval_top3_prefilled.csv`

## Limiti noti (post-MVP)
- tassonomia ruoli ancora espandibile (target riduzione ulteriore di `other`)
- review umana non ancora integrata in UI
- ottimizzazione ranking semantico iterativa


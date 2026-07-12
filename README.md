# jobintel-next

Backend MVP end-to-end per trasformare annunci ATS grezzi in un sistema interrogabile e operativo:
- pipeline strutturata
- API HTTP
- Admin UI
- saved searches + alert runs + email alerts

## Value Proposition
`jobintel-next` riduce attrito tra “raccolta dati jobs” e “uso prodotto”:
- normalizza payload eterogenei ATS in un contratto interno stabile
- espone query/facets utili per ricerca e discovery
- abilita workflow operativi (saved search, run-all, delta nuovi match, history)

## Problema Che Risolve
I job post ATS sono rumorosi e source-specific. Senza pipeline:
- ingestione fragile
- filtri incoerenti
- alert non affidabili

Con `jobintel-next`:
- da raw payload a `IndexedJob` con segnali consistenti
- da query manuali a saved searches riusabili
- da controllo ad-hoc a workflow osservabile via API/Admin UI

## Feature Principali
- Adapter Greenhouse con boundary chiaro (`client` / `mapper` / `collector`)
- Pipeline modulare:
  - language gate
  - cleaning
  - extraction
  - title normalization/classification
  - indexed stage
- Storage SQLite v1 (con fallback JSONL)
- Retrieval layer con filtri, sort e query packs
- FastAPI:
  - jobs / packs / facets
  - saved searches CRUD
  - alert runs history + summary
- Admin UI server-rendered:
  - overview
  - saved searches (create/edit/run/delete)
  - alerts history + detail
- Email alerts SMTP opzionali

## Stack Tecnico
- Python 3.11
- FastAPI + Pydantic
- SQLite
- Jinja2 (server-rendered UI)
- pytest
- uv + Makefile
- Docker / docker compose (deploy minimale)

## Architettura (Sintesi)
```text
ATS adapters -> CanonicalRawJob -> language -> cleaning -> extraction
-> title classification -> IndexedJob -> retrieval/serving -> API/UI
-> saved searches -> alert runs -> email delivery
```

Riferimenti:
- `docs/architecture_v1.md`
- `docs/runbook_step32.md`

## Demo Quickstart (Portfolio)
```bash
cd joballert2
make setup
make demo
make demo-alerts
make demo-api
```

Apri:
- Admin UI: `http://127.0.0.1:8000/admin`
- API docs: `http://127.0.0.1:8000/docs`

Flow consigliato:
1. `/admin` overview
2. `/admin/saved-searches` (CRUD + run)
3. `/admin/alerts` (run-all + history)
4. `/admin/alerts/{run_id}` (new matches detail)
5. `GET /alerts/summary` per snapshot operativo

Demo pack ufficiale:
- `data/demo/jobs_indexed_demo.jsonl`
- `data/demo/jobs_indexed_demo.db`
- `data/demo/saved_searches_demo.db`
- `data/demo/alerts/runs/*.json|*.md`

Dettagli: `docs/demo_pack_step33.md`

## Deploy Quickstart (Docker)
Build:
```bash
make docker-build
```

Run:
```bash
make docker-run
```

Oppure compose:
```bash
cp .env.example .env
make docker-compose-up
```

Apri:
- `http://127.0.0.1:8000/admin`
- `http://127.0.0.1:8000/docs`

Dettagli deploy: `docs/deploy_step35.md`

## Admin UI Screenshots
Overview:

![Admin Overview](docs/screenshots/admin_overview.png)

Saved Searches:

![Admin Saved Searches](docs/screenshots/admin_saved_searches.png)

Alerts History:

![Admin Alerts History](docs/screenshots/admin_alerts_history.png)

Alert Detail:

![Admin Alert Detail](docs/screenshots/admin_alert_detail.png)

Screenshot naming guide: `docs/screenshots/README.md`

## Why This Project Is Interesting
- mostra un percorso realistico da ingestion a serving prodotto
- separa bene contratti di dominio e boundary ATS
- privilegia scelte pragmatiche e verificabili (rules + contracts + tests)
- include operatività reale (alert workflow completo) senza overengineering

## Stato Attuale (Beta Piccola)
- auth/session locale e boundary multi-user minimo
- workflow completo: inbox -> shortlist -> pipeline -> review/today
- saved searches con lifecycle (`active|disabled|archived`), coverage/portfolio/hygiene
- alert runs per-user + digest email opzionale + scheduling cron-friendly (`run-due`)
- deploy prod-like minimale con secret/session guardrails

## Limiti Noti
- auth locale (no OAuth/social, no reset password email)
- scheduler cron-friendly locale, non distribuito
- delivery SMTP semplice/sincrona (no retry automatico avanzato)
- niente semantic search / recommendation engine / AI ranking
- niente analytics storica avanzata o BI

## Roadmap Breve
1. stabilizzazione beta con feedback utenti reali e fix mirati
2. hardening operativo incrementale (osservabilità, operazioni, recovery)
3. capability avanzate dopo consolidamento baseline (semantic/ranking evoluto)

## Comandi Operativi Principali
```bash
make help
make build-index
make run-api
make run-alerts
make beta-smoke
make cleanup-alerts KEEP_LAST=20
```

## Documentazione
- Runbook operativo: `docs/runbook_step32.md`
- Demo pack: `docs/demo_pack_step33.md`
- Deploy minimale: `docs/deploy_step35.md`
- Deploy hardening prod-like: `docs/deploy_hardening_step54.md`
- Pilot feedback pass: `docs/pilot_feedback_step80.md`
- Beta readiness finale: `docs/beta_readiness_step81.md`

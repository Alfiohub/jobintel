# Beta Readiness v1 (Step 81)

## Cosa significa "beta-ready" per questo progetto
In questo contesto, beta-ready significa:
- prodotto usabile da pochi utenti reali (1–5) con workflow completo daily/weekly
- deploy prod-like minimo ripetibile (Docker/compose + env chiari)
- checklist operativa concreta per verificare setup, flussi, persistenza e isolamento
- limiti e rischi residui espliciti prima di una beta più ampia

Non significa ancora: feature enterprise, AI avanzata, orchestrazione distribuita.

## Hardening/polish finali applicati

### 1) Target `make beta-smoke`
Aggiunto target operativo per eseguire una suite smoke beta-oriented in un comando unico:

```bash
make beta-smoke
```

Copre test chiave su:
- auth/session
- account/preferences
- saved searches API/UI
- alert ops/digest
- admin UI flow principale
- pilot readiness
- deploy hardening
- scheduling + digest product layer

### 2) README allineato allo stato reale
Aggiornato `README.md` per ridurre mismatch tra codice e documentazione:
- stato attuale aggiornato (multi-user/auth/session, lifecycle, today/review, digest, scheduling)
- limiti noti reali (no OAuth/reset email, no scheduler distribuito, no semantic/AI avanzato)
- riferimenti rapidi alle doc operative finali (`deploy_hardening_step54`, `pilot_feedback_step80`, `beta_readiness_step81`)

## Checklist operativa finale (beta)

### A) Setup e accesso
1. `make setup`
2. crea/valida utente locale (`jobintel-next auth create-user` o bootstrap)
3. login `/login` riuscito
4. logout e session clear verificati

### B) Discovery e search portfolio
1. crea saved search (manuale o target-aligned)
2. edit/disable/enable/archive/restore verificati
3. `archived` esclusa da working portfolio (`run-due`, coverage, hygiene)
4. coverage/portfolio/hygiene visibili in `/admin/saved-searches`

### C) Alerts, digest, scheduling
1. `run-all` da UI/API riuscito
2. digest fallback su `default_alert_email` verificato
3. caso senza destinatario: run ok + messaggio skip chiaro
4. `alerts run-due` (CLI) esegue solo search dovute/attive

### D) Triage e pipeline
1. inbox triage (`new/seen/saved/dismissed`)
2. shortlist operativa con pipeline (`saved/applied/interview/rejected`)
3. details persistenti (`notes`, timeline, follow-up, contact/materials)
4. today/review/notifications coerenti con CTA cross-view

### E) Export e isolamento
1. export CSV shortlist disponibile
2. colonne principali presenti
3. isolamento per-user su export/dati UI/API

### F) Deploy prod-like e persistenza
1. avvio con `.env.production.example` (secret reale)
2. `JOBINTEL_REQUIRE_SESSION_SECRET=true` attivo
3. restart app/container senza perdita DB/runs
4. health endpoint raggiungibile

## Comandi beta consigliati

### Locale demo rapido
```bash
make setup
make demo
make demo-alerts
make demo-api APP_PORT=8010
```

### Smoke suite beta
```bash
make beta-smoke
```

### Deploy prod-like minimale
```bash
make docker-build
make run-prod-like PROD_ENV_FILE=.env.production.example APP_PORT=8000
# oppure
make deploy-local PROD_ENV_FILE=.env.production.example
```

## Entry point docs consigliati
- setup/run operativo: `README.md`
- deploy prod-like: `docs/deploy_hardening_step54.md`
- pilot pass e attriti fixati: `docs/pilot_feedback_step80.md`
- daily/weekly operating model: `docs/ops_polish_step79.md`

## Rischi residui prima della beta estesa
- auth locale non enterprise (no OAuth/social/reset email)
- scheduler/delivery non distribuiti
- no retry/backoff delivery avanzato
- no analytics storica avanzata
- no semantic search/recommendation

## Cosa NON è ancora incluso
- nuove feature AI
- semantic search o ranking ML avanzato
- billing
- scheduler distribuito + queue/retry system complesso
- notification center realtime/push

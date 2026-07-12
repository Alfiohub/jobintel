# Pilot Readiness / Real User Pass v1 (Step 55)

## Obiettivo
Portare il prodotto a uno stato più stabile e chiaro per un pilot reale con 1-3 utenti, senza introdurre nuova architettura grande.

## Miglioramenti applicati

### 1) Pilot flow pass su superfici principali
Verificato e rifinito il flusso:
- login
- onboarding first-run
- create saved search
- run alerts
- inbox triage
- account settings
- digest visibility

### 2) Messaggi/errori più chiari
- login invalido: messaggio esplicito
  - `Login failed: invalid email or password`
- login page: hint operativo su creazione utente locale via CLI
- dashboard: indicatori diagnostici diretti per ridurre ambiguità operative

### 3) Diagnostics/status surface in `/admin`
Aggiunto blocco **Diagnostics** con:
- current user
- default alert email configurata o no
- saved searches enabled count
- latest run status (`ok` / `error` / `not_run`)
- backend mode SQLite enabled/disabled
- alert runs directory attiva

Questo rende più semplice capire rapidamente "perché non vedo dati" o "su quale utente/path sto lavorando".

## Checklist pilot testing (reale)

1. Login utente A
- login riuscito
- dashboard mostra utente corretto in diagnostics

2. Login utente B
- crea secondo utente locale
- verifica isolamento saved searches/job state/alert runs

3. First-run onboarding
- dashboard checklist visibile
- CTA verso create saved search / alerts / inbox / account

4. Saved search workflow
- create/edit saved search
- run singola e run-all
- verifica current/new count

5. Due-run scheduling
- esegui `alerts run-due`
- verifica che processi solo search dovute
- verifica metadata run coerenti

6. Digest fallback email
- imposta `default_alert_email` in account
- run con digest senza `email_to` esplicita
- verifica fallback e metadata delivery

7. Deploy prod-like
- avvio con `.env.production.example` (secret reale)
- `/health`, `/admin`, `/docs` raggiungibili

8. Smoke dopo restart
- restart container/app
- login ancora valido
- DB e run history persistenti su volume

## Test aggiunti
Nuovo file:
- `tests/api/test_pilot_readiness_step55.py`

Coperture:
- smoke pilot end-to-end su UI flow principale
- diagnostics render + aggiornamento checklist
- messaggio login invalido chiaro

## Rischi residui
- auth locale semplice (no OAuth/reset password email)
- delivery SMTP sincrona senza retry automatico avanzato
- scheduler cron-friendly ma non distribuito
- no analytics operative avanzate (solo observability base)

## Cosa monitorare nei primi utenti reali
- attrito nel primo setup account/email
- frequenza errori login e misunderstanding delle credenziali
- chiarezza di due/not due sulle saved searches
- tasso di digest inviati vs skipped vs error
- tempi medi run e eventuali lock skip su run-due

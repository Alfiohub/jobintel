# Onboarding / First-Run UX v1 (Step 53)

## Obiettivo
Rendere il primo accesso più guidato, così un utente nuovo non trova una UI "vuota" ma un flusso operativo chiaro.

## Empty states migliorati

### `/admin`
- aggiunta sezione **Getting Started** con checklist first-run
- progress visibile (`done/total`)
- sezione **Next Steps** con CTA dirette:
  - create saved search
  - run alerts
  - review inbox
  - set alert email
- empty state dedicato quando non esistono ancora run recenti

### `/admin/saved-searches`
- quando non ci sono saved searches:
  - messaggio esplicito su cosa manca
  - CTA dirette verso:
    - creazione prima saved search
    - alerts
    - account/default alert email

### `/admin/inbox`
- empty state contestuale quando `total_count=0`:
  - nessuna saved search: invita a crearla
  - nessun alert run: invita a eseguire alerts
  - filtri troppo stretti: invita ad allargare filtri/stati

### `/admin/alerts`
- empty state più guidato quando non ci sono run:
  - spiega il passo successivo
  - CTA verso saved searches/account/alerts flow

## Checklist first-run su dashboard
Checklist minima (done/not done):
1. Create your first saved search
2. Set a default alert email in Account
3. Run alerts to generate your first run
4. Review your inbox and mark at least one job

Calcolo pragmatico done:
- saved search esiste
- `default_alert_email` valorizzata
- almeno un alert run presente
- almeno un job con stato persistito (`seen/saved/dismissed`)

## Workflow consigliato first-run
1. Login e apertura `/admin`.
2. Click `Create your first saved search`.
3. Vai in `Account` e imposta `default_alert_email`.
4. Vai in `Alerts` e lancia `Run all enabled searches`.
5. Apri `Inbox` e marca almeno un job (`Seen`/`Save`/`Dismiss`).
6. Torna su `/admin` e verifica checklist completata.

## Test aggiunti
Aggiornato:
- `tests/api/test_admin_ui_step30.py`

Coperture nuove:
- render checklist first-run e CTA principali
- render empty states su dashboard/saved-searches/inbox/alerts
- aggiornamento checklist dopo flow minimo con dati reali

## Limiti noti
- onboarding statico server-rendered (no tour JS)
- nessuna analytics onboarding avanzata
- nessuna automazione email/onboarding sequence

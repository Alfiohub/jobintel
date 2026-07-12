# Pilot Feedback Pass v1 (Step 80)

## Obiettivo
Fare un pass finale orientato a pilot reali (1–3 utenti), riducendo attriti operativi e piccoli punti confusi senza introdurre nuove feature sostanziali.

## Flussi verificati end-to-end
Pass pragmatico su questi flussi:
- login/logout
- account/profile/preferences
- saved search lifecycle (`create/edit/disable/archive/restore`)
- target-aligned creation (`/admin/saved-searches/new` helper)
- alerts (`run-all`), due-run foundation, digest behavior
- inbox triage
- shortlist + pipeline + notes/details
- today/review/notifications navigation
- shortlist export CSV

## Bugfix / polish applicati

### 1) Saved Search lifecycle actions: meno attrito di navigazione
Problema:
- dopo azioni lifecycle da lista (`Enable`, `Disable`, `Archive`, `Restore`, `Run`, `Delete`) l’utente tornava sempre su `/admin/saved-searches` perdendo il filtro lifecycle corrente.

Fix:
- redirect ora preserva il contesto del filtro (`active`, `disabled`, `archived`) usando query corrente o `referer`.

Effetto:
- cleanup/maintenance più lineare quando si lavora su una vista filtrata.

### 2) Messaggi lifecycle più chiari
Migliorati i messaggi utente:
- archive: chiarisce che la search è esclusa da run-due e viste strategiche
- restore: chiarisce che torna `disabled` e va eventualmente riabilitata

### 3) Alerts run-all con email attiva ma senza destinatario
Problema:
- il run veniva eseguito ma il feedback mostrava solo errore tecnico su `email_to`.

Fix:
- messaggio ora esplicita che:
  - il run è completato
  - il digest è stato skippato
  - serve impostare `default_alert_email` in Account o passare `email_to`

Effetto:
- ridotta confusione tra “run fallito” e “delivery skippata”.

## File toccati
- `src/jobintel_next/app/admin_ui/router.py`
- `tests/api/test_admin_ui_step30.py`

## Checklist pilot testing (reale)
1. **Utente A / Utente B**
- login separati
- isolamento dati su inbox/shortlist/saved searches/alerts/export

2. **Auth/session**
- login valido/non valido
- logout + clear session

3. **Saved search lifecycle**
- create/edit
- disable/enable
- archive/restore
- verifica esclusione `archived` da run-due/coverage/portfolio/hygiene

4. **Target-aligned workflow**
- profilo target in account
- creazione search con helper/prefill
- verifica coverage/gap visibility

5. **Alerts / Digest**
- run-all standard
- run-all con digest e fallback `default_alert_email`
- caso senza destinatario: run ok + messaggio skip chiaro

6. **Shortlist pipeline**
- `saved -> applied -> interview -> rejected`
- details/notes/follow-up persistenti

7. **Today / Review / Notifications**
- CTA cross-view coerenti
- empty states leggibili
- distinzione daily vs weekly chiara

8. **Export correctness**
- CSV shortlist scaricabile
- colonne principali presenti
- isolamento per-user

9. **Deploy prod-like + restart persistence**
- avvio con env prod-like (`JOBINTEL_REQUIRE_SESSION_SECRET=true`)
- restart app/container
- persistenza DB/run artifacts verificata

## Test aggiunti/aggiornati
Aggiornato:
- `tests/api/test_admin_ui_step30.py`

Nuove coperture:
- redirect lifecycle che preserva filtro corrente
- messaggio run-all + digest skip senza destinatario
- testo aggiornato restore lifecycle

## Attriti residui
- feedback operativi ancora query-string based (no flash stack strutturato)
- UX form admin volutamente minimale, non guidata da wizard
- segnali review/notifications restano rule-based e statici

## Rischi residui prima della beta
- delivery SMTP sincrona (no retry automatico avanzato)
- scheduler cron-safe locale ma non distribuito
- auth locale non enterprise (no OAuth/reset email)
- observability operativa buona ma non ancora time-series/analytics avanzata

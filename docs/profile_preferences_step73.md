# Profile / Target Preferences v1 (Step 73)

## Obiettivo
Introdurre un profilo target per-user minimale, persistente e utile al workflow quotidiano, senza recommendation engine o matching AI.

## Campi supportati
Estensione delle user preferences (tabella `users`):
- `target_titles` (testo comma-separated)
- `target_role_families` (testo comma-separated)
- `preferred_location_types` (testo comma-separated: `remote`, `hybrid`, `onsite`)
- `salary_target_note`
- `keywords_note`

Modello scelto:
- estensione pragmatica della tabella utente esistente (`saved_searches.db`)

## UI aggiornata
Pagina:
- `GET /admin/account`

Nuova sezione:
- **Target Search Profile**
  - target titles
  - target role families
  - preferred location types
  - salary target note
  - keywords note

Update:
- `POST /admin/account` salva anche i campi profilo.

## Integrazione informativa (high ROI, rule-based)
### `/admin` (dashboard)
- blocco **Target Search Profile** con valori correnti
- insight semplice di allineamento shortlist:
  - role-family alignment
  - location alignment

### `/admin/today`
- header informativo con target profile corrente (titles / role families / locations)

### `/admin/shortlist`
- nota informativa con target profile corrente per contestualizzare triage/pipeline

## Come aiuta il workflow
1. Rende esplicito il target dell’utente dentro il prodotto.
2. Riduce ambiguità quando si revisionano shortlist e saved searches.
3. Fornisce un riferimento stabile per tuning manuale delle ricerche.

## Test aggiornati
Service:
- `tests/product/test_account_preferences_service_step45.py`
  - persistenza campi profilo
  - isolamento per-user

UI:
- `tests/api/test_account_preferences_step45.py`
  - render/edit sezione Target Search Profile
- `tests/api/test_admin_ui_step30.py`
  - presenza blocco/profilo su overview/today/shortlist

## Limiti noti
- nessun CV parsing
- nessun recommendation engine
- nessun matching semantico avanzato
- nessuna generazione profilo AI

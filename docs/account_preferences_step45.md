# Account / Preferences v1 (Step 45)

## Obiettivo
Aggiungere un livello account/settings minimale ma reale sopra la foundation multi-user già esistente.

## Campi supportati
Per ogni utente sono ora disponibili:
- `email`
- `default_alert_email` (opzionale)
- `include_dismissed_default` (bool)

## Storage / model
Riusata tabella `users` nel DB auth (`saved_searches.db`) con estensione schema:
- `default_alert_email` (`TEXT`, nullable)
- `include_dismissed_default` (`INTEGER`, default `1`)

Servizi aggiunti in `src/jobintel_next/product/auth/service.py`:
- `get_user_settings(...)`
- `update_user_settings(...)`

## UI aggiornata
Nuove route admin:
- `GET /admin/account`
- `POST /admin/account`

Nuova template:
- `src/jobintel_next/app/admin_ui/templates/account.html`

Navbar aggiornata:
- link `Account` disponibile su tutte le pagine admin.

## Integrazione workflow
- Le preferenze sono per-user (bound alla sessione utente).
- `default_alert_email` viene usata come fallback in `/admin/alerts/run-all` se `send_email=true` e il campo email nel form è vuoto.
- `include_dismissed_default` viene usata come default nella inbox quando `include_dismissed` non è esplicitamente passato in querystring.

## Test aggiunti
API/UI:
- `tests/api/test_account_preferences_step45.py`
  - render pagina account
  - update settings
  - isolamento preferences tra utenti

Service/storage:
- `tests/product/test_account_preferences_service_step45.py`
  - persistenza settings
  - isolamento per-user

## Limiti noti
- Nessun password reset
- Nessun OAuth/social login
- Nessun team/org settings
- Nessuna policy avanzata di scheduling preferences

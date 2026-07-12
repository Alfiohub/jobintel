# Password / Session Polish v1 (Step 52)

## Obiettivo
Rendere più credibile e usabile la auth/session locale senza introdurre OAuth o auth enterprise.

## Change password flow
Aggiunto cambio password locale per utente corrente.

Service layer:
- `change_local_password(...)` in `src/jobintel_next/product/auth/service.py`

Validazioni:
- `current_password` obbligatoria
- `new_password` obbligatoria
- lunghezza minima password nuova: 8
- errore chiaro se password attuale errata
- errore chiaro se conferma non coincide (UI route)

UI admin:
- nuova sezione `Change Password` su `/admin/account`
- endpoint:
  - `POST /admin/account/password`

Campi:
- current password
- new password
- confirm new password

## Session behavior (polish)
Session middleware ora usa config esplicita:
- `JOBINTEL_SESSION_SECRET`
- `JOBINTEL_SESSION_MAX_AGE` (default `43200`, 12h)
- `JOBINTEL_SESSION_COOKIE_NAME` (default `jobintel_session`)
- `JOBINTEL_SESSION_HTTPS_ONLY` (`true|false`, default `false`)
- `JOBINTEL_SESSION_SAME_SITE` (`lax|strict|none`, default `lax`)

Logout hardening:
- `POST /logout` ora:
  - pulisce session data
  - cancella cookie sessione corrente
  - cancella anche cookie legacy `session` per compatibilità

## Bootstrap / create user flow
Bootstrap locale resta idempotente via app startup (utente admin di default), ma ora è disponibile anche comando esplicito:

```bash
uv run jobintel-next auth create-user \
  --saved-db data/jobs/saved_searches.db \
  --email admin@example.com \
  --password "admin123" \
  --user-id local-user
```

Opzioni:
- `--inactive` per creare utente non attivo

## Moduli aggiornati
- `src/jobintel_next/product/auth/service.py`
- `src/jobintel_next/product/auth/__init__.py`
- `src/jobintel_next/app/api/dependencies.py`
- `src/jobintel_next/app/api/app.py`
- `src/jobintel_next/app/admin_ui/router.py`
- `src/jobintel_next/app/admin_ui/templates/account.html`
- `src/jobintel_next/cli.py`

## Test aggiunti/aggiornati
Aggiornati:
- `tests/api/test_auth_session_step43.py`
  - change password valido
  - errore su current password errata
  - login con nuova password
- `tests/api/test_account_preferences_step45.py`
  - render sezione change password
- `tests/product/test_account_preferences_service_step45.py`
  - change password service + verifica login

Nuovo:
- `tests/product/test_auth_cli_step52.py`
  - create-user command flow

## Limiti noti
- nessun password reset via email
- nessun OAuth/social login
- nessun invite flow/team management
- no ACL/ruoli avanzati in questo step

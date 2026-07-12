# Auth / Session v1 (Step 43)

## Obiettivo
Passare da boundary utente solo tecnico (env/header) a una UX locale reale con login/sessione per Admin UI, mantenendo fallback dev per API.

## Cosa è stato implementato

### 1) Auth locale minimale
Nuovo modulo:
- `src/jobintel_next/product/auth/service.py`
- `src/jobintel_next/product/auth/__init__.py`

Funzioni principali:
- `ensure_auth_schema(...)`
- `create_local_user(...)`
- `authenticate_local_user(...)`
- `bootstrap_local_user(...)`

Storage utente (riuso `saved_searches.db`):
- tabella `users` con:
  - `user_id`
  - `email`
  - `password_hash`
  - `created_at`
  - `is_active`

Password:
- hash PBKDF2 SHA-256 (no plain text)

### 2) Session cookie
In API app:
- `SessionMiddleware` aggiunto in `src/jobintel_next/app/api/app.py`
- secret configurabile via env `JOBINTEL_SESSION_SECRET`

Session data usata:
- `user_id`
- `user_email`

### 3) Login / Logout routes
Nuove route Admin UI:
- `GET /login`
- `POST /login`
- `POST /logout`

Template nuovo:
- `src/jobintel_next/app/admin_ui/templates/login.html`

Behavior:
- login valido: salva utente in sessione e redirect a `next` (default `/admin`)
- login invalido: redirect su `/login` con errore
- logout: clear session e redirect su `/login`

### 4) Protezione admin minimale
Le route `/admin*` sono protette:
- senza session cookie: redirect a `/login?next=...`
- con sessione valida: accesso consentito

Path principale UI ora è session-based.

### 5) Current user resolution
`get_current_user(...)` (`dependencies.py`) ora risolve in ordine:
1. sessione (`request.scope["session"]`)
2. header override tecnico/dev:
   - `X-JobIntel-User-Id`
   - `X-JobIntel-User-Email`
3. default user da env/app state

## Bootstrap utente locale
Configurazione (env):
- `JOBINTEL_BOOTSTRAP_EMAIL` (default: `admin@example.com`)
- `JOBINTEL_BOOTSTRAP_PASSWORD` (default: `admin123`)
- `JOBINTEL_DEFAULT_USER_ID`
- `JOBINTEL_DEFAULT_USER_EMAIL`

Alla creazione app viene bootstrapato un utente locale idempotente.

## Cosa è protetto
- Admin UI (`/admin`, inbox, saved searches, alerts, detail pages)
- Workflow UI create/edit/run/delete ora usa utente di sessione

## Cosa resta minimale
- Nessun signup pubblico
- Nessun reset password
- Nessun OAuth/social login
- Nessun ruolo/permesso avanzato

## Test aggiunti/aggiornati
Nuovo file:
- `tests/api/test_auth_session_step43.py`

Coperture:
- login valido
- login invalido
- admin protetto senza sessione
- logout
- isolamento dati tra utenti via sessione

Regression verdi su flussi UI/smoke:
- `tests/api/test_admin_ui_step30.py`
- `tests/api/test_smoke_e2e_step37.py`

## Limiti noti
- Auth pensata per local/demo e primo uso prodotto, non hardening enterprise
- Session management semplice (no CSRF hardening dedicato, no policy avanzate)
- Alert run artifacts filesystem restano globali

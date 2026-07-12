# Admin UI Step 30

## Obiettivo
Aggiungere una UI admin locale, minimale e server-rendered, per usare saved searches e alert runs senza dipendere da sola CLI/cURL.

## Modulo
- `src/jobintel_next/app/admin_ui/router.py`
- templates:
  - `src/jobintel_next/app/admin_ui/templates/base.html`
  - `index.html`
  - `saved_searches.html`
  - `saved_search_new.html`
  - `alerts.html`
  - `alert_detail.html`

Integrazione app:
- `create_app(...)` include anche il router admin.

## Pagine disponibili
- `/admin`
  - overview generale
  - conteggio saved searches
  - summary alert
  - recent runs
- `/admin/saved-searches`
  - lista saved searches
  - stato enabled/disabled
  - azioni enable/disable/run
- `/admin/saved-searches/new`
  - form creazione saved search (`filters` o `pack`)
- `/admin/alerts`
  - summary alert
  - lista run recenti
  - azione run-all
- `/admin/alerts/{run_id}`
  - dettaglio completo run

## Azioni supportate
- creare saved search via form
- enable/disable saved search
- run singolo saved search
- run-all saved searches abilitate
- (opzionale) run-all con email da form (`send_email` + `email_to`)

## Come avviare
API + Admin UI sulla stessa app FastAPI:

```bash
uv run uvicorn jobintel_next.app.api.app:app --reload
```

Poi aprire:
- `http://127.0.0.1:8000/admin`

## Limiti noti
- nessuna auth/login
- nessun multi-user
- nessuna UI avanzata/SPA
- styling minimale orientato all’operatività
- nessuna edit avanzata delle saved searches in questa fase

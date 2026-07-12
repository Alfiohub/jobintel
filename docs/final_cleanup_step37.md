# Final Cleanup / Smoke Test / Polish (Step 37)

## Obiettivo
Finalizzare il progetto in forma stabile e presentabile senza introdurre nuove feature prodotto.

## Smoke test e2e aggiunto
Nuovo test:
- `tests/api/test_smoke_e2e_step37.py`

Copertura:
- startup app
- `GET /health`
- render `GET /admin`
- create saved search (`POST /saved-searches`)
- run-all alerts (`POST /alerts/run-all`)
- list alert runs (`GET /alerts/runs`)
- alert run detail (`GET /alerts/runs/{run_id}`)

## Bugfix minimi fatti
1. Redirect admin UI con query params ora codificati in modo consistente:
   - fix encoding messaggi `message/error` (spazi, caratteri speciali)
   - applicato su create/edit/delete/enable/disable/run e run-all
2. Migliorata operatività `make run-api` / `make demo-api`:
   - supporto porta/host configurabili via `APP_PORT` / `APP_HOST`
   - utile quando `:8000` è già occupata

## Polish UI ad alto ROI
- navbar admin: aggiunto link rapido a `/docs`
- pagina alerts:
  - aggiunto riepilogo `Recent OK/Error runs`
  - messaggio esplicito quando non ci sono run

## Documentazione allineata
Aggiornata coerenza comandi/path su:
- `README.md`
- `docs/runbook_step32.md`
- `docs/demo_pack_step33.md`
- `docs/deploy_step35.md`

Allineamenti principali:
- comandi `make` realmente esistenti
- flow demo coerente con target `demo-*`
- indicazione chiara porta alternativa (`APP_PORT=8010`) per startup locale

## Limiti residui (voluti)
- nessuna auth/multi-user
- nessun scheduler distribuito
- nessuna semantic search/ranking avanzato
- deploy ancora volutamente minimale (single service)

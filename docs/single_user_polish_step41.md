# Single-user Polish v1 (Step 41)

## Obiettivo
Migliorare la UX quotidiana del prodotto single-user già esistente, senza aggiungere nuove capability backend strutturali.

## Superfici migliorate
- `GET /admin/inbox`
- `GET /admin/saved-searches/{search_id}`
- `GET /admin/alerts/{run_id}`

## Cambiamenti UX fatti

### 1) Badge e segnali visivi
Aggiunti badge chiari per:
- `job_state`: `new`, `seen`, `saved`, `dismissed`
- location: `remote`, `hybrid`, `onsite`
- salary: `salary` / `no salary`
- contesto ruolo: `role_family`

I badge sono implementati con CSS minimale in `base.html` e riusati su tutte le pagine chiave.

### 2) Contatori più visibili
Introdotte card KPI (`kpi-grid`) con valori principali:
- inbox: filtered/new/seen/saved/dismissed
- alert detail: total new matches, processed ok/error, timestamp
- saved search detail: current_count, new_count, enabled, last_run

### 3) Azioni rapide più leggibili
Le CTA `Seen / Save / Dismiss / Reset` sono mantenute ma rese più leggibili e coerenti in tabella con layout uniforme.

### 4) Navigazione più naturale
Aggiunti link rapidi tra superfici operative:
- `Inbox`
- `Saved Searches`
- `Alerts`
- `API Docs`

In alert detail e saved search detail sono presenti shortcut verso inbox/lista search/alerts.

### 5) Saved search mode più chiaro
Nella pagina `saved-search detail`:
- switch rapido `Current results` vs `New matches only`
- metadata e stato enabled più evidenti
- `current_count` e `new_count` messi in primo piano

## Workflow quotidiano consigliato
1. Parti da `/admin/inbox?state=new` per il triage.
2. Usa `Save` per shortlist, `Dismiss` per pulizia, `Seen` per avanzamento.
3. Vai su `/admin/saved-searches/{search_id}` e passa tra `Current`/`New` per lavorare search-by-search.
4. Controlla `/admin/alerts/{run_id}` per validare nuovi match giornalieri e rifinire stato.

## Test aggiornati
File principale aggiornato:
- `tests/api/test_admin_ui_step30.py`

Coperture aggiunte:
- presenza badge/state nelle pagine toccate
- presenza contatori/azioni principali
- presenza link di navigazione chiave

## Limiti residui
- single-user only (nessuna auth)
- nessun ranking/semantic search
- CSS volutamente minimale (no design system)

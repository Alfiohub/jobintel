# Job Search Dashboard / Funnel Overview v1 (Step 62)

## Obiettivo
Rendere la dashboard admin più utile per lo stato complessivo della ricerca lavoro, aggregando triage, shortlist, pipeline e alert in una vista operativa unica.

## KPI introdotti
In `/admin` è stato aggiunto il blocco **Job Search Funnel** con:
- `new`
- `saved`
- `applied`
- `interview`
- `rejected`

Metriche di attenzione immediate:
- `saved without notes`
- `interview without date`

## Sezioni nuove ad alto ROI
### 1) Saved Searches Needing Attention
Elenco sintetico delle saved search con segnali utili:
- `due now`
- quality flags (es. `high dismiss rate`, `no recent new matches`)
- latest new count

### 2) Top Shortlist Items
Top job salvati ordinati per rank con:
- titolo
- pipeline state
- reason sintetica (`Why ranked`)

### 3) Pipeline Needing Attention
Lista prioritaria dei job con azioni mancanti, es:
- `saved without notes`
- `interview without date`

## CTA / Navigazione
La dashboard include link diretti verso:
- Inbox
- Shortlist
- Saved Searches
- Alerts

Questo rende il flusso giornaliero più lineare senza introdurre UI complessa.

## Come leggere la dashboard
1. Controlla il funnel per capire dove si accumula il lavoro.
2. Apri `Pipeline Needing Attention` per risolvere gap operativi rapidi.
3. Guarda `Saved Searches Needing Attention` per mantenere qualità delle query.
4. Usa `Top Shortlist Items` come priorità del giorno.

## Test aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render KPI funnel
  - render sezioni principali
  - presenza CTA/link principali
  - comportamento sensato con pochi dati
- `tests/product/test_job_state_step38.py`
  - helper conteggi/list URL per stato (supporto KPI funnel)

## Limiti noti
- niente chart/time-series avanzate
- niente analytics BI
- niente kanban/reminder automatici
- nessun recommendation engine/semantic layer in questo step

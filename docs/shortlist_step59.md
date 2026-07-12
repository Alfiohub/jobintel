# Saved Jobs / Shortlist Workspace v1 (Step 59)

## Obiettivo
Trasformare lo stato `saved` in una superficie di lavoro dedicata, così la shortlist non resta dispersa tra inbox, alerts e saved searches.

## Nuova pagina
- `GET /admin/shortlist`

Mostra i job con `job_state=saved` dell’utente corrente, con:
- titolo
- company (`company_name` / fallback `source_org`)
- location badge (`remote/hybrid/onsite`)
- salary badge
- role_family / normalized_title
- rank score
- URL
- azioni rapide:
  - `Seen`
  - `Dismiss`
  - `Reset`

## Sort disponibili
- `rank` (default)
- `newest`
- `salary` (ordina per `salary_max` / `salary_min`)

## Filtri disponibili
- `role_family`
- `only_remote`
- `only_salary`
- `exclude_other`

## Navigazione aggiornata
- navbar: link `Shortlist`
- CTA da inbox: `Open shortlist workspace`
- CTA da saved-search detail: `Open shortlist`

## Implementazione pragmatica
La shortlist riusa logica esistente:
- retrieval jobs list
- stati utente (`job_state`)
- ranking leggero (`rank_jobs`)

Nessuna duplicazione pesante di business logic.

## Workflow consigliato
1. In inbox/saved-search marca i job utili come `saved`.
2. Lavora la shortlist in `/admin/shortlist` con sort `rank` o `newest`.
3. Usa `Seen` per avanzamento, `Dismiss` per pulizia, `Reset` per ripristino.
4. Tieni la shortlist come workspace giornaliero di prioritizzazione.

## Test aggiunti/aggiornati
Aggiornato:
- `tests/api/test_admin_ui_step30.py`

Copertura:
- render pagina shortlist
- solo job `saved` visibili
- sort/filter principali
- azioni rapide dalla shortlist
- presenza link `Shortlist` nella navigazione

## Limiti noti
- no note/applications tracking
- no kanban pipeline
- no reminder/calendar
- no semantic search/recommendation in questo step

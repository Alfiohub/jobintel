# Daily Review / Weekly Review v1 (Step 68)

## Obiettivo
Introdurre una review surface pratica per mantenere la ricerca lavoro pulita nel tempo, evidenziando candidature ferme e saved searches da revisionare.

## Nuova pagina
- `GET /admin/review`

## Sezioni introdotte
1. `Saved Jobs Stale`
- job in pipeline `saved` che richiedono revisione
- segnali usati: job salvato da tempo senza avanzamento, oppure senza note/follow-up
- CTA: shortlist filtrata (`/admin/shortlist?pipeline_state=saved`)

2. `Applied Jobs Without Recent Update`
- job `applied` senza aggiornamenti/follow-up utili
- segnali usati: `applied_at` mancante o candidatura vecchia senza follow-up
- CTA: shortlist filtrata (`/admin/shortlist?pipeline_state=applied`)

3. `Interview Items Missing Notes/Date`
- job `interview` con contesto incompleto
- segnali usati: `interview_at` mancante e/o note mancanti
- CTA: shortlist filtrata (`/admin/shortlist?pipeline_state=interview`)

4. `Saved Searches with No Recent New Matches`
- saved searches con segnale `no recent new matches` dagli insights
- CTA: dettaglio saved search

5. `High Dismiss-Rate Searches Needing Cleanup`
- saved searches con segnale `high dismiss rate` dagli insights
- CTA: dettaglio saved search

## Logica review usata
Deterministica e trasparente, basata solo su:
- `application_state`
- details/timeline (`notes`, `applied_at`, `interview_at`, `follow_up_at`)
- date presenti nei job (`published_at`)
- quality flags da `saved_search_insights`

Nessun scoring opaco o AI.

## Navigazione
- nuovo link `Review` in navbar
- CTA aggiunte da:
  - `/admin` (`Open Review view`)
  - `/admin/today` (`Open review`)

## Workflow consigliato
1. Apri `/admin/review` a inizio giornata o review settimanale.
2. Risolvi prima `Interview Items Missing Notes/Date` e `Applied Jobs Without Recent Update`.
3. Pulisci `Saved Jobs Stale` spostando lo stato pipeline o aggiungendo follow-up.
4. Tuning periodico delle search dalle sezioni di quality (`no recent new`, `high dismiss rate`).

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render pagina review + empty states
  - presenza blocchi principali e CTA
  - caso reale `interview` con gap (note/data mancanti)

## Limiti noti
- nessun calendar sync/reminder automatico
- nessuna analytics storica avanzata
- nessun coaching/recommendation engine

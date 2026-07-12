# Follow-up / Reminder Lite v1 (Step 63)

## Obiettivo
Aggiungere un layer minimale di follow-up sulle candidature per non perdere azioni successive nel workflow quotidiano.

## Campi introdotti
Nel layer `application_details` (per-user, `user_id + job_url`):
- `follow_up_at` (opzionale)
- `follow_up_note` (opzionale)

Questi campi si aggiungono a `notes`, `applied_at`, `interview_at` senza rompere il modello esistente.

## Storage / integrazione
File principale:
- `src/jobintel_next/product/application_tracking/service.py`

Aggiornamenti:
- schema `application_details` esteso con migration pragmatica (`ALTER TABLE` se colonne mancanti)
- update/read many-details includono i nuovi campi

## Shortlist aggiornata
Pagina:
- `GET /admin/shortlist`

Novità:
- visualizzazione follow-up in colonna `Notes / Timeline`
- stato follow-up:
  - `overdue`
  - `due soon`
  - `scheduled`
- update/clear follow-up tramite form dettagli esistente (`Save details` / `Clear details`)

Filtri nuovi:
- `only_follow_up_set=true`
- `only_follow_up_due=true`

## Dashboard aggiornata (`/admin`)
Nuova sezione:
- **Needs Follow-up**

Mostra job con follow-up scaduto o imminente, con:
- titolo
- follow-up date
- status (`overdue` / `due soon`)
- nota follow-up

Inoltre il summary attenzione ora include:
- `follow-up due/overdue=<count>`

## Due / Overdue logic
- `overdue`: `follow_up_at <= now`
- `due soon`: `follow_up_at` entro 48h
- `scheduled`: oltre 48h
- vuoto: nessun follow-up impostato

## Workflow consigliato
1. In shortlist, imposta `follow_up_at` e `follow_up_note` sui job attivi.
2. Usa filtro `only_follow_up_due` per il lavoro giornaliero.
3. Apri `/admin` e gestisci la sezione `Needs Follow-up` come lista prioritaria.

## Test aggiornati
- `tests/product/test_application_tracking_step60.py`
  - persistenza nuovi campi follow-up
  - isolamento per-user
- `tests/api/test_admin_ui_step30.py`
  - render shortlist follow-up
  - filtri `only_follow_up_set` / `only_follow_up_due`
  - sezione dashboard `Needs Follow-up`

## Limiti noti
- nessun calendar sync
- nessun reminder email automatico
- nessun push/in-app notification center
- niente kanban avanzato

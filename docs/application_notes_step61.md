# Application Notes / Timeline Lite v1 (Step 61)

## Obiettivo
Aggiungere un contesto persistente minimale alle candidature in pipeline, così la shortlist non contiene solo stato ma anche memoria operativa utile.

## Campi supportati
Per ogni coppia `(user_id, job_url)`:
- `notes` (testo libero breve)
- `applied_at` (opzionale)
- `interview_at` (opzionale)

I dati sono per-user e isolati tra account.

## Storage / modello
Modulo:
- `src/jobintel_next/product/application_tracking/service.py`

Nuova tabella SQLite:
- `application_details`
  - `user_id`
  - `job_url`
  - `notes`
  - `applied_at`
  - `interview_at`
  - `updated_at`
  - PK composta `(user_id, job_url)`

Nota pragmatica:
- la pipeline resta separata (`application_state`),
- i dettagli sono un layer leggero aggiuntivo e compatibile.

## Operazioni supportate
Service layer:
- `update_application_details(...)`
- `get_application_details(...)`
- `get_many_application_details(...)`
- `clear_application_details(...)`

Pipeline integration:
- quando lo stato passa a `applied` o `interview`, viene valorizzata automaticamente la milestone timestamp se assente.

## UI aggiornata
Pagina:
- `GET /admin/shortlist`

Novità per riga job:
- colonna `Notes / Timeline`
- visualizzazione note e date (quando presenti)
- form minimale inline per:
  - save/update `notes`, `applied_at`, `interview_at`
  - clear dettagli

Nuove action routes:
- `POST /admin/shortlist/details`
- `POST /admin/shortlist/details/clear`

## Workflow consigliato
1. Salva job interessanti in shortlist.
2. Avanza stato pipeline (`Applied`, `Interview`, `Rejected`).
3. Aggiungi note operative rapide (es. recruiter contact, follow-up).
4. Compila `applied_at` / `interview_at` per mantenere timeline minima.

## Test aggiunti
Service:
- `tests/product/test_application_tracking_step60.py`
  - persistenza dettagli
  - clear dettagli
  - isolamento per-user

UI:
- `tests/api/test_admin_ui_step30.py`
  - render colonna notes/timeline
  - update dettagli da shortlist
  - clear dettagli da shortlist

## Limiti noti
- niente rich text
- niente reminder/calendar sync
- niente ATS/email sync
- niente kanban avanzato o CRM complesso

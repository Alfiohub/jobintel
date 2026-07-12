# Application Materials / Submission Memory v1 (Step 71)

## Obiettivo
Aggiungere una memoria pratica dei materiali e della submission usata per ogni candidatura, senza introdurre upload file o document management.

## Campi supportati
Estensione di `application_details` (per-user su `user_id + job_url`):
- `resume_label`
- `cover_letter_label`
- `submission_note`

Questi si aggiungono ai dettagli già presenti:
- `notes`, `applied_at`, `interview_at`, `follow_up_at`, `follow_up_note`
- `application_channel`, `contact_name`, `contact_email`
- `compensation_note`, `external_application_url`

## Storage / service
File:
- `src/jobintel_next/product/application_tracking/service.py`

Aggiornamenti:
- migration pragmatica con `ALTER TABLE` se colonne mancanti
- `get_application_details(...)` / `get_many_application_details(...)` includono i nuovi campi
- `update_application_details(...)` salva i nuovi campi
- `clear_application_details(...)` resta coerente (reset completo tramite delete record)

## Shortlist UI aggiornata
Pagina:
- `GET /admin/shortlist`

Novità:
- nella colonna `Notes / Timeline` mostra:
  - `resume: ...`
  - `cover letter: ...`
  - `submission_note` (testo breve)
- form `Save details` esteso con:
  - `resume_label`
  - `cover_letter_label`
  - `submission_note`

Route già usate:
- `POST /admin/shortlist/details`
- `POST /admin/shortlist/details/clear`

## Review signal leggero
In `/admin/review` aggiunti segnali utili in `Applied Jobs Without Recent Update`:
- `applied without resume label`
- `applied without submission note`

## Export shortlist CSV
`GET /admin/exports/shortlist.csv` ora include anche:
- `resume_label`
- `cover_letter_label`
- `submission_note`

## Workflow consigliato
1. Quando passi un job a `applied`, compila almeno `resume_label`.
2. Se hai usato cover letter, salva `cover_letter_label`.
3. Registra in `submission_note` dettagli utili (es. custom answers / form specifico).
4. Usa export CSV per audit rapido delle submission inviate.

## Test aggiornati
Service:
- `tests/product/test_application_tracking_step60.py`
  - persistenza/clear nuovi campi
  - isolamento per-user

UI + export:
- `tests/api/test_admin_ui_step30.py`
  - render nuovi campi in shortlist
  - update/clear nuovi campi via form
  - export CSV con nuove colonne/campi

## Limiti noti
- nessun upload/storage allegati
- nessun CV repository centralizzato
- nessun sync ATS/email
- nessuna generazione documenti AI in questo step

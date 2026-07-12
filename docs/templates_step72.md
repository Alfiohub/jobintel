# Templates / Reusable Application Assets v1 (Step 72)

## Obiettivo
Trasformare `resume_label` e `cover_letter_label` da testo libero a una base riusabile per-user, senza upload file o template engine complesso.

## Modello templates
Nuova tabella per-user (`application_templates`) nel DB applicazioni:
- `template_id`
- `user_id`
- `kind` (`resume` | `cover_letter`)
- `label`
- `description`
- `is_active`
- `created_at`
- `updated_at`

File:
- `src/jobintel_next/product/application_tracking/service.py`

## Operazioni supportate
- `create_application_template(...)`
- `list_application_templates(...)`
- `set_application_template_active(...)`
- `delete_application_template(...)`

Tutte le operazioni rispettano il boundary utente.

## Superfici aggiornate

### 1) Admin Templates
Nuova pagina:
- `GET /admin/templates`

Azioni:
- create template (kind + label + description + active)
- enable/disable template
- delete template

Navbar:
- nuovo link `Templates`

### 2) Shortlist details (guided selection)
In `GET /admin/shortlist` il form dettagli include:
- select `resume_template_label` (template attivi kind `resume`)
- select `cover_letter_template_label` (template attivi kind `cover_letter`)
- input testo libero `resume_label` / `cover_letter_label` mantenuti per compatibilità

Regola pragmatica:
- se input libero è vuoto, viene usato il valore selezionato dal template
- se input libero è compilato, prevale il testo libero

### 3) Export CSV
`GET /admin/exports/shortlist.csv` resta compatibile e continua a esportare:
- `resume_label`
- `cover_letter_label`
- `submission_note`

## Workflow consigliato
1. Crea template riusabili in `/admin/templates` (es. `CV backend v2`, `CL generic data role`).
2. In shortlist usa i select template per compilare velocemente i dettagli candidatura.
3. Mantieni input libero per eccezioni/one-off.
4. Usa export CSV per audit materiali usati nelle submission.

## Test aggiunti/aggiornati
Nuovo:
- `tests/product/test_templates_step72.py`
  - persistenza templates
  - isolamento per-user
  - enable/disable/delete

Aggiornato:
- `tests/api/test_admin_ui_step30.py`
  - render pagina templates
  - create/enable/disable/delete flow base
  - shortlist che usa template selection

## Limiti noti
- nessun upload/storage file CV/CL
- nessun motore di rendering template
- nessuna generazione documenti AI
- nessun sync ATS/email

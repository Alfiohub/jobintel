# Application Details / Contact Memory v1 (Step 69)

## Obiettivo
Aggiungere una memoria candidatura più strutturata e per-user, senza trasformare il prodotto in un ATS/CRM complesso.

## Campi supportati
Estensione di `application_details` su chiave `(user_id, job_url)`:
- `application_channel` (es. `company_site`, `linkedin`, `referral`, `other`)
- `contact_name`
- `contact_email`
- `compensation_note`
- `external_application_url`

I campi restano opzionali e convivono con quelli già presenti:
- `notes`, `applied_at`, `interview_at`, `follow_up_at`, `follow_up_note`

## Storage / migration
File:
- `src/jobintel_next/product/application_tracking/service.py`

Aggiornamenti:
- schema `application_details` esteso con nuove colonne
- migration pragmatica con `ALTER TABLE` se colonne mancanti
- read/update/clear allineati ai nuovi campi

## UI shortlist aggiornata
Pagina:
- `GET /admin/shortlist`

Novità:
- nella colonna `Notes / Timeline` mostra anche:
  - `channel`
  - contatto (`name/email`) se presente
  - `external application link`
  - `compensation_note`
- form `Save details` esteso con input per i nuovi campi
- `Clear details` resetta anche i campi nuovi

Route coinvolte:
- `POST /admin/shortlist/details`
- `POST /admin/shortlist/details/clear`

## Piccolo impatto review
In `/admin/review` aggiunti due segnali pragmatici:
- `applied without channel`
- `interview` senza contatto (`contact_name/contact_email`)

## Workflow consigliato
1. In shortlist, quando passi a `applied`, imposta almeno `application_channel`.
2. Aggiungi contatto (`name/email`) appena disponibile.
3. Usa `external_application_url` come memoria rapida del thread esterno.
4. Compila `compensation_note` per mantenere vincoli/target senza note lunghe.

## Test aggiunti/aggiornati
Service:
- `tests/product/test_application_tracking_step60.py`
  - persistenza nuovi campi
  - isolamento per-user
  - clear completo

UI:
- `tests/api/test_admin_ui_step30.py`
  - update/clear nuovi campi da shortlist
  - render dettagli contatto/applicazione

## Limiti noti
- niente email/ATS sync
- niente allegati/CV storage
- niente CRM avanzato o model complesso contatti

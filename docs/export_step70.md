# Export / Reporting v1 (Step 70)

## Obiettivo
Permettere all’utente di portare fuori dal prodotto lo stato operativo della ricerca lavoro in modo semplice, per-user e immediato.

## Export supportati
In questo step:
- **Shortlist export CSV** per utente corrente (session-based)

Endpoint:
- `GET /admin/exports/shortlist.csv`

UI:
- bottone `Export CSV` in `/admin/shortlist`
- mantiene i filtri correnti nella query string (quando presenti)

## Campi inclusi nel CSV
- `title`
- `company`
- `url`
- `job_state`
- `application_state`
- `notes`
- `applied_at`
- `interview_at`
- `follow_up_at`
- `application_channel`
- `contact_name`
- `contact_email`
- `compensation_note`
- `external_application_url`
- `rank_score`
- `published_at`
- `role_family`
- `normalized_title`
- `location_type`
- `has_salary`

## Filtri supportati (coerenti con shortlist)
- `sort_by` (`rank|newest|salary`)
- `pipeline_state`
- `role_family`
- `only_remote`
- `only_salary`
- `exclude_other`
- `only_follow_up_set`
- `only_follow_up_due`

## Come si usa
1. Vai in `/admin/shortlist`.
2. Applica eventuali filtri/sort utili.
3. Click su `Export CSV`.
4. Ottieni file scaricabile con i job `saved` dell’utente corrente.

## Isolamento per-user
- export protetto da sessione (`/admin/*`)
- ogni utente esporta solo la propria shortlist/stato dettagli

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - presenza CTA export in shortlist
  - export CSV per-user
  - isolamento utenti nel contenuto
  - coerenza contenuto colonne principali

## Limiti noti
- nessun PDF reporting
- nessun export schedulato
- nessuna integrazione Google Sheets/Notion
- nessun reporting BI avanzato in questo step

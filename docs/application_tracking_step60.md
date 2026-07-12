# Application Tracking / Pipeline Lite v1 (Step 60)

## Obiettivo
Chiudere il loop operativo dopo il salvataggio job, trasformando la shortlist in una mini pipeline concreta e per-user.

## Stati pipeline supportati
Nuovo `application_state` per job salvati:
- `saved` (default implicito)
- `applied`
- `interview`
- `rejected`

Scelta di design:
- pipeline separata da `job_state`
- `job_state` resta per triage (`new|seen|saved|dismissed`)
- `application_state` traccia avanzamento candidatura

## Modulo introdotto
- `src/jobintel_next/product/application_tracking/service.py`
- `src/jobintel_next/product/application_tracking/__init__.py`

Operazioni base:
- `set_application_state(...)`
- `get_application_state(...)`
- `get_many_application_states(...)`
- `clear_application_state(...)`
- `count_application_states(...)`

Persistenza:
- tabella `application_state` su DB locale (riuso pragmatico `job_state.db`)
- chiave composta `(user_id, job_url)`

## Shortlist aggiornata
Pagina:
- `GET /admin/shortlist`

Novità UI:
- colonna `Pipeline` con stato corrente
- azioni rapide:
  - `Applied`
  - `Interview`
  - `Rejected`
  - `Reset Pipeline`
- filtro `pipeline_state` (`all/saved/applied/interview/rejected`)
- mini funnel counts in alto:
  - Applied / Interview / Rejected

Sort/filter shortlist già disponibili restano:
- sort: `rank`, `newest`, `salary`
- filtri: `role_family`, `only_remote`, `only_salary`, `exclude_other`

## Workflow consigliato
1. Salva job rilevanti in inbox/saved-search.
2. Apri `/admin/shortlist`.
3. Avanza pipeline su ogni opportunità (`Applied` -> `Interview` -> esito).
4. Usa filtro `pipeline_state` per focus operativo.
5. Mantieni `Reset Pipeline` per correzioni rapide.

## Test aggiunti/aggiornati
Nuovo (service):
- `tests/product/test_application_tracking_step60.py`
  - persistenza stato pipeline
  - isolamento per-user

Aggiornato (UI):
- `tests/api/test_admin_ui_step30.py`
  - render shortlist con pipeline
  - filtri pipeline
  - azioni rapide pipeline

## Limiti noti
- nessun tracking note/applications details
- nessun kanban avanzato
- nessun reminder/calendar
- nessuna integrazione ATS/email sync

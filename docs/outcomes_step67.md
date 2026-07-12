# Outcomes / Closed Loop Metrics v1 (Step 67)

## Obiettivo
Chiudere meglio il loop della ricerca lavoro con metriche funnel semplici e leggibili, basate sugli stati pipeline già presenti.

## Metriche introdotte
Layer outcome (`build_closed_loop_metrics`) calcola per utente:
- `open_pipeline_count` (`saved + applied + interview`)
- `applied_count`
- `interview_count`
- `rejected_count`
- `saved_to_applied_rate`
- `applied_to_interview_rate`
- `interview_to_rejected_rate`

Modulo:
- `src/jobintel_next/product/application_tracking/service.py`

## Superfici aggiornate

### `/admin`
Nuova sezione **Closed-loop Outcomes** con:
- KPI open/applied/interview/rejected
- conversioni principali (`Saved → Applied`, `Applied → Interview`)
- insight testuali semplici, ad esempio:
  - `You have X open opportunities`
  - `Y interviews currently active`
  - `High shortlist volume, low applied conversion` (solo in condizioni coerenti)

### `/admin/shortlist`
Nuova sezione **Outcome Summary** con:
- `Open opportunities`
- conversioni (`Saved → Applied`, `Applied → Interview`, `Interview → Rejected`)
- insight testuali coerenti col subset filtrato corrente

## Come leggere le metriche
1. **Open opportunities** misura backlog operativo reale.
2. **Saved → Applied** indica quanto shortlist diventa azione.
3. **Applied → Interview** mostra qualità candidature/fit nel tempo.
4. **Interview → Rejected** è utile come segnale di tuning candidatures/search.

## Test aggiunti/aggiornati
Nuovo:
- `tests/product/test_outcomes_step67.py`
  - calcolo conteggi/rate
  - comportamento sensato su input vuoto

Aggiornato:
- `tests/api/test_admin_ui_step30.py`
  - render sezioni outcomes su dashboard e shortlist

## Limiti noti
- nessuna analytics storica/time-series
- niente chart avanzati
- insight testuali volutamente semplici e rule-based
- nessun AI insight/recommendation in questo step

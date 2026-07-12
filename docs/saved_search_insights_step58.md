# Saved Search Performance / Quality Insights v1 (Step 58)

## Obiettivo
Aiutare l’utente a capire quali saved searches stanno producendo valore e quali stanno generando rumore, con metriche semplici e leggibili.

## Metriche introdotte
Per ogni saved search:
- `current_count`: risultati correnti della search
- `latest_new_count`: nuovi match dell’ultimo run noto (quando disponibile)
- `saved_marked_count`: job correnti marcati `saved`
- `dismissed_marked_count`: job correnti marcati `dismissed`
- `saved_rate`: quota `saved` sui job correnti campionati
- `dismiss_rate`: quota `dismissed` sui job correnti campionati
- `last_run_at`

Note implementative:
- le metriche di stato usano job state per-user
- per motivi pragmatici, il conteggio stato usa uno scan cap (`scan_limit`) sui risultati correnti

## Modulo/helper aggiunto
Nuovo modulo:
- `src/jobintel_next/product/saved_searches/insights.py`

Funzioni:
- `build_saved_search_insight(...)`
- `build_saved_search_insights_map(...)`

Queste aggregano in modo testabile:
- risultati search correnti
- job state per-user
- latest new count da run history (quando presente)

## Superfici aggiornate

### `/admin/saved-searches`
Aggiunte colonne insight:
- Current
- Latest New
- Saved Marks
- Dismissed Marks
- Saved %
- Dismiss %
- Quality

`Quality` mostra flag semplici (quando applicabili), es:
- `high dismiss rate`
- `no recent new matches`
- `no current matches`

### `/admin/saved-searches/{search_id}`
Aggiunti KPI e snapshot qualità:
- Saved marked / Dismissed marked
- Saved rate / Dismiss rate
- quality flags
- indicazione di sample parziale quando `current_count > scanned_count`

## Come interpretare le metriche
- **current_count alto + dismiss_rate alta**: probabile rumore, conviene stringere filtri/pack
- **saved_rate alta**: search utile, buona candidata a mantenere/duplicare
- **latest_new_count = 0** per run recenti: search potenzialmente stantia o troppo restrittiva
- **no current matches**: query troppo stretta o mercato momentaneamente vuoto

## Test aggiunti/aggiornati
Nuovo:
- `tests/product/test_saved_search_insights_step58.py`
  - calcolo metriche base (saved/dismissed/rates)
  - comportamento sensato senza history o state

Aggiornato:
- `tests/api/test_admin_ui_step30.py`
  - render lista con colonne insight
  - render dettaglio con quality snapshot/KPI

## Limiti noti
- non è analytics storica completa (no BI/time-series)
- rates calcolate su campione corrente (scan cap), non sempre su universo completo
- nessun recommendation engine o tuning automatico query

# Relevance / Ranking Foundation v1 (Step 56)

## Obiettivo
Introdurre un ranking leggero, deterministico e spiegabile per migliorare la qualità percepita dei risultati senza semantic search o ML pesante.

## Modulo introdotto
- `src/jobintel_next/product/ranking/service.py`
- `src/jobintel_next/product/ranking/__init__.py`

Funzioni principali:
- `compute_job_rank_score(...)`
- `rank_jobs(...)`

## Segnali usati nello score
Score cumulativo basato su segnali già presenti nel dominio:
- freschezza pubblicazione (`published_at`) con decay lineare 30 giorni
- freschezza update (`updated_at`) con peso ridotto
- `job_state` (favorisce `new`/`saved`, penalizza forte `dismissed`)
- `has_salary`
- `has_skills`
- `location_type` (bonus remoto, minore ibrido)
- `title_is_other` (penalty)
- fit con query quando disponibile:
  - `expected_normalized_title`
  - `expected_role_family`

Lo score è deterministico e restituisce anche `rank_factors` (breakdown per segnale).

## Logica sintetica
`compute_job_rank_score` restituisce:
- `rank_score` (float)
- `rank_factors` (dict con contributo di ogni segnale)

`rank_jobs`:
1. calcola score su ogni job
2. arricchisce il record con `rank_score` + `rank_factors`
3. ordina discendente per score (tie-break su `published_at`, poi URL)

## Superfici aggiornate
### Inbox
- `/admin/inbox`
- risultati ordinati con ranking
- colonna `Rank` visibile per ogni job

### Saved search workspace
- `/admin/saved-searches/{search_id}`
- risultati ordinati con ranking
- colonna `Rank` visibile
- quando la search è di tipo filters, il ranking usa anche fit su `normalized_title`/`role_family` se presenti nei filtri

## Test aggiunti/aggiornati
Nuovo:
- `tests/product/test_ranking_step56.py`
  - ordering coerente
  - preferenza job `new` rispetto a `dismissed`
  - effetto positivo del title fit

Aggiornato:
- `tests/api/test_admin_ui_step30.py`
  - presenza colonna `Rank` in inbox e saved search detail

## Limiti noti
- nessun embedding/vector/semantic layer
- pesi statici (non appresi)
- ranking applicato alle superfici admin principali, non ancora a tutto il layer API pubblico

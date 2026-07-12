# Search / Result Triage UX v1 (Step 57)

## Obiettivo
Rendere il ranking leggero introdotto nello step56 realmente utile nel workflow quotidiano di triage.

## Superfici migliorate

### `/admin/inbox`
Miglioramenti principali:
- sort esplicito:
  - `rank` (default)
  - `newest`
- quick filters ad alto ROI:
  - `only_remote`
  - `only_salary`
  - `exclude_other`
  - `high_rank_only`
- colonna `Why ranked` con spiegazione sintetica (es. `state:new, fresh, skills signal`)
- vista `state=saved` utilizzabile con `sort_by=newest` per shortlist operativa

### `/admin/saved-searches/{search_id}`
Miglioramenti principali:
- sort esplicito (`rank` / `newest`)
- stessi quick filters pragmatici dell’inbox
- colonna `Why ranked`
- ranking adattato ai filtri saved search quando disponibili (`normalized_title`/`role_family` fit)

### `/admin` (overview)
Nuova sezione:
- `Top Ranked New Jobs`
- mostra top job nuovi con:
  - rank
  - title/url
  - reason sintetica

## Come leggere il rank nel workflow
1. Apri inbox su `state=new` con `sort_by=rank`.
2. Applica quick filters (`only_remote`, `only_salary`, `exclude_other`) per ridurre rumore.
3. Usa `Why ranked` per capire rapidamente i driver del punteggio.
4. Sposta i job buoni in `saved`.
5. Vai in `state=saved&sort_by=newest` per gestire la shortlist nel tempo.

## Test aggiunti/aggiornati
Aggiornato:
- `tests/api/test_admin_ui_step30.py`
  - sort/filters in inbox
  - render `Why ranked`
  - saved view ordinata con `sort_by=newest`
  - sezione `Top Ranked New Jobs` in dashboard

Conferma ranking core:
- `tests/product/test_ranking_step56.py`

## Limiti noti
- ranking ancora a pesi statici (no apprendimento)
- quick filters solo sulle superfici admin principali
- nessun semantic/vector/LLM reranking

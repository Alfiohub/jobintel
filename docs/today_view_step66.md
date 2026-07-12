# Priority Queue / Today View v1 (Step 66)

## Obiettivo
Creare una vista giornaliera unica orientata all'azione, per evitare continui salti tra dashboard, inbox, shortlist e notifications.

## Nuova pagina
- `GET /admin/today`

## Sezioni della Today View
### 1) High Ranked New Jobs
- usa ranking deterministico esistente (`rank_score` + `rank_reason`)
- mostra top job `new` più rilevanti
- CTA: apertura job/inbox triage

### 2) Follow-up Due / Overdue
- usa `follow_up_at` + status (`due`/`overdue`)
- mostra solo elementi che richiedono azione
- CTA: shortlist filtrata `only_follow_up_due=true`

### 3) Shortlist Items Needing Attention
- segnali semplici da pipeline/application details:
  - `saved without notes`
  - `interview without date`
- priorità `high|medium` esplicita

### 4) High Priority Attention
- riuso del layer `attention` step64
- include solo item con priorità `high`
- CTA dirette alla superficie corretta

## Logica di priorità usata
Nessuna AI/magia opaca; solo regole deterministiche basate su:
- `rank_score`
- `follow_up_status`
- `application_state` + metadata (`notes`, `interview_at`)
- `attention_items` già esistenti

## Navigazione aggiornata
- navbar: nuovo link `Today`
- dashboard `/admin`: CTA `Open Today view`

## Workflow consigliato
1. Inizia da `/admin/today` ogni giorno.
2. Risolvi prima `Follow-up Due / Overdue`.
3. Passa a `Shortlist Items Needing Attention`.
4. Fai triage su `High Ranked New Jobs`.
5. Controlla `High Priority Attention` per errori/urgenze residue.

## Test aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render pagina today
  - presenza blocchi principali
  - presenza CTA/link
  - comportamento sensato con dati pochi/vuoti

## Limiti noti
- no AI prioritization/recommendation
- no realtime reminders
- no calendar sync
- no notifiche push

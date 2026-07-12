# Notification Center / Follow-up Digest v1 (Step 64)

## Obiettivo
Rendere più visibili le azioni operative urgenti con un layer di notifiche/attention per-user, leggero e derivato dai dati già presenti.

## Segnali usati (high ROI)
Attention builder per-user (`build_attention_items_for_user`) usa questi segnali:
1. follow-up `due/overdue`
2. saved searches `due now`
3. saved searches con quality flag (`high dismiss rate`, `no recent new matches`, ecc.)
4. latest alert run con digest error

Modulo:
- `src/jobintel_next/product/attention/service.py`

## Superfici aggiornate
### Dashboard `/admin`
Aggiunta sezione **Needs Attention** con:
- tipo (`follow_up`, `saved_search_due`, `saved_search_quality`, `digest_error`)
- titolo sintetico
- priorità (`high|medium|low`)
- CTA `Open`

### Pagina dedicata `/admin/notifications`
Vista completa delle attention items con la stessa semantica (priority + type + action link).

### Navbar
Nuovo link `Notifications`.

## Digest per-user aggiornato
`build_digest_body_text/html` supporta ora sezione opzionale **Needs attention**.

Nel workflow `alerts run-due --send-digest-email`:
- vengono calcolate attention items per-user
- il digest email include i top item (max 5)
- metadata delivery include `attention_items_count`

## Come leggere le notifiche
- **high**: azioni urgenti (es. follow-up overdue, digest error)
- **medium**: attività da completare presto (es. follow-up due, search due now)
- **low**: segnali di qualità/tuning

Ogni item punta direttamente alla superficie corretta (`shortlist`, `saved-search`, `alerts`).

## Test aggiunti/aggiornati
- `tests/product/test_attention_step64.py`
  - generation attention items da segnali multipli
- `tests/api/test_admin_ui_step30.py`
  - render dashboard `Needs Attention`
  - render pagina `/admin/notifications`
  - CTA/link principali
- `tests/product/test_digest_email_step48.py`
  - sezione `Needs attention` in digest text/html

## Limiti noti
- nessun realtime/websocket
- nessun push notification
- nessun reminder email separato automatico
- nessuna preference avanzata per notifiche
- layer attuale derivato/stateless (no mark read persistente)

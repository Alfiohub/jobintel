# Notification Preferences / Quieting v1 (Step 65)

## Obiettivo
Ridurre il rumore del layer attention/digest con preferenze per-user semplici e pragmatiche.

## Preferenze supportate
Nuovi campi utente (tabella `users`):
- `show_saved_search_quality_attention` (bool)
- `show_due_saved_search_attention` (bool)
- `show_follow_up_attention` (bool)
- `show_digest_error_attention` (bool)
- `digest_include_attention` (bool)

Default: tutte `true`.

## Integrazione nel prodotto
### Attention builder
`build_attention_items_for_user(...)` ora rispetta le preferenze utente correnti:
- se una categoria è disattivata, gli item di quel tipo non vengono generati

Modulo:
- `src/jobintel_next/product/attention/service.py`

### Dashboard / Notifications
Le sezioni:
- `/admin` → `Needs Attention`
- `/admin/notifications`
mostrano solo item consentiti dalle preferenze utente.

### Digest email
Nel flow `alerts run-due --send-digest-email`:
- se `digest_include_attention=false`, la sezione `Needs attention` non viene inclusa nel digest
- se `true`, include i top item filtrati dalle stesse preferenze notification

## Account UI aggiornata
`/admin/account` include nuova sezione **Notification Preferences** con checkbox semplici per:
- follow-up attention
- due saved searches attention
- saved search quality attention
- digest error attention
- include attention in digest

Save/update usa il form account esistente.

## Workflow consigliato
1. Tieni attive solo le categorie che ti servono nel quotidiano.
2. Disattiva `saved_search_quality_attention` se vuoi ridurre il rumore di tuning.
3. Disattiva `digest_include_attention` se vuoi digest più snello e solo sui nuovi match.
4. Usa `/admin/notifications` come vista completa solo quando necessario.

## Test aggiornati
- `tests/product/test_account_preferences_service_step45.py`
  - persistenza preferenze notification per-user
- `tests/api/test_account_preferences_step45.py`
  - render section `Notification Preferences` + update UI
- `tests/product/test_attention_step64.py`
  - attention builder filtra segnali secondo preferenze
- `tests/product/test_digest_email_step48.py`
  - digest rispetta `digest_include_attention`

## Limiti noti
- no mark-read persistente
- no snooze avanzato
- no realtime/push
- no preference engine complesso (solo toggle bool)

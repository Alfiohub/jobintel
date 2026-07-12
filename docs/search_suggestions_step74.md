# Saved Search Suggestions / Target-Aligned Query Helpers v1 (Step 74)

## Obiettivo
Usare il target profile per-user per guidare creazione/tuning delle saved searches con helper semplici, rule-based e trasparenti.

## Logica suggestion usata
Il sistema legge il profilo target utente e genera preset pragmatici:
- `target_role_families` -> suggerimenti `role_family=...`
- `target_titles` -> suggerimenti `normalized_title=...` (normalizzati in snake_case)
- `preferred_location_types` -> aggiunto `location_type` dove disponibile
- `keywords_note` -> helper opzionale `skills_contains=[...]`
- sempre aggiunto `title_is_other=false` come filtro anti-rumore di base

Nessuna AI e nessuna logica opaca: solo regole deterministiche.

## Superfici aggiornate

### `/admin/saved-searches/new`
Nuovo blocco **Target-aligned helpers** con:
- snapshot profilo target corrente
- pulsante/link `Use target profile`
- `Quick suggestions` clickabili che prefillsano:
  - `name`
  - `query_type=filters`
  - `filters_json`

Se il profilo è vuoto, viene mostrato un empty state guidato verso `/admin/account`.

### `/admin/saved-searches`
Aggiunto insight leggero per search esistenti:
- colonna `Target Alignment` (`aligned`, `location only`, `missing alignment`, `pack/manual review`)
- pannello `Target profile coverage gap` con role families target non ancora coperte da search abilitate

## Workflow consigliato
1. Imposta target profile in `Account`.
2. Vai in `New Saved Search` e usa `Use target profile` o un preset rapido.
3. Controlla `Saved Searches` per verificare `Target Alignment` e gap di copertura.
4. Crea/rifinisci search finché i gap principali sono coperti.

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render helper/suggestions in `saved-searches/new`
  - prefill con `use_target_profile=true`
  - comportamento con profilo vuoto
  - render alignment/gap in lista saved searches

## Limiti noti
- nessuna generazione query semantica
- nessun recommendation engine
- nessuna AI generation di saved search
- insight di allineamento volutamente semplici (rule-based)

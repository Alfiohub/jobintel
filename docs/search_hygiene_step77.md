# Search Hygiene / Noise Reduction v1 (Step 77)

## Obiettivo
Mantenere il portfolio di saved searches pulito e sostenibile nel tempo, riducendo rumore e sovrapposizioni con regole semplici e trasparenti.

## Regole hygiene usate
Analisi applicata alle saved searches **abilitate**:

1. **duplicate**
- stessa firma query (stesso `filters_json` normalizzato oppure stesso `pack_name`)

2. **overlap**
- search filters con scope molto simile su `role_family` e location compatibile
- utile per segnalare possibili sovrapposizioni operative

3. **stale**
- ultima run presente ma `latest_new_count = 0`

4. **noisy**
- dismiss rate alta (>= 0.6) con latest new basso (<= 1)

5. **low_yield**
- segnali persistenti di bassa resa (high dismiss-rate + assenza/pochi nuovi)

## Output generato
Blocco `Search Hygiene` in `/admin/saved-searches` con:
- KPI per categoria (`duplicate`, `overlap`, `noisy`, `stale`, `low_yield`)
- conteggio `candidate disable/review`
- lista item con:
  - categoria
  - severità (`high|medium|low`)
  - search
  - reason sintetica
  - related ids (se presenti)

## CTA operative
Per ogni item hygiene:
- `Open`
- `Edit`
- `Disable` (azione rapida, se search ancora enabled)

Questo permette un cleanup pragmatico senza workflow complessi.

## Superfici aggiornate
- `GET /admin/saved-searches`
  - nuovo blocco `Search Hygiene`
  - quick action disable nella lista hygiene

## Come interpretare i segnali
- **duplicate/high**: candidato forte a disabilitazione immediata
- **overlap/medium**: valutare merge logico o scope più distinto
- **stale/noisy/low_yield**: rivedere filtri e valore strategico della search
- usare insieme a `Target Coverage` e `Portfolio Strategy` per decisioni bilanciate

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render blocco `Search Hygiene`
  - rilevazione duplicate/overlap
  - rilevazione stale/noisy/low-yield in scenario reale
  - azione rapida `Disable` dalla lista hygiene
  - comportamento sensato con portfolio piccolo/vuoto

## Limiti noti
- nessun optimizer AI
- nessun merge automatico di search
- nessun semantic overlap detection
- regole volutamente conservative e rule-based

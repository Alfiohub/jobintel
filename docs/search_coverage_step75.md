# Saved Search Coverage / Gap Closure v1 (Step 75)

## Obiettivo
Aiutare l'utente a capire se le saved searches abilitate coprono davvero il target profile e dove mancano ricerche importanti.

## Logica coverage (rule-based)
Coverage analysis confronta:
- target profile per-user (`target_role_families`, `target_titles`, `preferred_location_types`)
- saved searches abilitate correnti

Analisi introdotta:
- **role family coverage**
- **normalized title coverage**
- **preferred location type coverage**

Per ogni target viene calcolato stato:
- `covered`: match esplicito in una search `filters` abilitata
- `partial`: copertura potenziale via search broad/pack (quando applicabile)
- `missing`: nessuna copertura rilevata

## Struttura coverage esposta
Nella UI vengono mostrati:
- KPI: `Targets`, `Covered`, `Partial`, `Missing`, `Coverage %`
- lista gap actionable (`missing` + `partial`) con:
  - tipo target (`role_family`, `normalized_title`, `location_type`)
  - spiegazione sintetica
  - CTA `Create search for missing target`

## Superfici aggiornate

### `/admin/saved-searches`
Nuovo blocco **Target Coverage**:
- KPI coverage
- gap list con CTA di chiusura
- comportamento vuoto quando profilo target non configurato

CTA gap closure usa prefill verso `/admin/saved-searches/new` con query params coerenti (`use_target_profile=true`, `filters_json` già impostato).

## Come leggere covered / partial / missing
1. **Covered**: target già coperto da almeno una search abilitata.
2. **Partial**: copertura incerta o indiretta, da rendere esplicita con una search dedicata.
3. **Missing**: target scoperto, da chiudere subito con CTA rapida.

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render blocco Target Coverage + KPI/gap list
  - CTA `Create search for missing target` con prefill
  - comportamento sensato con profilo vuoto
  - coerenza con colonna `Target Alignment`

## Limiti noti
- nessuna recommendation AI
- nessun matching semantico avanzato
- analisi coverage volutamente rule-based e conservativa
- pack coverage trattata in modo prudente (`partial`), non con inferenza profonda

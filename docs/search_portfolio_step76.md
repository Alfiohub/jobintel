# Search Portfolio / Strategy View v1 (Step 76)

## Obiettivo
Trasformare le saved searches abilitate da elenco tecnico a portfolio strategico leggibile, con categorie semplici e insight rule-based.

## Categorie strategiche usate
Ogni saved search viene classificata in una categoria pragmatica:
- `broad discovery`
- `target-aligned`
- `location-focused`
- `manual/pack review`

Regole principali (deterministiche):
- `pack` o `frequency=manual` -> `manual/pack review`
- allineamento target esplicito su role/title -> `target-aligned`
- filtro location senza role/title forte -> `location-focused`
- fallback -> `broad discovery`

## Vista aggiornata
Pagina principale aggiornata:
- `GET /admin/saved-searches`

Nuovi elementi:
1. **Search Portfolio / Strategy** (KPI)
- enabled count
- broad discovery count
- target-aligned count
- location-focused count
- manual/pack review count
- low-yield enabled searches

2. **Portfolio insights** (rule-based)
Esempi mostrati quando applicabili:
- `Too many broad searches compared to focused ones`
- `Missing focused target-aligned searches for your profile`
- `Portfolio dominated by low-yield searches`
- `Good balance between broad discovery and targeted searches`

3. **Tabella saved searches**
Per ogni search mostra anche:
- categoria strategica (`Strategy`)
- reason sintetica
- target alignment
- latest new / saved rate / dismiss rate / due / enabled

## Come leggere la vista
1. Controlla il mix categorie per capire se il portfolio è sbilanciato.
2. Usa gli insight per correggere rumorosità o gap strategici.
3. Apri CTA `Open` o `Create target-aligned search` per chiudere i gap.
4. Valida nel tempo con `latest_new_count`, `dismiss_rate`, `saved_rate`.

## Test aggiunti/aggiornati
- `tests/api/test_admin_ui_step30.py`
  - render blocco `Search Portfolio / Strategy`
  - presenza colonna `Strategy`
  - categorizzazione visibile (`broad`, `target-aligned`, `location-focused`, `manual/pack review`)
  - render `Portfolio insights`
  - compatibilità con coverage/alignment e empty state

## Limiti noti
- nessun optimizer AI
- nessuna generazione automatica di search
- nessun reasoning semantico avanzato
- insight portfolio volutamente semplici e rule-based

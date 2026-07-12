# Language Stage - Step 5

## Scopo
Implementare il primo stage reale di processing:

- input: `CanonicalRawJob`
- output: `LanguageDecision`

Il language stage lavora sul **raw posting** (title + excerpt description), non solo sul titolo.

## Moduli implementati
- `src/jobintel_next/pipelines/language/text_utils.py`
  - pulizia minima per language stage (unescape + strip HTML base)
  - costruzione testo combinato `title + description_excerpt`
- `src/jobintel_next/pipelines/language/policy.py`
  - policy finale di decisione `en/non_en/unknown`
- `src/jobintel_next/pipelines/language/stage.py`
  - wrapper stage (`run_one`, `run_many`)

## Policy (aggiornata)
1. `language_hint` è un segnale iniziale, non una verità assoluta.
2. La decisione usa sempre testo combinato da `CanonicalRawJob`:
- `title`
- excerpt di `description_raw` (dopo unescape + strip html minimo)
3. Viene usato un detector incapsulato (`lingua-language-detector`) su un set lingue ristretto.
4. Decision policy:
- hint + detector concordi e affidabili -> bucket concorde
- hint + detector in conflitto -> prevale detector solo con evidenza forte, altrimenti `unknown`
- detector debole -> fallback a heuristics testuali
- segnale complessivo debole -> `unknown`

## Output `LanguageDecision`
- `bucket`: `en | non_en | unknown`
- `reason`: stringa esplicita (`hint_detector_agree`, `hint_detector_conflict`, `detector_primary`, `hint_without_text_support`, ...)
- `language_code`: opzionale
- `confidence`: opzionale

## Esempi
- Hint `en` presente -> `en` (prioritario)
- Testo francese chiaro in description -> `non_en`
- Titolo corto e senza description -> `unknown`

## Limiti noti
- Detector limitato a un set lingue europee principali; lingue fuori set tendono a `unknown`.
- Su testi molto corti o misti la policy preferisce `unknown`.
- Non usa ancora segmentazione completa del posting.

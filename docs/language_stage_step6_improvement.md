# Language Stage Step 6 Improvement

## Problema osservato
Nel primo run di evaluation il language stage era quasi totalmente guidato da `language_hint`:
- `hint_en` e `hint_non_en` dominavano i reason counts
- rischio concreto: hint errato => bucket errato

## Miglioramento implementato
- `language_hint` degradato a **segnale** (non decisione finale automatica).
- Introduzione detector incapsulato con `lingua-language-detector`.
- Decisione finale orchestrata dalla policy interna:
  - agreement hint+detector -> usa bucket condiviso
  - conflict hint+detector -> evita fiducia cieca nel hint
  - detector debole -> fallback heuristics
  - segnale debole/misto -> `unknown`

## Nuovi reason principali
- `hint_detector_agree`
- `hint_detector_disagree_detector_override`
- `hint_detector_conflict`
- `detector_primary`
- `hint_without_text_support`
- `hint_without_enough_text`

## Cosa resta invariato
- Input: `CanonicalRawJob`
- Output: `LanguageDecision`
- Bucket supportati: `en`, `non_en`, `unknown`

## Limiti noti
- Il detector è limitato a un set lingue candidate pratico.
- Posting multilingua o con testo poco informativo possono restare `unknown` per prudenza.

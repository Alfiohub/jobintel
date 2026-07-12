# CanonicalRawJob Contract (V1)

## Scopo
`CanonicalRawJob` è il **contratto interno stabile** che rappresenta un annuncio dopo il mapping da ATS esterno e prima del processing (language, cleaning, extraction, title classification).

È il handoff ufficiale tra:
- ingestion (adapter + mapper)
- processing pipeline (step successivi)

## Perché esiste
- evita dipendenza diretta dal formato specifico di ogni ATS
- rende il processing uniforme e testabile
- riduce regressioni quando cambia un adapter esterno
- mantiene tracciabilità grazie al `raw_payload` preservato

---

## Differenze: ATS payload vs SourceRawJob vs CanonicalRawJob

## Payload ATS esterno
- formato proprietario (es. Greenhouse JSON)
- variabile per source
- contiene molte informazioni non normalizzate

## SourceRawJob
- snapshot del fetch per una source
- include payload grezzo + metadati fetch (`source`, `source_org`, `fetched_at`, ecc.)
- ancora source-specific

## CanonicalRawJob
- modello interno comune a tutte le source
- campi minimi stabili per processing downstream
- nessuna logica semantica avanzata (solo mapping)

---

## Campi consigliati `CanonicalRawJob`

## Obbligatori

| Campo | Significato | Esempio | Origine Greenhouse | Perché serve |
|---|---|---|---|---|
| `source` | sorgente ATS | `"greenhouse"` | costante adapter | routing e analytics per source |
| `source_org` | tenant/board ATS | `"found"` | slug board (`/boards/{slug}`) | dedup, troubleshooting, multi-tenant |
| `url` | URL pubblico annuncio | `"https://job-boards.greenhouse.io/found/jobs/4652575005"` | `absolute_url` | chiave funzionale e link prodotto |
| `title` | titolo raw annuncio | `"Data Analytics Director"` | `title` | base per cleaning/title normalization |
| `company_name` | nome azienda raw | `"Found"` | `company_name` | display e feature search/filter |
| `raw_payload` | payload ATS completo preservato | `{...}` | intero JSON risposta job | audit/debug/reprocess |

## Opzionali

| Campo | Significato | Esempio | Origine Greenhouse | Perché serve |
|---|---|---|---|---|
| `external_id` | id esterno ATS | `"4652575005"` | `id` | dedup e riconciliazione |
| `location_raw` | location testuale non normalizzata | `"Remote"` | `location.name` | input per normalization location |
| `published_at` | prima pubblicazione | `"2026-01-22T15:31:21+00:00"` | `first_published` | ranking temporale/business freshness |
| `updated_at` | ultimo update annuncio | `"2026-03-25T05:00:22+00:00"` | `updated_at` | incremental ingest e freshness |
| `language_hint` | hint lingua non definitivo | `"en"` | `language` | seed per language decision |
| `description_raw` | descrizione raw (anche HTML) | `"<div>..."` | `content` | input per cleaning/sectioning |
| `departments_raw` | reparti raw ATS | `[{"name":"Data Analytics"}]` | `departments` | metadata org opzionale |
| `offices_raw` | offices raw ATS | `[{"location":"Remote"}]` | `offices` | metadata location opzionale |

Nota pratica: in Greenhouse `first_published` e `updated_at` vanno mantenuti distinti. Se manca `first_published`, `published_at` può restare `null`.

---

## Cosa NON deve essere calcolato qui
Nel mapping `CanonicalRawJob` **non** devono comparire campi derivati di processing:
- decisione lingua (`en/non_en/unknown`)
- `title_clean`, `description_clean`, `content_hash`
- salary/location type/skills/seniority/education
- `normalized_title`, `role_family`, confidence di classificazione

Questi appartengono ai successivi stage:
1. language decision
2. cleaning
3. extraction
4. title classification

---

## Invariants (regole del contratto)
1. `url` è obbligatorio e non vuoto.
2. `title` è obbligatorio e non vuoto.
3. `raw_payload` deve essere preservato senza perdita informativa.
4. `published_at` e `updated_at` sono concetti distinti (non forzare merge).
5. `company_name` usa il valore migliore dal payload ATS; non derivarlo dal board se esiste un valore più affidabile nel payload.
6. Il mapping deve essere deterministico: stesso payload in input => stesso `CanonicalRawJob` in output.
7. Campi nuovi futuri devono essere opzionali per compatibilità retroattiva.

---

## Mapping notes for future ATS
Ogni nuovo adapter (Lever, SmartRecruiters, ecc.) deve convergere su **questo stesso contratto**.

Regola operativa:
- adapter/client: solo fetch source-specific
- mapper source-specific: converte in `CanonicalRawJob`
- processing downstream: ignora dettagli della source e lavora solo sul contratto canonico

Se una source non fornisce un campo, il mapper lascia `null` (non inventa valori semantici).

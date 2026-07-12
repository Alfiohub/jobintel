# Domain Contracts - Step 3

## Scopo
Definire i contratti dati interni stabili prima di implementare language detection, cleaning, extraction, title normalization e indexing engine.

Strategia scelta: **dataclass** (singolo stile coerente).

---

## Modelli

## 1) SourceRawJob
- Produce stage: source adapter/client (immediatamente dopo fetch HTTP)
- Consume stage: canonicalization mapper
- Obbligatori: `source`, `source_org`, `fetched_at`, `payload`
- Opzionali: `source_record_id`

## 2) CanonicalRawJob
- Produce stage: mapper per source (`greenhouse mapper`)
- Consume stage: language decision + cleaning
- Obbligatori: `source`, `source_org`, `url`, `title`, `company_name`
- Opzionali: `external_id`, `location_raw`, `posted_at`, `language_hint`, `description_raw`, `raw_payload`

## 3) LanguageDecision
- Produce stage: language detector/policy
- Consume stage: gating pre-cleaning e reporting
- Obbligatori: `url`, `bucket`, `reason`
- Opzionali: `language_code`, `confidence`

## 4) CleanedJob
- Produce stage: cleaning
- Consume stage: extraction + title normalization
- Obbligatori: `url`, `title_clean`, `description_clean`, `location_clean`
- Opzionali: `requirements_clean`, `responsibilities_clean`, `content_hash`

## 5) ExtractedAttributes
- Produce stage: extraction
- Consume stage: indexing
- Obbligatori: `url`
- Opzionali: seniority/employment/location/salary/skills/tags

## 6) TitleClassification
- Produce stage: title normalization/classification
- Consume stage: indexing
- Obbligatori: `url`, `normalized_title`, `role_family`, `classification_status`, `match_method`, `confidence`
- Opzionali: `matched_rule_id`, `notes`

## 7) IndexedJob
- Produce stage: indexing builder
- Consume stage: serving/query/search layer
- Obbligatori: `source`, `source_org`, `url`, `company_name`, `title_raw`, `title_clean`, `normalized_title`, `role_family`, `classification_status`, `match_method`, `confidence`
- Opzionali: lingua/localizzazione/salary/skills/tags

---

## Flusso tra modelli
`SourceRawJob -> CanonicalRawJob -> LanguageDecision -> CleanedJob -> (ExtractedAttributes + TitleClassification) -> IndexedJob`

Nota: `LanguageDecision` può agire come gate (skip/non_en/unknown) prima di cleaning.

---

## Stabilità del contratto
1. I campi obbligatori non si rimuovono senza versione nuova del contratto.
2. Nuovi campi devono essere opzionali per backward compatibility.
3. I nomi campo usati nei file JSONL devono restare stabili.
4. Ogni stage deve leggere solo il contratto precedente, evitando dipendenze implicite.
5. Serializzazione standard via helper `domain.models.serde`.

---

## File implementati
- `src/jobintel_next/domain/models/contracts.py`
- `src/jobintel_next/domain/models/serde.py`
- `src/jobintel_next/domain/models/__init__.py`

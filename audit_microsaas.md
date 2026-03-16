# Audit Tecnico e Architetturale - `automation/microsaas`

## Scope
File revisionati:
- `automation/microsaas/export_greenhouse_jobs.py`
- `automation/microsaas/run_microsaas_pipeline.py`
- `automation/microsaas/title_normalization.py`
- `automation/microsaas/tag_extraction.py`
- `automation/microsaas/build_gold_eval_set.py`
- `automation/microsaas/autolabel_gold_eval.py`
- `analyze_review_cases.py`
- `db_schema_microsaas.sql`

---

## Problemi (ordinati per priorita')

## P0 - Drift logico tra componenti di valutazione/labeling
1. Regole review non allineate tra pipeline di autolabel e analisi review.
   - `autolabel_gold_eval.py` ha logica aggiornata per `location_without_country` (piu' conservativa).
   - `analyze_review_cases.py` usa ancora regola piu' aggressiva (`location_type` valorizzato + country vuoto).
   - Impatto: metriche review distorte e decisioni operative basate su conteggi incoerenti.

2. Normalizzazione paese/enum duplicata in piu' script.
   - Alias country e validazioni location/employment/seniority sono replicate tra `autolabel_gold_eval.py`, `tag_extraction.py`, `location_normalization.py`, `rerun_review_subset.py`.
   - Impatto: stessi input possono dare output diversi a seconda del punto pipeline.

## P1 - Responsabilita' troppo concentrate
3. `run_microsaas_pipeline.py` resta molto grande e multifunzione.
   - Orchestration + cleaning + embedding providers + schema migration + cache policy + persistence SQL + reporting.
   - Refactor recente ha ridotto duplicazioni, ma il file e' ancora un "god script".
   - Impatto: alto costo di manutenzione, rischio regressioni su cambiamenti piccoli.

4. SQL inline molto esteso e fragile.
   - Query `INSERT ... VALUES(?,...,?)` lunghe e ad alta probabilita' di mismatch colonne/placeholders.
   - Impatto: errori runtime facili da introdurre durante evoluzione schema.

## P1 - Dato "strutturato" ma in parte placeholder
5. Tassonomia esterna (`taxonomy_*`) e' attualmente placeholder.
   - `taxonomy_mapping.py` usa regole statiche di esempio, non dataset ESCO/O*NET reali.
   - Impatto: rischio di interpretare campi tassonomici come "ground truth" quando non lo sono.

6. Confidence per campo sono euristiche fisse non calibrate.
   - `tag_extraction.py` produce valori utili ma non validati su benchmark.
   - Impatto: downstream potrebbe usarle come probabilita' reali.

## P2 - Coerenza modello dati e utilizzo operativo
7. Campi DB ricchi ma parzialmente sottoutilizzati.
   - Es: `processing_version`, `extraction_version`, `experience_text_raw`, `education_text_raw`, `taxonomy_*`, confidence granulari.
   - Manca una "data quality dashboard" o report automatico che usi sistematicamente questi campi.

8. Stratified sampling gold migliorato ma non ancora "quality-aware" end-to-end.
   - `build_gold_eval_set.py` ha controlli opzionali validi, ma non c'e' un controllo post-sample con soglie minime/alert.
   - Impatto: i campioni possono comunque deviare senza feedback forte.

## P3 - Robustezza operativa
9. Export Greenhouse deduplica solo per `id`.
   - Potenziale collisione cross-board/source org se il provider non garantisce global uniqueness.
   - Impatto basso/medio ma reale in scaling multi-source.

10. Scripts eterogenei senza libreria condivisa di utility.
   - Pattern ripetuti: parsing CSV, normalizzazione token, merge note, parse JSON from LLM output, ecc.
   - Impatto: manutenzione dispersiva.

---

## Quick Wins (basso costo, alto ritorno)

1. Unificare regole review in un modulo condiviso.
   - Estrarre in `automation/microsaas/review_rules.py` la logica usata sia da `autolabel_gold_eval.py` sia da `analyze_review_cases.py`.

2. Unificare normalizzazioni comuni.
   - Creare `automation/microsaas/normalization_common.py` con:
     - country aliases e `_normalize_country`
     - normalizzazione enum (`location_type`, `employment_type`, `seniority`)
     - helper liste (`_normalize_semicolon_list`)

3. Aggiungere test minimi "golden" per funzioni critiche.
   - `title_normalization.normalize_title`
   - `tag_extraction.extract_salary`
   - `location_normalization.normalize_location`
   - `_apply_rule_based_review` vs `_extract_categories` (coerenza)

4. Ridurre fragilita' SQL con helper centralizzato.
   - Funzione interna che costruisce dinamicamente colonne/values da dict per `extraction_cache` e `jobs_indexed`.

5. Etichettare esplicitamente i campi placeholder.
   - Aggiungere nota nel report pipeline: `taxonomy_mapping_mode=placeholder_rules`.

---

## Refactor non urgenti

1. Separare `run_microsaas_pipeline.py` in moduli:
   - `pipeline_orchestrator.py`
   - `persistence_sqlite.py`
   - `embedding_client.py`
   - `cleaning.py`

2. Introdurre typed models (dataclass/Pydantic) per record intermedi.
   - Evita dict-key drift tra cache, indexed row, save DB.

3. Centralizzare configurazione.
   - Parametri hardcoded (version strings, thresholds, default models, limits) in file config unico.

4. Reporting strutturato.
   - Unire report pipeline, review analysis e sampling QA in un artefatto unico (JSON + markdown).

---

## Campi DB incoerenti/sottoutilizzati (focus)

1. `taxonomy_*`:
   - coerenti a schema, ma semanticamente "beta/placeholder".

2. `title_confidence/location_confidence/...`:
   - presenti e salvati, ma senza calibrazione o monitoraggio drift.

3. `processing_version/extraction_version`:
   - valorizzati, ma non usati per compatibilita' controllata (es. backfill guidato da versione).

4. `tags_json`:
   - contiene metadati utili (es. `country_source`) ma manca uno standard esplicito di contratto versione.

---

## Roadmap proposta (3 fasi)

## Fase 1 - Stabilizzazione (1-2 settimane)
- Allineare logica review tra autolabel e analyzer (single source of truth).
- Estrarre modulo normalizzazioni comuni.
- Aggiungere test minimi per salary/location/title/review rules.
- Aggiungere quality checks post-sampling (assert di distribuzione e quota `other`).

Deliverable:
- meno falsi allarmi review
- regressioni intercettate presto
- comportamento consistente tra script.

## Fase 2 - Hardening pipeline (2-4 settimane)
- Rifattorizzare persistence SQL (builder per upsert).
- Spezzare `run_microsaas_pipeline.py` in moduli.
- Introdurre modelli tipizzati per i record (cache/indexed/tags).
- Migliorare osservabilita' (report unico con warning su placeholder fields).

Deliverable:
- pipeline piu' mantenibile
- minore rischio di errori su evoluzione schema.

## Fase 3 - Qualita' semantica e scaling (4+ settimane)
- Integrare mapping ESCO/O*NET reale (file lookup versionato + confidence ragionata).
- Calibrare confidence per campo su benchmark gold.
- Raffinare ranking con segnali calibrati (non solo euristiche statiche).
- Estendere campioni gold a nuove fonti/lingue mantenendo QA standardizzato.

Deliverable:
- qualita' parsing/ranking piu' affidabile
- tassonomia esterna utilizzabile in prodotto, non solo informativa.

---

## Conclusione sintetica
Il sottoprogetto e' in buono stato operativo per MVP locale: pipeline end-to-end, DB coerente, tooling di review e sampling presenti. I rischi principali non sono "mancanza di feature", ma **coerenza logica tra script**, **fragilita' da SQL/manual wiring** e **placeholder che sembrano definitivi**. Con i quick wins sopra, la qualita' aumenta sensibilmente senza stravolgere l'architettura.


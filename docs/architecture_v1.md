# Architecture V1 (Pratica) - jobintel_next

## 1) Obiettivo Del Sistema
Costruire una base SaaS solida per ingestione e indicizzazione annunci lavoro con pipeline chiara e incrementale:

`source adapters -> ingestion/canonicalization -> language gate -> cleaning -> extraction -> title normalization -> indexing -> serving`

Obiettivi pratici V1:
- separare responsabilità (niente script monolitici scollegati)
- rendere i passaggi testabili in isolamento
- mantenere contratti dati stabili tra moduli
- permettere estensione a nuove fonti oltre Greenhouse

---

## 2) Stato Attuale: Analisi Rapida

### Cosa c'è di buono
- `clients/greenhouse.py` già incapsula accesso HTTP + mapping base.
- `collectors/greenhouse.py` introduce già il concetto di adapter sorgente.
- `source_registry.py` introduce (anche se minimale) il boundary “source -> collector”.
- Export JSONL funziona su board singolo e multi-board.

### Cosa è duplicato/confuso
- Mapping Greenhouse è presente sia in `clients/greenhouse.py` che in `collectors/greenhouse.py`.
- Più entrypoint (`cli.py`, `main.py`, `automation/export_*`) con responsabilità sovrapposte.
- `config.py` (env) e config YAML convivono senza un contratto unico.
- Script discovery (`ddg_discover`, `commoncrawl_seed`) stanno vicino al core ingest ma sono tool di supporto.

### Cosa va preservato
- Greenhouse HTTP logic robusta (retry, timeout, concorrenza).
- Output JSONL canonico come formato di handoff.
- Config basata su `sources.*` per abilitare scaling multi-source.

### Cosa va rifuso
- Unico mapper Greenhouse (no duplicazione client/collector).
- Unico layer orchestration per ingestion (invece di più script equivalenti).
- Contratti dati espliciti e versionati tra stage.

---

## 3) Architettura Target Minima V1

## Moduli e confini

1. `adapters/` (source adapters)
- Responsabilità: parlare con API esterne e ritornare `SourceRawJob`.
- Nessuna logica di cleaning/normalization.

2. `ingestion/`
- Responsabilità: orchestrare fetch, dedup tecnico iniziale, mapping a `CanonicalRawJob`.
- Definisce interfacce comuni per tutti gli adapter.

3. `language/`
- Responsabilità: classificare lingua (`en` / `non_en` / `unknown`) e motivazione.
- Nessuna logica title extraction qui.

4. `cleaning/`
- Responsabilità: pulizia testuale deterministica (html strip, whitespace, section slicing).

5. `extraction/`
- Responsabilità: attributi strutturati (salary, location_type, skills, employment, ecc.).

6. `titles/`
- Responsabilità: title normalization/classification indipendente.
- Input: titolo pulito + varianti lessicali.
- Output: contratto `TitleClassification`.

7. `indexing/`
- Responsabilità: costruire `IndexedJob` pronto per query/serving.
- Gestisce anche persistenza (jsonl/sqlite) in modo coerente.

8. `serving/` (futuro SaaS layer)
- Responsabilità: API query/filter/search su `IndexedJob`.
- Non contiene logica di ingest.

---

## 4) Contratti Dati Principali (concettuali)

1. `SourceRawJob`
- payload sorgente + metadati fetch (`source`, `source_org`, `fetched_at`).

2. `CanonicalRawJob`
- campi minimi normalizzati: `id`, `url`, `title`, `company_name`, `location_raw`, `description_raw`, `posted_at`, `language_hint`, `raw_payload`.

3. `CleanedJob`
- `title_clean`, `description_clean`, `requirements_clean`, `responsibilities_clean`, `content_hash`.

4. `ExtractedAttributes`
- `seniority`, `employment_type`, `location_type`, `country/city/region`, `salary_*`, `skills`, `confidence_*`.

5. `TitleClassification`
- `normalized_title`, `role_family`, `classification_status`, `match_method`, `confidence`, `matched_rule_id`, `notes`.

6. `IndexedJob`
- aggregato finale per serving: canonical + cleaned + extracted + title + embedding/meta indexing.

Regola chiave: ogni stage legge contratto precedente e scrive il successivo, senza side-effect impliciti.

---

## 5) Greenhouse: trattamento corretto

### A) HTTP client (`adapters/greenhouse/client.py`)
- solo chiamate API, retry, timeout, pagination/concurrency.
- ritorna payload raw Greenhouse.

### B) Mapper (`adapters/greenhouse/mapper.py`)
- converte payload Greenhouse in `SourceRawJob` / `CanonicalRawJob`.
- unica fonte mapping (evitare doppioni in collector o script).

### C) Collector/orchestrator (`ingestion/collectors/greenhouse_collector.py`)
- coordina: `client -> mapper -> stream/list`.
- non deve fare cleaning/extraction/title.

---

## 6) Data Flow End-to-End

1. `ingest run`:
- legge config `sources`
- esegue adapter collector
- produce `raw_jobs.jsonl` (canonical raw)

2. `process run`:
- language gate
- cleaning
- extraction
- title normalization
- indexing
- produce `jobs_indexed.jsonl` + DB

3. `serve run` (futuro):
- carica indice/DB
- espone API SaaS

---

## 7) Decisioni Architetturali V1
- **Pipeline a stage espliciti**: no “mega script”.
- **Contratti dati stabili**: dataclass/pydantic per ogni stage.
- **Adapter isolati**: ogni fonte ATS in modulo indipendente.
- **Script automation separati dal core**: discovery seed tools fuori dal percorso critico.
- **Idempotenza**: dedup basato su hash/chiavi stabili.

---

## 8) Anti-pattern Da Evitare
- Duplicare mapping fonte in più file.
- Mischiare fetch + cleaning + extraction nello stesso modulo.
- Aggiungere nuovi script ad-hoc senza inserirli nel flow ufficiale.
- Accoppiare troppo presto serving con ingestion internals.
- Cambiare contratti output senza versionamento minimo.

---

## 9) Piano di Migrazione Dall'attuale Struttura

### Step 1 (immediato, basso rischio)
- Congelare i file attuali come seed funzionante.
- Introdurre struttura target (cartelle vuote + contratti di dominio).
- Spostare il mapping Greenhouse in un punto unico.

### Step 2
- Unificare entrypoint ingestion in un solo comando ufficiale.
- Fare deprecazione soft di script duplicati (`automation/export_*` wrapper verso nuovo modulo).

### Step 3
- Portare language/cleaning/extraction/title/indexing in moduli separati con test.
- Ogni modulo con input/output dichiarato.

### Step 4
- Introdurre persistenza indice e API serving come layer separato.

---

## 10) Primo Step Tecnico Consigliato Dopo Questo Documento
Implementare **solo il refactor Greenhouse boundary**:
1. `adapters/greenhouse/client.py`
2. `adapters/greenhouse/mapper.py`
3. `ingestion/collectors/greenhouse_collector.py`
4. aggiornare `source_registry` a usare quel collector
5. eliminare duplicazione mapping client/collector

Questo dà subito ordine senza aprire ancora il resto della pipeline.

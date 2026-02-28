# jobintel

Pipeline di job intelligence: raccoglie, valuta, deduplica e notifica offerte di lavoro.

## Stato Del Repo
- `src/jobintel/*`: runtime attuale del prodotto
- `modules/*`: target architecture del monorepo, ancora in migrazione
- `scripts/train_ner_baseline.py` e docs NER: baseline sperimentale per training locale/Colab
- `data/` e `.secrets/`: locali, non fanno parte del repo pubblico

## Mappa Progetto
- Runtime attuale: `src/jobintel/*`
- Moduli target (monorepo): `modules/*`
- Contratti:
  - `openapi_v1.yaml`
  - `db_schema_v1.sql`
  - `architecture_v1.md`
- Documentazione operativa: `docs/README.md`

## Cosa fa
- Colleziona job da Greenhouse
- Assegna uno score con regole semplici
- Evita duplicati con SQLite
- Stampa risultati in console (instant/digest)

## Requisiti
- Python 3.13
- `uv`

## Installazione
```bash
uv venv .venv --python 3.13
source .venv/bin/activate
uv pip install -e .
```

## Comandi rapidi (per chi non sa nulla)

### 1) Scopri aziende (automatico)
Esegue dorking su DuckDuckGo, verifica gli slug Greenhouse e crea un file di target.
```bash
uv run --active python scripts/ddg_discover.py
```
Output:
- crea `config/generated/targets.yml`
- stampa quante aziende ha trovato

### 2) Lancia la pipeline
Usa la lista generata e stampa i risultati.
```bash
uv run --active jobintel --config config/generated/targets.yml
```
Output atteso:
```
=== INSTANT (high match) ===
...
=== DIGEST (medium match) ===
...
```

### 3) Vedi i risultati salvati
I job finiscono in SQLite.
```bash
sqlite3 data/jobintel.sqlite "select score, company, title, url from seen_jobs order by score desc limit 20;"
```

## API (per frontend)
Avvia un’API HTTP per filtrare i job dal frontend.
```bash
uv run --active uvicorn jobintel.api:app --reload --port 8001
```

Esempi:
- `http://127.0.0.1:8001/jobs`
- `http://127.0.0.1:8001/v1/jobs`
- `http://127.0.0.1:8001/jobs?min_score=80`
- `http://127.0.0.1:8001/jobs?remote=true`
- `http://127.0.0.1:8001/jobs?location=Europe`
- `http://127.0.0.1:8001/jobs?date_from=2026-02-01&date_to=2026-02-12`

## Config (opzionale)
Esempi:
- `config/default.yml`
- `config/examples/data_analyst.yml`
- `config/examples/local.example.yml`

## Dove finiscono i dati
SQLite in `data/jobintel.sqlite`.

## Test rapidi
```bash
uv run --active pytest -q
```

## Sicurezza
- Non committare chiavi/API token.
- Usa variabili ambiente per script locali e non versionare config/secrets locali.

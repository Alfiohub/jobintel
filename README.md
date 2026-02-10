# jobintel

Pipeline di job intelligence: raccoglie, valuta, deduplica e notifica offerte di lavoro.

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

## Config
Esempi:
- `config/default.yml`
- `config/examples/data_analyst.yml`

Per l’uso reale crea un file locale (non versionato) con le tue chiavi:
```bash
cp config/examples/data_analyst.yml config/local.yml
```

## Esecuzione
```bash
uv run jobintel run --config config/local.yml
```

## Discovery (branch aggregators)
Nel branch `feature/aggregators` trovi il comando per scoprire board Greenhouse via TheirStack:
```bash
uv run jobintel discover --config config/discovery.yml
```

## Dove finiscono i dati
SQLite in `data/jobintel.sqlite`.

Query veloce:
```bash
sqlite3 data/jobintel.sqlite "select score, company, title, source from seen_jobs order by score desc limit 20;"
```

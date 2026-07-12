# Demo Pack ufficiale v1 (Step 33)

## Obiettivo
Fornire una demo ufficiale, piccola e riproducibile, per mostrare rapidamente il progetto senza dipendere dal dataset completo.

## Cosa contiene il demo pack
Path base: `data/demo/`

- `jobs_indexed_demo.jsonl`  
  Dataset indexed piccolo (8 job), con:
  - più `role_family` (`software_engineering`, `data_engineering`, `sales`, `marketing`, `healthcare_clinical`, `skilled_trades`, `other`)
  - job con salary e senza salary
  - job remote/hybrid/onsite
  - skill set minimi utili (`python`, `sql`, `dbt`, ecc.)
- `jobs_indexed_demo.db`  
  SQLite index demo costruito dal JSONL demo.
- `saved_searches_demo.db`  
  Saved searches demo seedate:
  - `Demo Python Tech` (filters)
  - `Demo Remote Data Jobs` (pack)
  - `Demo High Confidence Tech` (pack)
- `alerts/runs/<run_id>.json|.md`  
  Un run demo già generato per mostrare history e dettaglio.

## Comandi demo aggiunti (Makefile)
- `make demo`  
  Build index demo + seed saved searches demo.
- `make demo-alerts`  
  Esegue run-all sul demo pack e genera artifact in `data/demo/alerts/runs`.
- `make demo-api`  
  Avvia API + Admin UI con env puntate al demo pack.
- `make help`  
  Mostra tutti i target, inclusi quelli demo.

## Flow demo consigliato (5-6 passi)
1. Preparare il demo pack:

```bash
make demo
```

2. Generare un run alert demo:

```bash
make demo-alerts
```

3. Avviare API + Admin UI in modalità demo:

```bash
make demo-api
```

Se `:8000` è occupata:

```bash
make demo-api APP_PORT=8010
```

4. Aprire overview:
- `http://127.0.0.1:8000/admin`

5. Mostrare saved searches:
- `http://127.0.0.1:8000/admin/saved-searches`

6. Mostrare alert summary + dettaglio run:
- `http://127.0.0.1:8000/admin/alerts`
- aprire un run in `http://127.0.0.1:8000/admin/alerts/{run_id}`

## Cosa mostrare in Admin UI
- overview con run count e latest run
- lista saved searches già pronta (edit/run/delete)
- run-all e dettaglio con `new_matches_count`
- history runs locale per osservabilità operativa

## Limiti del demo pack vs dataset reale
- coverage ridotta (solo pochi esempi, no long-tail reale)
- no rappresentatività statistica completa
- utile per portfolio/demo UX, non per valutazioni quantitative finali

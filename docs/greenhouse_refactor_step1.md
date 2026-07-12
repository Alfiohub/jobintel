# Greenhouse Refactor - Step 1

## Scopo
Pulire il boundary Greenhouse separando:
- HTTP client
- mapper
- collector/orchestrator

## Cosa è stato spostato

Nuovo path ufficiale:
- `src/jobintel_next/adapters/greenhouse/client.py`
  - solo chiamate HTTP Greenhouse API (timeout, retry)
  - nessun mapping business

- `src/jobintel_next/adapters/greenhouse/mapper.py`
  - unica fonte mapping Greenhouse -> `CanonicalRawJob`

- `src/jobintel_next/ingestion/collectors/greenhouse_collector.py`
  - orchestration boards + concurrency
  - usa client + mapper
  - nessuna logica cleaning/extraction/title

## Cosa resta legacy (temporaneamente)
- `src/jobintel_next/clients/greenhouse.py`
- `src/jobintel_next/collectors/greenhouse.py`

Questi file ora sono shim di compatibilità e reindirizzano al nuovo path.
Non vanno usati per nuovo sviluppo.

## Path ufficiale ora
- Registry: `src/jobintel_next/source_registry.py` -> nuovo collector ingestion
- Main entrypoint: `src/jobintel_next/main.py` (immutato nel comportamento, ma usa registry aggiornato)
- Export script: `automation/export_greenhouse_jobs.py` usa nuovo collector
- CLI `jobintel-next export` usa nuovo collector

## Compatibilità output
L'output JSONL è mantenuto compatibile con il formato attuale:
- `source`, `source_org`, `external_id`, `url`, `title`, `company_name`, `location_raw`, `posted_at`, `language`, `raw_payload`

## Prossimo step suggerito
Step 2: consolidare config/command surface (un entrypoint ingest ufficiale + wrapper automation deprecati).

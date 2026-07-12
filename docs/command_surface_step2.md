# Command Surface - Step 2

## Comando ufficiale
Entrypoint ufficiale: `jobintel-next` (module `jobintel_next.cli`).

Command surface ufficiale:
- `jobintel-next ingest run --config <yaml> --out <jsonl>`
- `jobintel-next ingest export --source greenhouse --board <slug> --out <jsonl>`

## Config ufficiale
- **YAML è source of truth** per run strutturati (`ingest run`).
- Sezione attesa: `sources.*`.
- **Env vars sono solo override tecnici** (non business config):
  - `GREENHOUSE_TIMEOUT_SEC`
  - `GREENHOUSE_MAX_RETRIES`
  - `GREENHOUSE_MAX_CONCURRENCY`

## Cosa è legacy
- `python -m jobintel_next.main --config ... --out ...`
  - supportato come wrapper deprecato.
- `automation/export_greenhouse_jobs.py`
  - supportato come wrapper deprecato.

Questi path esistono per compatibilità, ma non sono più la command surface primaria.

## Esempi d'uso

Run da config YAML:
```bash
uv run jobintel-next ingest run --config config/generated/targets.yml --out data/all_jobs.jsonl
```

Export board singolo:
```bash
uv run jobintel-next ingest export --source greenhouse --board found --out data/found_jobs.jsonl
```

Override tecnico via env:
```bash
GREENHOUSE_TIMEOUT_SEC=30 GREENHOUSE_MAX_RETRIES=5 \
uv run jobintel-next ingest run --config config/default.yml --out data/jobs.jsonl
```

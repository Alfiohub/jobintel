# HTTP API Hardening Step 21

## Obiettivo
Rendere la HTTP API v1 più robusta e prevedibile come backend locale di prodotto.

## Miglioramenti implementati
- Response models Pydantic espliciti per tutti gli endpoint:
  - health
  - jobs list/count
  - packs list/run/count
- Separazione struttura FastAPI:
  - `app.py`: bootstrap + startup lifecycle
  - `router.py`: endpoint handlers
  - `schemas.py`: response schemas / tipi
  - `dependencies.py`: config dataset path + dependency injection
- Startup hardening:
  - risoluzione dataset path da override o env `JOBINTEL_INDEXED_INPUT`
  - validazione file dataset all'avvio (fail fast con errore chiaro)
- Error handling:
  - pack inesistente -> `404` con messaggio coerente
  - query param invalidi (es. `limit < 0`) -> `422` FastAPI validation
- Defaults/config:
  - dataset default: `data/jobs/jobs_indexed_en.jsonl`
  - paginazione default: `limit=20`, `offset=0`
  - sort default: `published_at_desc`

## Configurazione
- Override dataset via env:

```bash
export JOBINTEL_INDEXED_INPUT=data/jobs/jobs_indexed_en.jsonl
uv run uvicorn jobintel_next.app.api.app:app --reload
```

- Oppure in codice:

```python
from jobintel_next.app.api import create_app
app = create_app(input_path="data/jobs/jobs_indexed_en.jsonl")
```

## Error Cases Principali
- `GET /packs/{pack_name}` con pack non noto:
  - status: `404`
  - detail: `unknown query pack: ...`
- `GET /jobs` con parametri invalidi (es. `limit=-1`):
  - status: `422`
  - validation error standard FastAPI
- Startup con dataset path non valido:
  - `RuntimeError` in startup/lifespan (API non avviata)

## Test Aggiunti
- health endpoint
- jobs list con filtri + paginazione
- jobs count
- packs list
- pack run
- paginazione pack
- validazione params (`422`)
- pack inesistente (`404`)
- startup config da env
- startup failure su dataset path non valido

## Limiti noti
- scan locale JSONL in-memory (no DB index/persistenza)
- nessuna auth
- nessun ranking avanzato
- nessuna semantic search

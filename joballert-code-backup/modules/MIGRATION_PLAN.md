# Migration Plan (6 modules, 1 repo)

## Phase 0
- scaffolding moduli
- documentazione ownership

## Phase 1
- estrarre route API in package modulare
- mantenere legacy + `/v1/*`

## Phase 2
- spostare ingestion e intelligence runtime in moduli dedicati
- mantenere adapter backward-compatible

## Phase 3
- spostare pipeline NER/training in `ner-training`

## Phase 4
- separare frontend su contratti `/v1/*`

# Embedding Policy (Production)

## Obiettivo
Massimizzare qualità della ricerca semantica mantenendo costi e complessità sotto controllo.

## Decisione
- Default runtime: `semantic_provider=hash` (zero costo, sempre disponibile).
- Runtime premium: `semantic_provider=openai` su richieste semantiche reali (query utente).
- Batch indexing:
  - ambiente dev/test: `EMBEDDING_MODE=hash`
  - ambiente prod: `EMBEDDING_MODE=openai` solo se budget approvato e monitoraggio attivo.
- `gemini` resta provider secondario/fallback operativo.

## Regole pratiche
- Non chiamare provider esterno per filtri SQL standard.
- Chiamare provider esterno solo quando c'è `semantic_query`.
- Usare cache per evitare ricalcolo embeddings su contenuto già visto (`content_hash`).
- In caso di errore provider/API key: fallback automatico a `hash` lato prodotto.

## Soglie e guardrail
- Budget mensile embedding da definire prima del go-live.
- Alert se errore provider > 3% su finestra 1h.
- Alert se latenza semantic query > soglia target.

## Rollout consigliato
1. `hash` only in produzione (stabilità).
2. Attivazione `openai` per una quota di traffico semantico.
3. Confronto qualità/risultati e costi.
4. Estensione graduale se KPI migliorano.

## KPI per confermare la policy
- CTR sui risultati semantici.
- Conversione (click/apply) da query semantiche.
- Tempo medio risposta endpoint semantico.
- Costo per 1.000 query semantiche.

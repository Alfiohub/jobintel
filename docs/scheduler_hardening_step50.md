# Scheduler Hardening v1 (Step 50)

## Obiettivo
Rendere `alerts run-due` cron-safe e robusto in setup locale/produzione minima, evitando doppie esecuzioni concorrenti.

## Strategia lock adottata
Lock file per-user su filesystem:
- path: `data/alerts/runs/<user_id>/.run_due.lock`

Comportamento:
- il runner prova ad acquisire lock con creazione atomica (`O_CREAT|O_EXCL`)
- se lock già presente:
  - run non parte
  - nessun artifact JSON/MD viene scritto
  - viene restituito summary `status=skipped_locked`, `lock_acquired=false`
- a fine run normale il lock viene sempre rilasciato (`finally`)

Modulo: `src/jobintel_next/product/saved_searches/runner.py`

## Hardening operativo aggiunto
`run_due_saved_searches(...)` ora include metadata minimi:
- `started_at`
- `finished_at`
- `duration_seconds`
- `lock_acquired`
- `lock_path`
- `status` (`ok` | `skipped_locked`)

Scrittura artifact più sicura:
- write atomica (`*.tmp` + rename) per JSON e MD
- riduce rischio artifact mezzi scritti

## CLI `jobintel-next alerts run-due`
Comportamento aggiornato:
- lock acquisito: output summary completo, exit code `0`
- lock non acquisito (run concorrente): output esplicito, exit code `2`

Messaggio tipico su lock:
- `status=skipped_locked`
- `message=another run-due execution is already in progress`

## Esempio cron
```cron
0 * * * * cd /path/to/joballert2 && uv run jobintel-next alerts run-due --saved-db data/jobs/saved_searches.db --input data/jobs/jobs_indexed_en.jsonl --sqlite data/jobs/jobs_indexed_en.db --outdir data/alerts/runs --user-id local-user --user-email local@example.com
```

Suggerimento shell:
- monitorare exit code `2` come “skip lock” non distruttivo

## Exit codes
- `0`: run eseguito con successo (anche con `processed_error` interni gestiti in summary)
- `2`: lock già presente, run bloccato in modo pulito

## Test aggiunti
Nuovo file:
- `tests/product/test_scheduler_hardening_step50.py`

Coperture:
- lock acquisito e rilasciato correttamente
- secondo run bloccato con lock presente
- cleanup lock a fine run
- artifact/summary coerenti
- exit behavior CLI sensato (`2` su lock)

## Limiti noti
- nessun lock distribuito cross-host
- nessuna gestione stale-lock avanzata (TTL/heartbeat)
- nessuna queue/retry orchestration
- no scheduler distribuito in questo step

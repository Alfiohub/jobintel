# MVP Checklist (One Command)

Esegui dalla root progetto:

```bash
bash scripts/mvp_checklist.sh
```

Cosa controlla:
- presenza file critici MVP
- disponibilita `uv`
- lettura DB MVP (`data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite`)
- import Search API (`automation/microsaas/search_api.py`)

Se tutto OK stampa: `MVP checklist passed.`

# Title Coverage Recovery Batch v23-v25

## 1) Baseline iniziale
- baseline dataset: `data/jobs/jobs_titled_en_recovery_v22.jsonl`
- total rows: `81,011`
- `other`: `39,508` (`48.77%`)

## 2) Pass 1 — v23
- Nome: `Compliance / Risk Edge Expansion`
- Cluster: `compliance_risk`
- `other`: `39,508 -> 39,417`
- Delta: `-91`
- Nuove label: nessuna

## 3) Pass 2 — v24
- Nome: `Logistics Edge Expansion`
- Cluster: `logistics`
- `other`: `39,417 -> 39,388`
- Delta: `-29`
- Nuove label: nessuna

## 4) Pass 3 — v25
- Nome: `Education Edge Expansion`
- Cluster: `education`
- `other`: `39,388 -> 39,364`
- Delta: `-24`
- Nuove label: `school_counselor`, `school_administrator`

## 5) `other` totale prima/dopo batch
- Prima: `39,508` (`48.77%`)
- Dopo: `39,364` (`48.59%`)

## 6) Delta totale batch
- `-144`

## 7) Nuove label introdotte nel batch
- `school_counselor`
- `school_administrator`

## 8) Cluster più promettenti per batch successivo
1. `skilled_trades` residual con pattern forti non-IT (service/fleet/auto tech molto espliciti)
2. `compliance_risk` residual su micro-sottocluster ad alta precisione (KYC/compliance onboarding / internal audit edge)
3. `design_creative` residual con contesto forte non generico (`producer/editor` contestualizzati)

## 9) Cluster da evitare per ora
1. `general manager` / managerial generic
2. `business analyst` / `quantitative researcher`
3. generic engineering ambiguity (`principal engineer`, `manager, software engineering`)
4. generic `producer` senza contesto forte

## 10) File toccati
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- `docs/title_recovery_pass_v23/*`
- `docs/title_recovery_pass_v24/*`
- `docs/title_recovery_pass_v25/*`
- `data/jobs/jobs_titled_en_recovery_v23.jsonl`
- `data/jobs/jobs_titled_en_recovery_v24.jsonl`
- `data/jobs/jobs_titled_en_recovery_v25.jsonl`

## 11) Stato test
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`
- Result: `34 passed`

## Top residual other aggiornati (post-v25)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)
6. `social enterprise and program delivery-evergreen` (27)
7. `personal care specialist (part time)` (26)
8. `quantitative researcher` (24)
9. `business analyst` (20)
10. `sonder responder` (19)

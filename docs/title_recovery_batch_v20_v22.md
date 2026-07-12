# Title Coverage Recovery Batch v20-v22

## Baseline iniziale batch
- dataset baseline: `data/jobs/jobs_titled_en_recovery_v19.jsonl`
- rows total: `81,011`
- `other`: `39,892` (`49.24%`)

## Pass 1 (v20)
- Nome: `Skilled Trades Explicit Technician Expansion`
- Cluster: `skilled_trades`
- `other`: `39,892 -> 39,805` (delta `-87`)
- Nuove label: nessuna

## Pass 2 (v21)
- Nome: `Design / Creative Precision Expansion`
- Cluster: `design_creative`
- `other`: `39,805 -> 39,670` (delta `-135`)
- Nuove label: `journalist`, `ux_researcher`, `art_director`, `creative_director`

## Pass 3 (v22)
- Nome: `Healthcare Support Technician Precision`
- Cluster: `healthcare_clinical`
- `other`: `39,670 -> 39,508` (delta `-162`)
- Nuove label: `certified_nursing_assistant`, `pharmacy_technician`, `patient_care_technician`

## Totale batch
- `other` prima batch: `39,892` (`49.24%`)
- `other` dopo batch: `39,508` (`48.77%`)
- Delta totale batch: `-384`

## Nuove label introdotte nel batch
- `journalist`
- `ux_researcher`
- `art_director`
- `creative_director`
- `certified_nursing_assistant`
- `pharmacy_technician`
- `patient_care_technician`

## Top residual other aggiornati (post-v22)
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

## Cluster più promettenti per batch successivo
1. `skilled_trades` residual (sottocluster stretti: service/field technician non-IT, automotive-specific variants)
2. `design_creative` residual (producer/editor contestuali non generici)
3. `compliance_risk` residual (payroll risk/compliance e product compliance patterns stretti)

## Cluster da evitare per ora
1. generic managerial/program titles (`general manager`, `program evergreen`)
2. generic analytics ambiguity (`business analyst`, `quantitative researcher`)
3. generic engineering ambiguity (`principal engineer`, `manager, software engineering`) senza contesto forte

## File toccati
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- `docs/title_recovery_pass_v20/*`
- `docs/title_recovery_pass_v21/*`
- `docs/title_recovery_pass_v22/*`
- `data/jobs/jobs_titled_en_recovery_v20.jsonl`
- `data/jobs/jobs_titled_en_recovery_v21.jsonl`
- `data/jobs/jobs_titled_en_recovery_v22.jsonl`

## Stato test
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`
- Result: `34 passed`

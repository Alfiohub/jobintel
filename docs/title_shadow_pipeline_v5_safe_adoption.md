# Shadow Pipeline v5 — Next Safe Adoption Batch

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v50_safe.jsonl`
- total rows: `81,011`
- other baseline: `36,281`
- status: `ok`

## B. Candidate review
- `enterprise_architect_cluster` -> `solutions_architect/architecture` -> `promote_safe` | pattern nominale forte su `enterprise architect`, basso rischio semantico.
- `fullstack_developer_cluster` -> `software_engineer/software_engineering` -> `promote_safe` | pattern tecnico esplicito e confinato su `fullstack developer`.
- `budtender_cluster` -> `store_associate/sales` -> `promote_safe` | cluster retail/cannabis molto uniforme e disambiguato.
- `sales_operations_analyst_cluster` -> `data_analyst or operations_specialist` -> `reject_for_now` | ambiguità di family target.
- `implementation_engineer_cluster` -> `n/a` -> `reject_for_now` | ancora ambiguo cross-domain.
- `client_partner_cluster` -> `n/a` -> `reject_for_now` | titolo troppo trasversale.
- `business_analyst_cluster` -> `n/a` -> `reject_for_now` | cluster storico ambiguo.
- `producer_naked_cluster` -> `n/a` -> `reject_for_now` | `producer` nudo non disambiguato.

## C. Safe batch selected
1. `enterprise_architect_cluster`
   - target label: `solutions_architect`
   - target role family: `architecture`
   - why selected: volume solido e pattern leggibile (`enterprise architect` variants)
   - risk level: `low`
2. `fullstack_developer_cluster`
   - target label: `software_engineer`
   - target role family: `software_engineering`
   - why selected: forma tecnica specifica non generica
   - risk level: `low`
3. `budtender_cluster`
   - target label: `store_associate`
   - target role family: `sales`
   - why selected: cluster residuale molto uniforme (`budtender` variants)
   - risk level: `low`

## D. Changes implemented
- files modified:
  - `src/jobintel_next/pipelines/titles/rules.py`
  - `tests/pipelines/test_titles_stage_step12.py`
- rules added:
  - `arch_enterprise_architect_core_safe_v5`
  - `eng_fullstack_developer_core_safe_v5`
  - `retail_budtender_core_safe_v5`
- taxonomy changes: none
- new labels introduced: none

## E. Test results
- executed:
  - `tests/pipelines/test_titles_stage_step12.py`
  - `tests/pipelines/test_titles_eval_step13.py`
  - `tests/test_cli_titles_step12.py`
- result: `64 passed`

## F. Eval results
- output dataset: `data/jobs/jobs_titled_en_recovery_v51_safe.jsonl`
- eval artifacts: `docs/title_recovery_pass_v51_safe/*`
- other before: `36,281`
- other after: `36,197`
- delta absolute: `-84`
- delta percent: `-0.23%`
- sample titoli coperti:
  - `Principal Enterprise Architect` (9), `Enterprise Architect` (4)
  - `Fullstack Developer` (11), `Senior Fullstack Developer, Developer Productivity (Backstage)` (2)
  - `Budtender PT` (13), `Budtender Part Time` (5)

## G. Recommendation
- `adopt_safe_batch_and_continue_shadow`
- rationale: batch corto, guardrail stretti, regole leggibili e miglioramento netto senza overmatch evidente.

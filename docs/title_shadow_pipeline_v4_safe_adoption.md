# Shadow Pipeline v4 — Next Safe Adoption Batch

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v49_safe.jsonl`
- total rows: `81,011`
- other baseline: `36,528`
- status: `ok`

## B. Candidate review
- `insurance_agent_geo_cluster` -> `account_executive/sales` -> `promote_safe` | Pattern molto uniforme (`Insurance Agent - city, state`) e semanticamente sales.
- `hr_generalist_cluster` -> `hr_generalist/people_operations` -> `promote_safe` | Pattern chiaro su `HR/Human Resources Generalist`.
- `speech_language_pathologist_cluster` -> `speech_language_pathologist/healthcare_clinical` -> `promote_safe` | Pattern clinico esplicito e poco ambiguo.
- `sales_operations_analyst_cluster` -> `data_analyst|operations_specialist` -> `reject_for_now` | Ambiguità funzionale (analytics vs ops).
- `restaurant_manager_cluster` -> `operations_specialist` -> `reject_for_now` | Rischio overmatch manageriale.
- `office_manager_cluster` -> `operations_specialist` -> `reject_for_now` | Titolo troppo trasversale.
- `business_analyst_cluster` -> `n/a` -> `reject_for_now` | cluster storico ambiguo.
- `producer_naked_cluster` -> `n/a` -> `reject_for_now` | `producer` nudo resta ambiguo.

## C. Safe batch selected
1. `insurance_agent_geo_cluster`
   - target label: `account_executive`
   - target family: `sales`
   - why: volume alto e forma ripetitiva forte
   - risk: `low`
2. `hr_generalist_cluster`
   - target label: `hr_generalist`
   - target family: `people_operations`
   - why: pattern nominale diretto e leggibile
   - risk: `low`
3. `speech_language_pathologist_cluster`
   - target label: `speech_language_pathologist`
   - target family: `healthcare_clinical`
   - why: nomenclatura clinica molto chiara
   - risk: `low`

## D. Changes implemented
- files modified:
  - `src/jobintel_next/pipelines/titles/rules.py`
  - `src/jobintel_next/pipelines/titles/taxonomy.py`
  - `tests/pipelines/test_titles_stage_step12.py`
- rules added:
  - `sales_insurance_agent_geo_core_safe_v4`
  - `people_hr_generalist_core_safe_v4`
  - `health_speech_language_pathologist_core_safe_v4`
- new labels introduced:
  - `hr_generalist` -> `people_operations`
  - `speech_language_pathologist` -> `healthcare_clinical`

## E. Test results
- executed:
  - `tests/pipelines/test_titles_stage_step12.py`
  - `tests/pipelines/test_titles_eval_step13.py`
  - `tests/test_cli_titles_step12.py`
- result: `61 passed`

## F. Eval results
- output dataset: `data/jobs/jobs_titled_en_recovery_v50_safe.jsonl`
- eval artifacts: `docs/title_recovery_pass_v50_safe/*`
- other before: `36,528`
- other after: `36,281`
- delta absolute: `-247`
- delta percent: `-0.68%`
- sample covered titles:
  - `Insurance Agent - San Antonio, TX` (3), `Insurance Agent` (2)
  - `HR Generalist` (13), `Human Resources Generalist` (5)
  - `Virtual Speech Language Pathologist (SLP)` (12), `Speech Language Pathologist` (9)

## G. Recommendation
- `adopt_safe_batch_and_continue_shadow`
- rationale: batch corto, pattern chiari, rischio basso, delta consistente.

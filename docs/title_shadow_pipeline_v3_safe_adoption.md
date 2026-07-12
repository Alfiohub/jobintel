# Shadow Pipeline v3 — Next Safe Adoption Batch

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v48_safe.jsonl`
- total rows: `81,011`
- other baseline: `36,629`
- status: `ok`

## B. Candidate review
- `client_success_manager_cluster` -> `customer_success_manager/customer_success` -> `promote_safe` | Pattern molto chiaro e specifico su client success.
- `devsecops_engineer_cluster` -> `devops_engineer/devops` -> `promote_safe` | Variante engineering ben disambiguata.
- `data_architect_cluster` -> `solutions_architect/architecture` -> `promote_with_tighter_rule` | Buon volume ma va tenuta forma core stretta.
- `hr_generalist_cluster` -> `hr_generalist/people_operations` -> `reject_for_now` | Richiederebbe nuova label e perimetro people da allargare.
- `chief_of_staff_cluster` -> `chief_of_staff/operations` -> `reject_for_now` | Semantica ampia e cross-domain.
- `payroll_specialist_cluster` -> `finance/compliance?` -> `reject_for_now` | Ambiguità finance/compliance/ops.
- `support_engineer_it_core` -> `it_support_specialist/it_operations` -> `reject_for_now` | Già promosso nel v2 safe.

## C. Safe batch selected
1. `client_success_manager_cluster`
   - target: `customer_success_manager`
   - family: `customer_success`
   - reason: varianti uniformi (`Client Success Manager`, `Senior ...`)
   - risk: `low`
2. `devsecops_engineer_cluster`
   - target: `devops_engineer`
   - family: `devops`
   - reason: pattern tecnico specifico (`DevSecOps Engineer`)
   - risk: `low`
3. `data_architect_cluster`
   - target: `solutions_architect`
   - family: `architecture`
   - reason: cluster consistente, regola stretta su forma core
   - risk: `medium-low`

## D. Changes implemented
- files modified:
  - `src/jobintel_next/pipelines/titles/rules.py`
  - `tests/pipelines/test_titles_stage_step12.py`
- rules added:
  - `csm_client_success_manager_core_safe_v3`
  - `eng_devsecops_engineer_core_safe_v3`
  - `arch_data_architect_core_safe_v3`
- taxonomy changes: none
- new labels introduced: none

## E. Test results
- executed:
  - `tests/pipelines/test_titles_stage_step12.py`
  - `tests/pipelines/test_titles_eval_step13.py`
  - `tests/test_cli_titles_step12.py`
- result: `58 passed`

## F. Eval results
- output dataset: `data/jobs/jobs_titled_en_recovery_v49_safe.jsonl`
- eval artifacts: `docs/title_recovery_pass_v49_safe/*`
- other before: `36,629`
- other after: `36,528`
- delta absolute: `-101`
- delta percent: `-0.28%`
- sample covered titles:
  - `Client Success Manager` (13), `Senior Client Success Manager - Strategic Accounts` (4)
  - `DevSecOps Engineer` (14), `Senior DevSecOps Engineer` (3)
  - `Data Architect` (12), `Senior Data Architect` (7)

## G. Recommendation
- `adopt_safe_batch_and_continue_shadow`
- rationale: delta buono con 3 cluster puliti, nessuna nuova label, regole leggibili e testate.

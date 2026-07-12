# Shadow Pipeline v2 — Safe Adoption Batch

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v46.jsonl`
- total rows: `81,011`
- other baseline: `36788`
- status: `ok`

## B. Shadow v1 review
- `support_engineer_it_core` | target `it_support_specialist/it_operations` | verdict `promote_with_tighter_rule` | High volume, but tightened with strict exclusions for customer/product/manager tokens.
- `paralegal_specialty_cluster` | target `paralegal/legal` | verdict `reject_for_now` | Shadow pattern was broad (\bparalegal\b); too wide for safe auto-adoption.
- `occupational_therapist_core` | target `occupational_therapist/healthcare_clinical` | verdict `promote_safe` | Very explicit clinical title family, low ambiguity.
- `respiratory_therapist_core` | target `respiratory_therapist/healthcare_clinical` | verdict `promote_safe` | Very explicit clinical title family, low ambiguity.
- `business_analyst_cluster` | target `n/a` | verdict `reject_for_now` | Historically ambiguous generic analyst bucket.
- `producer_naked_cluster` | target `n/a` | verdict `reject_for_now` | Naked producer remains ambiguous across domains.

## C. Safe batch selected
- `support_engineer_it_core` -> `it_support_specialist` / `it_operations` | selected with tighter rule and explicit negative guards | risk `medium-low`
- `occupational_therapist_core` -> `occupational_therapist` / `healthcare_clinical` | explicit clinical title | risk `low`
- `respiratory_therapist_core` -> `respiratory_therapist` / `healthcare_clinical` | explicit clinical title | risk `low`

## D. Changes implemented
- Updated files:
  - `src/jobintel_next/pipelines/titles/rules.py`
  - `src/jobintel_next/pipelines/titles/taxonomy.py`
  - `tests/pipelines/test_titles_stage_step12.py`
- New/updated rules:
  - `it_support_engineer_core_safe_v2` (tight support-engineer variants + exclusions)
  - `health_occupational_therapist_core_v2`
  - `health_respiratory_therapist_core_v2`
- New labels introduced:
  - `occupational_therapist` -> `healthcare_clinical`
  - `respiratory_therapist` -> `healthcare_clinical`

## E. Test results
- executed:
  - `tests/pipelines/test_titles_stage_step12.py`
  - `tests/pipelines/test_titles_eval_step13.py`
  - `tests/test_cli_titles_step12.py`
- result: `55 passed`

## F. Eval results
- other before: `36788`
- other after: `36629`
- delta absolute: `-159`
- delta percent: `-0.43%`
- sample covered titles:
  - `Support Engineer` (11), `Senior Support Engineer` (9), `Production Support Engineer` (5)
  - `Occupational Therapist` (14), `Contracted In-Home Occupational Therapist` (12), `Pediatric Occupational Therapist` (8)
  - `Respiratory Therapist - Registered` (13), `Respiratory Therapist - Registered - Float Pool` (3)

## G. Recommendation
- `adopt_safe_batch_and_continue_shadow`
- Reason: batch delivered meaningful delta with conservative readable rules; continue using shadow discovery for prioritization, then promote only tightened low-risk clusters.
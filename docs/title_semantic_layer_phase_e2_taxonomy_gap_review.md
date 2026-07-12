# Fase E.2 — Taxonomy Gap Review mirata

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
- total rows: `81011`
- other baseline: `36092`
- status: `ok`

## B. Taxonomy gap inventory
1. `engineer` | reps: Principal Engineer (16); Senior Engineer (10); Staff Engineer (7) | current internal `ml_engineer/machine_learning` (0.828) | issue `too_generic` | Naked `engineer` is historically high-risk and not suitable for safe promotion.
2. `production_engineer` | reps: Production Engineer (10); Senior Product Engineer (9); Product Engineer (8) | current internal `manufacturing_engineer/industrial_engineering` (0.9054) | issue `internal_candidate_incoherent` | Current internal suggestion (`sales_engineer`) is off-domain; industrial/manufacturing family is closer.
3. `designer` | reps: Designer (11); Senior Designer (8); Designer II (6) | current internal `product_designer/design` (0.828) | issue `too_generic` | Naked `designer` remains too broad (product, visual, motion, industrial, etc.).
4. `data_science_manager` | reps: Data Science Manager (16) | current internal `data_science_manager/data_science` (1.0) | issue `missing_managerial_label` | Internal candidate (`story_editor`) is clearly wrong; recurring managerial DS titles indicate taxonomy gap.
5. `onboarding_specialist` | reps: Onboarding Specialist (13) | current internal `marketing_specialist/marketing` (0.7081) | issue `cross_domain_title` | Onboarding spans customer success, compliance, operations, and HR; title-only mapping is unstable.
6. `procurement_manager` | reps: Procurement Manager (13) | current internal `product_manager/product_management` (0.6401) | issue `taxonomy_granularity_gap` | Recurring procurement management titles are real but currently forced into unrelated labels.
7. `fpga_engineer` | reps: FPGA Engineer (11) | current internal `electrical_engineer/industrial_engineering` (1.0) | issue `internal_candidate_incoherent` | FPGA role is hardware/electrical oriented; current `ml_engineer` suggestion is weak.
8. `software_development_manager` | reps: Software Development Manager (10) | current internal `engineering_manager/software_engineering` (1.0) | issue `existing_label_not_retrieved` | Canonical `engineering_manager` already exists and is semantically aligned.
9. `sales_representative` | reps: Sales Representative (10) | current internal `business_development_representative/sales` (0.768) | issue `core_sales_label_missing` | High-frequency generic sales title lacks a clean canonical destination without forcing BDR/AE.
10. `operations_analyst` | reps: Operations Analyst (10) | current internal `data_analyst/data_analytics` (0.8173) | issue `analytics_vs_operations_overlap` | Can map to data analytics, finance ops, biz ops depending on context not present in title.
11. `technical_architect` | reps: Technical Architect (8) | current internal `solutions_architect/architecture` (1.0) | issue `existing_label_not_retrieved` | Current internal suggestion is misaligned (`technical_recruiter`); architecture label exists.
12. `it_administrator` | reps: IT Administrator (7) | current internal `it_support_specialist/it_operations` (1.0) | issue `existing_label_not_retrieved` | Current `school_administrator` retrieval is noisy; IT admin maps better to IT operations.

## C. Taxonomy decision table
1. `engineer` | decision `keep_other_by_policy` | target `n/a` | confidence `high` | rationale: Naked `engineer` is historically high-risk and not suitable for safe promotion.
2. `production_engineer` | decision `map_to_existing_label` | target `manufacturing_engineer/industrial_engineering` | confidence `medium` | rationale: Current internal suggestion (`sales_engineer`) is off-domain; industrial/manufacturing family is closer.
3. `designer` | decision `keep_other_by_policy` | target `n/a` | confidence `high` | rationale: Naked `designer` remains too broad (product, visual, motion, industrial, etc.).
4. `data_science_manager` | decision `new_label_worth_adding` | target `data_science_manager/data_science` | confidence `medium` | rationale: Internal candidate (`story_editor`) is clearly wrong; recurring managerial DS titles indicate taxonomy gap.
5. `onboarding_specialist` | decision `needs_context_not_title_only` | target `n/a` | confidence `medium` | rationale: Onboarding spans customer success, compliance, operations, and HR; title-only mapping is unstable.
6. `procurement_manager` | decision `taxonomy_merge_or_cleanup_needed` | target `procurement_manager/logistics` | confidence `medium` | rationale: Recurring procurement management titles are real but currently forced into unrelated labels.
7. `fpga_engineer` | decision `map_to_existing_label` | target `electrical_engineer/industrial_engineering` | confidence `medium` | rationale: FPGA role is hardware/electrical oriented; current `ml_engineer` suggestion is weak.
8. `software_development_manager` | decision `map_to_existing_label` | target `engineering_manager/software_engineering` | confidence `high` | rationale: Canonical `engineering_manager` already exists and is semantically aligned.
9. `sales_representative` | decision `taxonomy_merge_or_cleanup_needed` | target `sales_representative/sales` | confidence `medium` | rationale: High-frequency generic sales title lacks a clean canonical destination without forcing BDR/AE.
10. `operations_analyst` | decision `needs_context_not_title_only` | target `n/a` | confidence `medium` | rationale: Can map to data analytics, finance ops, biz ops depending on context not present in title.
11. `technical_architect` | decision `map_to_existing_label` | target `solutions_architect/architecture` | confidence `medium` | rationale: Current internal suggestion is misaligned (`technical_recruiter`); architecture label exists.
12. `it_administrator` | decision `map_to_existing_label` | target `it_support_specialist/it_operations` | confidence `medium` | rationale: Current `school_administrator` retrieval is noisy; IT admin maps better to IT operations.

## D. Priority shortlist (max 10)
1. `software_development_manager` | action `map_to_existing_label` | expected value `high` | risk `low` | why now: High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing.
2. `production_engineer` | action `map_to_existing_label` | expected value `high` | risk `low` | why now: High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing.
3. `fpga_engineer` | action `map_to_existing_label` | expected value `high` | risk `low` | why now: High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing.
4. `it_administrator` | action `map_to_existing_label` | expected value `low` | risk `low` | why now: Material ambiguity currently blocks safe promotion and keeps semantic reviewer conservative.
5. `technical_architect` | action `map_to_existing_label` | expected value `low` | risk `low` | why now: Material ambiguity currently blocks safe promotion and keeps semantic reviewer conservative.
6. `data_science_manager` | action `new_label_worth_adding` | expected value `medium` | risk `medium` | why now: Material ambiguity currently blocks safe promotion and keeps semantic reviewer conservative.
7. `sales_representative` | action `taxonomy_merge_or_cleanup_needed` | expected value `high` | risk `medium` | why now: High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing.
8. `procurement_manager` | action `taxonomy_merge_or_cleanup_needed` | expected value `high` | risk `medium` | why now: High-volume cluster with wrong current internal target; fixing taxonomy decision improves future semantic routing.
9. `onboarding_specialist` | action `needs_context_not_title_only` | expected value `medium` | risk `medium` | why now: Material ambiguity currently blocks safe promotion and keeps semantic reviewer conservative.

## E. Taxonomy review summary
- true taxonomy gaps: `3`
- title-only ambiguity: `2`
- keep_other_by_policy: `2`
- resolvable with existing labels: `5`
- decision counts: `{'map_to_existing_label': 5, 'new_label_worth_adding': 1, 'keep_other_by_policy': 2, 'needs_context_not_title_only': 2, 'taxonomy_merge_or_cleanup_needed': 2}`

## F. Final recommendation
- `keep_taxonomy_stable_and_accept_residual`
- reason: Gaps are mostly ambiguous or low-value; taxonomy expansion would add noise.

# Phase E — Semantic Layer Bootstrap Report

## 1. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v54_semantic_patch.jsonl`
- total rows: `81011`
- other baseline: `36015`
- status: `mismatch`

## 2. Semantic layer bootstrap summary
- internal canonical titles: `83`
- ESCO rows indexed: `3043`
- O*NET rows indexed: `1016`
- embedding approach: `hashed_char_trigram_cosine`
- fallback note: `sentence-transformers not configured in this environment; using deterministic local semantic-lite vectors`

## 3. Retrieval quality sample (30)
1. `General Manager` (40) | internal: `financial_analyst` 0.5538 | ESCO: `gambling manager` 1.0 | O*NET: `General and Operations Managers` 0.9049 | action: `keep_other_for_now`
2. `Senior Market Strategy and Partnerships Manager` (36) | internal: `sales_manager` 0.4681 | ESCO: `political campaign officer` 0.5825 | O*NET: `Marketing Managers` 0.5433 | action: `keep_other_for_now`
3. `Hair Color Bar Assistant, Licensed Cosmetologist` (32) | internal: `medical_assistant` 0.4384 | ESCO: `meteorology technician` 0.5504 | O*NET: `Hairdressers, Hairstylists, and Cosmetologists` 0.683 | action: `keep_other_for_now`
4. `General Application` (31) | internal: `hr_generalist` 0.4206 | ESCO: `ICT application developer` 0.6836 | O*NET: `Training and Development Specialists` 0.6606 | action: `noise_or_non_role`
5. `Producer` (27) | internal: `content_producer` 1.0 | ESCO: `producer` 1.0 | O*NET: `Producers and Directors` 1.0 | action: `keep_other_for_now`
6. `Social Enterprise and Program Delivery-Evergreen` (27) | internal: `delivery_driver` 0.4118 | ESCO: `social entrepreneur` 0.5114 | O*NET: `Driver/Sales Workers` 0.4731 | action: `keep_other_for_now`
7. `Personal Care Specialist (Part Time)` (26) | internal: `store_associate` 0.5228 | ESCO: `hairdresser` 0.6208 | O*NET: `Computer User Support Specialists` 0.6719 | action: `keep_other_for_now`
8. `Quantitative Researcher` (24) | internal: `ux_researcher` 0.5757 | ESCO: `financial trader` 0.6845 | O*NET: `Financial Quantitative Analysts` 1.0 | action: `keep_other_for_now`
9. `Business Analyst` (20) | internal: `data_analyst` 0.536 | ESCO: `business economics researcher` 1.0 | O*NET: `Management Analysts` 1.0 | action: `keep_other_for_now`
10. `Restaurant General Manager` (19) | internal: `hr_generalist` 0.4776 | ESCO: `accommodation manager` 0.7892 | O*NET: `Food Service Managers` 0.8558 | action: `keep_other_for_now`
11. `Sonder Responder` (19) | internal: `respiratory_therapist` 0.3036 | ESCO: `mineral processing operator` 0.6768 | O*NET: `Paramedics` 0.7888 | action: `keep_other_for_now`
12. `Manager, Software Engineering` (18) | internal: `engineering_manager` 0.9411 | ESCO: `software developer` 0.7694 | O*NET: `Software Developers` 0.7694 | action: `needs_tighter_rule`
13. `Cultivation Associate` (18) | internal: `operations_specialist` 0.4029 | ESCO: `hop farmer` 0.6415 | O*NET: `Agricultural Equipment Operators` 0.7746 | action: `keep_other_for_now`
14. `Leader in Training` (17) | internal: `engineering_manager` 0.4068 | ESCO: `educational counsellor` 0.5646 | O*NET: `General and Operations Managers` 0.5646 | action: `keep_other_for_now`
15. `Data Science Manager` (16) | internal: `data_science_manager` 1.0 | ESCO: `database administrator` 0.7065 | O*NET: `Managers, All Other` 0.7273 | action: `needs_tighter_rule`
16. `Principal Engineer` (16) | internal: `ml_engineer` 0.8528 | ESCO: `ship assistant engineer` 1.0 | O*NET: `Logistics Engineers` 1.0 | action: `needs_tighter_rule`
17. `Intelligence Operations Integrator` (16) | internal: `operations_specialist` 0.4827 | ESCO: `intelligence communications interceptor` 0.6976 | O*NET: `Military Officer Special and Tactical Operations Leaders, All Other` 0.8304 | action: `keep_other_for_now`
18. `Senior Firmware Engineer` (15) | internal: `software_engineer` 0.7739 | ESCO: `fire protection technician` 0.8182 | O*NET: `Blockchain Engineers` 1.0 | action: `needs_tighter_rule`
19. `Senior Technical Enablement Architect` (15) | internal: `solutions_architect` 0.7636 | ESCO: `naval architect` 0.5585 | O*NET: `Computer Systems Engineers/Architects` 0.7636 | action: `needs_tighter_rule`
20. `Manager, Paid Social` (15) | internal: `marketing_specialist` 0.5236 | ESCO: `social services manager` 0.661 | O*NET: `Public Relations Managers` 0.6522 | action: `keep_other_for_now`
21. `Restaurant Manager` (14) | internal: `financial_analyst` 0.5853 | ESCO: `accommodation manager` 1.0 | O*NET: `Food Service Managers` 1.0 | action: `keep_other_for_now`
22. `Chief of Staff` (14) | internal: `compliance_manager` 0.2638 | ESCO: `public administration manager` 1.0 | O*NET: `Chief Executives` 0.7351 | action: `keep_other_for_now`
23. `Office Manager` (13) | internal: `school_administrator` 0.7971 | ESCO: `office manager` 1.0 | O*NET: `General and Operations Managers` 1.0 | action: `keep_other_for_now`
24. `Onboarding Specialist` (13) | internal: `marketing_specialist` 0.7081 | ESCO: `specialist nurse` 0.7478 | O*NET: `Medical Records Specialists` 0.8025 | action: `semantic_layer_candidate`
25. `Sales Enablement Manager` (13) | internal: `sales_manager` 0.6886 | ESCO: `sales account manager` 0.7185 | O*NET: `First-Line Supervisors of Retail Sales Workers` 0.6958 | action: `semantic_layer_candidate`
26. `Implementation Engineer` (13) | internal: `operations_specialist` 0.6441 | ESCO: `instrumentation engineer` 0.7732 | O*NET: `Bioengineers and Biomedical Engineers` 0.8292 | action: `keep_other_for_now`
27. `Procurement Manager` (13) | internal: `product_manager` 0.6401 | ESCO: `energy manager` 0.8429 | O*NET: `Purchasing Managers` 1.0 | action: `semantic_layer_candidate`
28. `Machine Learning Researcher` (13) | internal: `ml_engineer` 0.6368 | ESCO: `research engineer` 0.6507 | O*NET: `Computer and Information Research Scientists` 0.8247 | action: `keep_other_for_now`
29. `Client Partner` (13) | internal: `customer_service_specialist` 0.5185 | ESCO: `client relations manager` 0.5827 | O*NET: `Accountants and Auditors` 0.6684 | action: `keep_other_for_now`
30. `Production Lead` (12) | internal: `manufacturing_engineer` 0.6876 | ESCO: `set buyer` 0.7619 | O*NET: `Production, Planning, and Expediting Clerks` 1.0 | action: `semantic_layer_candidate`

## 4. Residual category split
- `keep_other_for_now`: `1919`
- `needs_tighter_rule`: `467`
- `semantic_layer_candidate`: `401`
- `taxonomy_gap`: `111`
- `noise_or_non_role`: `79`
- `safe_rule_candidate`: `18`

## 5. Top opportunities
- `Manager, Software Engineering` | vol `18` | target `engineering_manager/software_engineering` | risk `low` | action `needs_tighter_rule`
- `Data Science Manager` | vol `16` | target `data_science_manager/data_science` | risk `low` | action `needs_tighter_rule`
- `Principal Engineer` | vol `16` | target `ml_engineer/machine_learning` | risk `low` | action `needs_tighter_rule`
- `Senior Firmware Engineer` | vol `15` | target `software_engineer/software_engineering` | risk `medium` | action `needs_tighter_rule`
- `Senior Technical Enablement Architect` | vol `15` | target `solutions_architect/architecture` | risk `low` | action `needs_tighter_rule`
- `Product Support Specialist` | vol `11` | target `it_support_specialist/it_operations` | risk `low` | action `needs_tighter_rule`
- `Designer` | vol `11` | target `product_designer/design` | risk `low` | action `needs_tighter_rule`
- `Territory Manager` | vol `11` | target `account_manager/sales` | risk `medium` | action `needs_tighter_rule`
- `Sales Director` | vol `11` | target `sales_manager/sales` | risk `low` | action `needs_tighter_rule`
- `Senior Salesforce Administrator` | vol `10` | target `it_support_specialist/it_operations` | risk `low` | action `safe_rule_candidate`
- `Manager, Business Development` | vol `10` | target `account_manager/sales` | risk `low` | action `needs_tighter_rule`
- `Senior Manager, Engineering` | vol `10` | target `engineering_manager/software_engineering` | risk `low` | action `needs_tighter_rule`

## 6. Top failure modes
- `General Manager` | vol `40` | reason `keep_other_for_now` | risk `high`
- `Senior Market Strategy and Partnerships Manager` | vol `36` | reason `keep_other_for_now` | risk `medium`
- `Hair Color Bar Assistant, Licensed Cosmetologist` | vol `32` | reason `keep_other_for_now` | risk `medium`
- `General Application` | vol `31` | reason `noise_or_non_role` | risk `high`
- `Producer` | vol `27` | reason `keep_other_for_now` | risk `high`
- `Social Enterprise and Program Delivery-Evergreen` | vol `27` | reason `keep_other_for_now` | risk `medium`
- `Personal Care Specialist (Part Time)` | vol `26` | reason `keep_other_for_now` | risk `medium`
- `Quantitative Researcher` | vol `24` | reason `keep_other_for_now` | risk `high`
- `Business Analyst` | vol `20` | reason `keep_other_for_now` | risk `high`
- `Restaurant General Manager` | vol `19` | reason `keep_other_for_now` | risk `high`
- `Sonder Responder` | vol `19` | reason `keep_other_for_now` | risk `medium`
- `Cultivation Associate` | vol `18` | reason `keep_other_for_now` | risk `medium`

## 7. Recommendation
- `semantic_layer_useful_only_as_reviewer`
- rationale: The residual has many high-ambiguity manager/analyst/partner titles; semantic retrieval improves triage and candidate ranking, but confidence is insufficient for direct auto-adoption without tighter human-in-the-loop review.

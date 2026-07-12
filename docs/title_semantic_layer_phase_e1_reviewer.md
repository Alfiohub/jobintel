# Fase E.1 — Reviewer-Driven Safe Batch Generation

## A. Baseline confirmation
- repo: `joballert2`
- dataset: `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
- total rows: `81011`
- other baseline: `36092`
- status: `ok`

## B. Semantic reviewer summary
- cluster reviewati: `113`
- convergenza alta: `80`
- cluster con conflitto: `15`
- cluster keep_other: `14`

## C. Reviewer table (top 30)
1. `engineer` | reps: Principal Engineer (16); Senior Engineer (10); Staff Engineer (7) | internal `ml_engineer` 0.828 | ESCO `ship assistant engineer` 1.0 | O*NET `Logistics Engineers` 1.0 | conf `high` | risk `high` | verdict `keep_other_for_now`
2. `production_engineer` | reps: Production Engineer (10); Senior Product Engineer (9); Product Engineer (8) | internal `manufacturing_engineer` 0.9054 | ESCO `maintenance and repair engineer` 1.0 | O*NET `Industrial Engineers` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
3. `manager_software_engineering` | reps: Manager, Software Engineering (18); Senior Manager, Software Engineering (8) | internal `engineering_manager` 0.9365 | ESCO `software developer` 0.7578 | O*NET `Software Developers` 0.7578 | conf `high` | risk `low` | verdict `promote_safe`
4. `designer` | reps: Designer (11); Senior Designer (8); Designer II (6) | internal `product_designer` 0.828 | ESCO `art director` 1.0 | O*NET `Video Game Designers` 1.0 | conf `high` | risk `high` | verdict `keep_other_for_now`
5. `firmware_engineer` | reps: Senior Firmware Engineer (15); Firmware Engineer (10) | internal `software_engineer` 0.7739 | ESCO `fire protection technician` 0.8182 | O*NET `Blockchain Engineers` 1.0 | conf `high` | risk `medium` | verdict `promote_with_tighter_rule`
6. `production` | reps: Production Lead (12); Production Associate (8) | internal `manufacturing_engineer` 0.7118 | ESCO `set buyer` 0.7619 | O*NET `Production, Planning, and Expediting Clerks` 1.0 | conf `high` | risk `high` | verdict `keep_other_for_now`
7. `sales_director` | reps: Sales Director (11); Director, Sales (8) | internal `sales_manager` 0.8099 | ESCO `sales manager` 0.9421 | O*NET `Sales Managers` 0.9421 | conf `high` | risk `low` | verdict `promote_safe`
8. `manager_engineering` | reps: Senior Manager, Engineering (10); Manager, Engineering (8) | internal `engineering_manager` 0.909 | ESCO `foundry manager` 0.909 | O*NET `Architectural and Engineering Managers` 0.8281 | conf `high` | risk `low` | verdict `promote_safe`
9. `data_science_manager` | reps: Data Science Manager (16) | internal `data_science_manager` 1.0 | ESCO `database administrator` 0.7065 | O*NET `Managers, All Other` 0.7273 | conf `high` | risk `low` | verdict `promote_with_tighter_rule`
10. `fp_a_analyst` | reps: FP&A Analyst (8); Senior FP&A Analyst (8) | internal `data_analyst` 0.685 | ESCO `mergers and acquisitions analyst` 0.8551 | O*NET `Cost Estimators` 0.7205 | conf `high` | risk `medium` | verdict `promote_with_tighter_rule`
11. `technical_enablement_architect` | reps: Senior Technical Enablement Architect (15) | internal `solutions_architect` 0.7636 | ESCO `naval architect` 0.5585 | O*NET `Computer Systems Engineers/Architects` 0.7636 | conf `medium` | risk `low` | verdict `promote_with_tighter_rule`
12. `research_scientist` | reps: Research Scientist (7); Senior Research Scientist (6) | internal `data_scientist` 0.6462 | ESCO `bioinformatics scientist` 1.0 | O*NET `Computer and Information Research Scientists` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
13. `procurement_manager` | reps: Procurement Manager (13) | internal `product_manager` 0.6401 | ESCO `energy manager` 0.8429 | O*NET `Purchasing Managers` 1.0 | conf `high` | risk `medium` | verdict `promote_with_tighter_rule`
14. `onboarding_specialist` | reps: Onboarding Specialist (13) | internal `marketing_specialist` 0.7081 | ESCO `debarker operator` 0.7598 | O*NET `Medical Records Specialists` 0.8025 | conf `high` | risk `medium` | verdict `needs_taxonomy_decision`
15. `sales_enablement_manager` | reps: Sales Enablement Manager (13) | internal `sales_manager` 0.6698 | ESCO `sales account manager` 0.7097 | O*NET `First-Line Supervisors of Retail Sales Workers` 0.7 | conf `medium` | risk `medium` | verdict `keep_other_for_now`
16. `people_partner` | reps: People Partner (7); Senior People Partner (6) | internal `people_business_partner` 0.739 | ESCO `talent acquisition manager` 0.4556 | O*NET `Patient Representatives` 0.614 | conf `low` | risk `medium` | verdict `keep_other_for_now`
17. `territory_manager` | reps: Territory Manager (11) | internal `account_manager` 0.7788 | ESCO `commercial sales representative` 1.0 | O*NET `Sales Managers` 1.0 | conf `high` | risk `medium` | verdict `promote_with_tighter_rule`
18. `fpga_engineer` | reps: FPGA Engineer (11) | internal `electrical_engineer` 1.0 | ESCO `quality engineer` 0.8172 | O*NET `Petroleum Engineers` 0.7631 | conf `high` | risk `low` | verdict `promote_safe`
19. `product_support_specialist` | reps: Product Support Specialist (11) | internal `it_support_specialist` 0.8537 | ESCO `textile product developer` 0.7205 | O*NET `Computer User Support Specialists` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
20. `software_development_manager` | reps: Software Development Manager (10) | internal `engineering_manager` 1.0 | ESCO `mine development engineer` 0.8004 | O*NET `Information Technology Project Managers` 0.8747 | conf `high` | risk `low` | verdict `promote_safe`
21. `manager_business_development` | reps: Manager, Business Development (10) | internal `account_manager` 0.9365 | ESCO `sales account manager` 0.9365 | O*NET `Marketing Managers` 0.9365 | conf `high` | risk `low` | verdict `promote_safe`
22. `business_development` | reps: Business Development Associate (10) | internal `business_development_representative` 0.8564 | ESCO `business coach` 0.8676 | O*NET `Market Research Analysts and Marketing Specialists` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
23. `photojournalist` | reps: Photojournalist (10) | internal `journalist` 0.7915 | ESCO `photojournalist` 1.0 | O*NET `Photographers` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
24. `sales_representative` | reps: Sales Representative (10) | internal `business_development_representative` 0.768 | ESCO `commercial sales representative` 1.0 | O*NET `Retail Salespersons` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
25. `operations_analyst` | reps: Operations Analyst (10) | internal `data_analyst` 0.8173 | ESCO `investment analyst` 0.7681 | O*NET `Management Analysts` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
26. `director_product_management` | reps: Director, Product Management (10) | internal `product_manager` 0.6661 | ESCO `corporate risk manager` 0.7224 | O*NET `Marketing Managers` 0.934 | conf `high` | risk `low` | verdict `promote_safe`
27. `machine_learning_scientist` | reps: Senior Machine Learning Scientist (10) | internal `ml_engineer` 0.6491 | ESCO `artificial intelligence engineer` 0.6491 | O*NET `Computer and Information Research Scientists` 1.0 | conf `high` | risk `low` | verdict `promote_safe`
28. `child_and_adolescent_therapist_lsw_contract_1099` | reps: Child and Adolescent Therapist - LSW - Contract/1099 (10) | internal `psychotherapist` 0.8766 | ESCO `animal therapist` 0.4523 | O*NET `Clinical and Counseling Psychologists` 0.781 | conf `high` | risk `low` | verdict `promote_safe`
29. `manager_programmatic` | reps: Manager, Programmatic (10) | internal `project_manager` 0.7453 | ESCO `programme manager` 0.7574 | O*NET `General and Operations Managers` 0.7453 | conf `high` | risk `medium` | verdict `promote_with_tighter_rule`
30. `operations` | reps: Operations Associate (10) | internal `operations_specialist` 0.7103 | ESCO `laser beam welder` 0.7619 | O*NET `First-Line Supervisors of Firefighting and Prevention Workers` 0.7619 | conf `medium` | risk `high` | verdict `keep_other_for_now`

## D. Candidate safe batch shortlist (max 5)
1. `firmware_engineer`
- representative titles: Senior Firmware Engineer (15); Firmware Engineer (10)
- suggested target label: `software_engineer`
- suggested role family: `software_engineering`
- support internal/ESCO/O*NET: `0.7739` / `0.8182` / `1.0`
- risk: `medium`
- promotion type: `tight_rule_candidate`
2. `onboarding_specialist`
- representative titles: Onboarding Specialist (13)
- suggested target label: `marketing_specialist`
- suggested role family: `marketing`
- support internal/ESCO/O*NET: `0.7081` / `0.7598` / `0.8025`
- risk: `medium`
- promotion type: `taxonomy_gap_do_not_promote_yet`
3. `product_support_specialist`
- representative titles: Product Support Specialist (11)
- suggested target label: `it_support_specialist`
- suggested role family: `it_operations`
- support internal/ESCO/O*NET: `0.8537` / `0.7205` / `1.0`
- risk: `low`
- promotion type: `safe_rule_candidate`

## E. Taxonomy gap list
- `onboarding_specialist` | reps: Onboarding Specialist (13) | possible family: `marketing` | why insufficient: internal target confidence not robust enough for safe promotion

## F. Failure modes
- `engineer` | reps: Principal Engineer (16); Senior Engineer (10) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `designer` | reps: Designer (11); Senior Designer (8) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `production` | reps: Production Lead (12); Production Associate (8) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `sales_enablement_manager` | reps: Sales Enablement Manager (13) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `people_partner` | reps: People Partner (7); Senior People Partner (6) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `operations` | reps: Operations Associate (10) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `director_enterprise_sales` | reps: Director, Enterprise Sales (9) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `partner_success_manager` | reps: Partner Success Manager (8) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `product_analytics_team_new_products` | reps: Product Analytics Team Lead, New Products (8) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `architect` | reps: Architect (7) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `plan_documents_specialist_freelance_project` | reps: Plan Documents Specialist - Freelance Project (7) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `specialist_facilities_property_operations` | reps: Specialist II, Facilities, Property Operations (6) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `operations_specialist_freelance_project` | reps: Operations Associate Specialist - Freelance Project (6) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high
- `product_operations_analyst_product_analytics` | reps: Product Operations Analyst - Product Analytics (6) | verdict `keep_other_for_now` | reason: ambiguity/overmatch risk remains high

## G. Final recommendation
- `semantic_layer_not_yet_actionable`
- reason: Signal is still mixed and not enough high-confidence clusters pass conservative guardrails.

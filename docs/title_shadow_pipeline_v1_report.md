# Shadow Pipeline v1 — ESCO/O*NET-assisted Title Recovery Benchmark

## 1. Baseline
- Repo: `joballert2`
- Dataset benchmark: `data/jobs/jobs_titled_en_recovery_v46.jsonl`
- Total rows: `81011`
- Other baseline: `36788`
- Baseline status: `ok`

## 2. ESCO/O*NET assets found
- ESCO occupations_en: `ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv/occupations_en.csv`
- ESCO broaderRelationsOccPillar_en: `ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv/broaderRelationsOccPillar_en.csv`
- ESCO ISCOGroups_en: `ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv/ISCOGroups_en.csv`
- O*NET Occupation Data: `ONETfiles/db_30_2_excel/Occupation Data.xlsx`
- O*NET Alternate Titles: `ONETfiles/db_30_2_excel/Alternate Titles.xlsx`
- O*NET Related Occupations: `ONETfiles/db_30_2_excel/Related Occupations.xlsx`
- ESCO lookup rows: `32918`
- O*NET lookup rows: `76881`

## 3. Residual discovery summary
### Top 50 residual raw titles
1. `General Manager` (40)
2. `Senior Market Strategy and Partnerships Manager` (36)
3. `Hair Color Bar Assistant, Licensed Cosmetologist` (32)
4. `General Application` (31)
5. `Producer` (27)
6. `Social Enterprise and Program Delivery-Evergreen` (27)
7. `Personal Care Specialist (Part Time)` (26)
8. `Quantitative Researcher` (24)
9. `Business Analyst` (20)
10. `Sonder Responder` (19)
11. `Restaurant General Manager` (19)
12. `Manager, Software Engineering` (18)
13. `Cultivation Associate` (18)
14. `Leader in Training` (17)
15. `Outside Sales Representative - Roofing` (17)
16. `Data Science Manager` (16)
17. `Principal Engineer` (16)
18. `Intelligence Operations Integrator` (16)
19. `Senior Firmware Engineer` (15)
20. `Manager, Paid Social` (15)
21. `Senior Technical Enablement Architect` (15)
22. `DevSecOps Engineer` (14)
23. `Occupational Therapist` (14)
24. `Chief of Staff` (14)
25. `Restaurant Manager` (14)
26. `HR Generalist` (13)
27. `Sales Enablement Manager` (13)
28. `Office Manager` (13)
29. `Client Partner` (13)
30. `Client Success Manager` (13)
31. `Implementation Engineer` (13)
32. `Onboarding Specialist` (13)
33. `Procurement Manager` (13)
34. `Director, FP&A` (13)
35. `DashMart Variable Schedule Team Member` (13)
36. `Machine Learning Researcher` (13)
37. `Respiratory Therapist - Registered` (13)
38. `Budtender PT` (13)
39. `Data Architect` (12)
40. `Senior Business Analyst` (12)
41. `Payroll Specialist` (12)
42. `General Interest` (12)
43. `Breeze Airways Flight Attendant - Part Time` (12)
44. `Production Lead` (12)
45. `Virtual Speech Language Pathologist (SLP)` (12)
46. `Contracted In-Home Occupational Therapist` (12)
47. `Shift Lead, Licensed Cosmetologist` (12)
48. `Licensed Real Estate Agent - Fully Vetted Leads Provided` (12)
49. `Sales Operations Analyst` (11)
50. `Fullstack Developer` (11)

### Top 50 normalized residual strings
1. `insurance agent` (159)
2. `engineer` (45)
3. `general manager` (41)
4. `market strategy and partnerships manager` (41)
5. `business analyst` (36)
6. `firmware engineer` (34)
7. `manager software engineering` (33)
8. `hair color bar assistant licensed cosmetologist` (32)
9. `general application` (31)
10. `` (31)
11. `designer` (31)
12. `producer` (28)
13. `social enterprise and program delivery evergreen` (27)
14. `join our talent community` (26)
15. `personal care specialist part time` (26)
16. `quantitative researcher` (25)
17. `engagement manager` (24)
18. `data architect` (23)
19. `devsecops engineer` (23)
20. `production` (23)
21. `support engineer` (23)
22. `business development` (22)
23. `don t see what you re looking for` (22)
24. `salesforce administrator` (21)
25. `database engineer` (21)
26. `consultant` (21)
27. `product engineer` (21)
28. `manager engineering` (20)
29. `security operations engineer` (20)
30. `salesforce developer` (19)
31. `machine learning scientist` (19)
32. `architect` (19)
33. `test engineer` (19)
34. `fp a analyst` (19)
35. `implementation engineer` (19)
36. `buyer` (19)
37. `sonder responder` (19)
38. `restaurant general manager` (19)
39. `sales operations analyst` (18)
40. `payroll specialist` (18)
41. `cultivation` (18)
42. `hr generalist` (17)
43. `operations` (17)
44. `enterprise architect` (17)
45. `data science manager` (17)
46. `sales enablement manager` (17)
47. `client success manager` (17)
48. `people partner` (17)
49. `software architect` (17)
50. `leader in training` (17)

### Top 50 tokens
1. `manager` (5964)
2. `engineer` (5780)
3. `director` (3081)
4. `specialist` (2224)
5. `operations` (2019)
6. `analyst` (1874)
7. `of` (1589)
8. `sales` (1434)
9. `and` (1317)
10. `engineering` (1219)
11. `business` (1098)
12. `data` (1083)
13. `product` (1058)
14. `systems` (1052)
15. `development` (1043)
16. `ai` (1024)
17. `technician` (999)
18. `technical` (931)
19. `support` (883)
20. `developer` (849)
21. `intern` (830)
22. `design` (816)
23. `management` (772)
24. `strategy` (760)
25. `consultant` (732)
26. `time` (688)
27. `partner` (678)
28. `security` (592)
29. `architect` (591)
30. `research` (552)
31. `head` (545)
32. `coordinator` (525)
33. `shift` (525)
34. `test` (510)
35. `2026` (505)
36. `team` (504)
37. `services` (498)
38. `global` (494)
39. `software` (488)
40. `customer` (484)
41. `enterprise` (470)
42. `part` (469)
43. `client` (458)
44. `strategic` (451)
45. `finance` (442)
46. `growth` (427)
47. `partnerships` (425)
48. `starlink` (411)
49. `remote` (407)
50. `scientist` (407)

### Top 30 bigrams
1. `director of` (576)
2. `head of` (519)
3. `part time` (466)
4. `systems engineer` (354)
5. `business development` (317)
6. `design engineer` (281)
7. `test engineer` (260)
8. `vice president` (251)
9. `software engineering` (213)
10. `business analyst` (196)
11. `full time` (193)
12. `support engineer` (189)
13. `operations analyst` (183)
14. `machine learning` (180)
15. `operations engineer` (178)
16. `summer 2026` (168)
17. `insurance agent` (168)
18. `data center` (164)
19. `territory manager` (159)
20. `2nd shift` (158)
21. `automation engineer` (153)
22. `sales director` (150)
23. `general manager` (147)
24. `fp a` (145)
25. `research engineer` (145)
26. `product management` (143)
27. `partnerships manager` (143)
28. `sales representative` (141)
29. `support specialist` (139)
30. `supply chain` (139)

### Top 30 trigrams
1. `m f d` (116)
2. `director of product` (100)
3. `operations part time` (97)
4. `manager software engineering` (92)
5. `intern summer 2026` (88)
6. `member of technical` (88)
7. `director business development` (88)
8. `bangkok based relocation` (64)
9. `ai trainer advanced` (61)
10. `join our talent` (59)
11. `don t see` (53)
12. `speech language pathologist` (51)
13. `medical science liaison` (50)
14. `based relocation provided` (50)
15. `director product management` (48)
16. `our talent community` (48)
17. `and partnerships manager` (47)
18. `market strategy and` (46)
19. `strategy and partnerships` (46)
20. `4 000 bonus` (45)
21. `of product management` (44)
22. `director of strategic` (43)
23. `regional vice president` (43)
24. `global supply manager` (41)
25. `back end engineer` (40)
26. `specialist part time` (40)
27. `go to market` (40)
28. `aircraft maintenance instructor` (39)
29. `machine learning scientist` (38)
30. `re looking for` (38)

### Fuzzy clusters (sample)
1. `insurance agent` | volume `159` | examples: insurance agent (159)
2. `market strategy and partnerships manager` | volume `47` | examples: market strategy and partnerships manager (41), market strategy partnerships manager (6)
3. `engineer` | volume `45` | examples: engineer (45)
4. `general manager` | volume `41` | examples: general manager (41)
5. `business analyst` | volume `36` | examples: business analyst (36)
6. `firmware engineer` | volume `34` | examples: firmware engineer (34)
7. `manager software engineering` | volume `33` | examples: manager software engineering (33)
8. `hair color bar assistant licensed cosmetologist` | volume `32` | examples: hair color bar assistant licensed cosmetologist (32)
9. `general application` | volume `31` | examples: general application (31)
10. `` | volume `31` | examples:  (31)
11. `designer` | volume `31` | examples: designer (31)
12. `producer` | volume `28` | examples: producer (28)
13. `social enterprise and program delivery evergreen` | volume `27` | examples: social enterprise and program delivery evergreen (27)
14. `sales director` | volume `27` | examples: sales director (14), director sales (13)
15. `join our talent community` | volume `26` | examples: join our talent community (26)
16. `personal care specialist part time` | volume `26` | examples: personal care specialist part time (26)
17. `quantitative researcher` | volume `25` | examples: quantitative researcher (25)
18. `engagement manager` | volume `24` | examples: engagement manager (24)
19. `data architect` | volume `23` | examples: data architect (23)
20. `devsecops engineer` | volume `23` | examples: devsecops engineer (23)

## 4. Top candidate clusters
1. `support_engineer_it_core` | volume `187` | action `map_to_existing` | target `it_support_specialist/it_operations` | risk `medium` | ROI `high` | ESCO `medium` | O*NET `strong` | reps: Support Engineer (11); Senior Support Engineer (9); Customer Support Engineer (7); Production Support Engineer (5)
2. `paralegal_specialty_cluster` | volume `49` | action `add_new_normalized_title` | target `paralegal/legal` | risk `medium` | ROI `medium` | ESCO `weak` | O*NET `strong` | reps: Corporate Paralegal (9); Paralegal (6); Litigation Paralegal (6); Paralegal II, Corporate (6)
3. `occupational_therapist_core` | volume `52` | action `add_new_normalized_title` | target `occupational_therapist/healthcare_clinical` | risk `low` | ROI `medium` | ESCO `weak` | O*NET `weak` | reps: Occupational Therapist (14); Contracted In-Home Occupational Therapist (12); Pediatric Occupational Therapist (8); Traveling Occupational Therapist (8)
4. `business_analyst_cluster` | volume `195` | action `keep_other_for_now` | target `/` | risk `high` | ROI `low` | ESCO `medium` | O*NET `medium` | reps: Business Analyst (20); Senior Business Analyst (12); Technical Business Analyst (4); Business Analyst - Retail Energy (3)
5. `devsecops_engineer_cluster` | volume `37` | action `map_to_existing` | target `devops_engineer/devops` | risk `low` | ROI `medium` | ESCO `medium` | O*NET `weak` | reps: DevSecOps Engineer (14); Senior DevSecOps Engineer (3); Sr. DevSecOps Engineer- Reliability & Security (Remote from Bulgaria) (1); Chief DevSecOps Engineer (1)
6. `chief_of_staff_cluster` | volume `77` | action `add_new_normalized_title` | target `chief_of_staff/operations` | risk `medium` | ROI `medium` | ESCO `none` | O*NET `none` | reps: Chief of Staff (14); Chief of Staff to the Managing Director of AI (10); Chief of Staff to the Chief Customer Officer (4); Chief of Staff, Tactical Recon & Strike (3)
7. `data_architect_cluster` | volume `36` | action `map_to_existing` | target `solutions_architect/architecture` | risk `medium` | ROI `medium` | ESCO `medium` | O*NET `medium` | reps: Data Architect (12); Senior Data Architect (7); Senior Data Architect - Wealth & Asset Management. (2); Staff Data Architect (2)
8. `hr_generalist_cluster` | volume `38` | action `add_new_normalized_title` | target `hr_generalist/people_operations` | risk `low` | ROI `medium` | ESCO `none` | O*NET `none` | reps: HR Generalist (13); Human Resources Generalist (5); Senior HR Generalist (3); Graduate HR Generalist - AMER (1)
9. `client_success_manager_cluster` | volume `36` | action `map_to_existing` | target `customer_success_manager/customer_success` | risk `medium` | ROI `medium` | ESCO `weak` | O*NET `weak` | reps: Client Success Manager (13); Senior Client Success Manager - Strategic Accounts (4); Senior Client Success Manager (2); Enterprise Client Success Manager (Chicago) (1)
10. `respiratory_therapist_core` | volume `20` | action `add_new_normalized_title` | target `respiratory_therapist/healthcare_clinical` | risk `low` | ROI `medium` | ESCO `none` | O*NET `weak` | reps: Respiratory Therapist - Registered (13); Respiratory Therapist - Registered - Float Pool (3); Respiratory Therapist - Registered FT, M-F 7p-7:30a rotating weekend (2); Respiratory Therapist - Registered Full-time Day 7a-7:30p, rotating weekends (1)
11. `implementation_engineer_cluster` | volume `31` | action `keep_other_for_now` | target `/` | risk `high` | ROI `medium` | ESCO `none` | O*NET `weak` | reps: Implementation Engineer (13); Senior Implementation Engineer (5); Sr. Technical Implementation Engineer, Prepared by Axon (5); Identity and Access Management Implementation Engineer (1)
12. `client_partner_cluster` | volume `70` | action `keep_other_for_now` | target `/` | risk `high` | ROI `low` | ESCO `none` | O*NET `none` | reps: Client Partner (13); Senior Director - Director, Client Partner (5); Senior Client Partner, Large Customer Sales (Tech) (4); Senior Client Partner, App Dev Enterprise (2)
13. `producer_naked_cluster` | volume `28` | action `keep_other_for_now` | target `/` | risk `high` | ROI `low` | ESCO `strong` | O*NET `strong` | reps: Producer (27); PRODUCER (1)
14. `procurement_manager_cluster` | volume `29` | action `keep_other_for_now` | target `/` | risk `high` | ROI `low` | ESCO `weak` | O*NET `medium` | reps: Procurement Manager (13); Procurement Manager (Data Centers) (2); Procurement Manager Operations (2); Junior Procurement Manager (1)
15. `office_manager_cluster` | volume `24` | action `keep_other_for_now` | target `/` | risk `high` | ROI `low` | ESCO `medium` | O*NET `weak` | reps: Office Manager (13); Office Manager (Tel Aviv, Israel) (1); Operations - Office Manager (1); Office Manager - ADESA (1)

## 5. 3 clusters selected for shadow execution
1. `support_engineer_it_core` -> `it_support_specialist/it_operations` | pattern `\b(?:support engineer|application support engineer|cloud support engineer|software support engineer|systems support engineer|production support engineer|infrastructure support engineer|enterprise support engineer|database support engineer|platform support engineer|data center support engineer|tech support engineer|l2 support engineer|l3 support engineer|tier\s*[123]\s*support engineer)\b` | volume_est `187` | risk `medium`
2. `paralegal_specialty_cluster` -> `paralegal/legal` | pattern `\bparalegal\b` | volume_est `49` | risk `medium`
3. `occupational_therapist_core` -> `occupational_therapist/healthcare_clinical` | pattern `\boccupational therapist\b` | volume_est `52` | risk `low`

## 6. Changes implemented
- Added shadow pipeline scripts under `experiments/title_shadow_pipeline/`:
  - `common.py`
  - `analyze_residual.py`
  - `esco_lookup.py`
  - `onet_lookup.py`
  - `generate_candidate_clusters.py`
  - `run_shadow_batch.py`
  - `README.md`
- Generated artifacts:
  - `experiments/title_shadow_pipeline/reports/residual_analysis.json`
  - `experiments/title_shadow_pipeline/reports/esco_lookup.jsonl`
  - `experiments/title_shadow_pipeline/reports/onet_lookup.jsonl`
  - `experiments/title_shadow_pipeline/reports/candidate_clusters.json`
  - `data/jobs/jobs_titled_en_shadow_esco_onet_v1.jsonl`
  - `docs/title_shadow_pipeline_v1/title_eval_step13.json`

## 7. Test results
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`
- Result: `53 passed`

## 8. Eval results
- Shadow rows_total: `81011`
- Shadow other: `36500`
- Shadow matched: `44511`
- Cluster hits from selected rules:
  - `support_engineer_it_core`: `187`
  - `occupational_therapist_core`: `52`
  - `paralegal_specialty_cluster`: `49`

## 9. Benchmark comparison vs current baseline
- Other before: `36788`
- Other after (shadow): `36500`
- Delta absolute: `-288`
- Delta percent: `-0.78%`
- New mappings introduced in shadow batch:
  - `support_engineer_it_core` -> `it_support_specialist/it_operations`
  - `paralegal_specialty_cluster` -> `paralegal/legal`
  - `occupational_therapist_core` -> `occupational_therapist/healthcare_clinical`

## 10. Recommendation
- Decision: `adopt_shadow_findings_incrementally`
- Rationale: shadow delivered measurable reduction with readable deterministic patterns; promote only low-risk clusters first and keep ESCO/O*NET as discovery aid, not auto-mapper.
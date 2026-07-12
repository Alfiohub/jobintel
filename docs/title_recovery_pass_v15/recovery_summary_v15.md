# Title Coverage Recovery Pass v15 — Healthcare Clinical Expansion

## Scope
Pass focalizzato solo su `healthcare_clinical` residuale ad alto volume, con regole conservative su sottocluster clinici ad alta chiarezza.

## Before / After
- Total rows: `81,011`
- `other` before (v14): `40,650` (`50.18%`)
- `other` after (v15): `40,430` (`49.91%`)
- Delta `other`: `-220`

## Healthcare Clinical Cluster Delta
- `healthcare_clinical` residual before (v14): `831`
- `healthcare_clinical` residual after (v15): `701`
- Delta healthcare_clinical residual: `-130`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso label esistenti per minimizzare complessità tassonomica:
- `licensed_practical_nurse`
- `registered_nurse`
- `psychotherapist`
- `behavioral_support_specialist`

## Regole aggiunte (sottocluster high-ROI)
- `health_licensed_vocational_nurse` -> `licensed_practical_nurse`
- `health_staff_nurse` -> `registered_nurse`
- `health_clinical_social_worker` -> `psychotherapist`
  - include segnali forti `licensed clinical social worker` / `lcsw`
- `health_mental_or_clinical_therapist` -> `psychotherapist`
  - `mental health therapist`, `clinical therapist`, `primary clinical therapist`
- `health_behavior_analyst` -> `behavioral_support_specialist`
  - `behavior analyst` (usato con guardrail in combinazione con altri test anti-overmatch)

## Guardrail rispettati
- nessun mapping generico di tutti i `therapist`
- nessun mapping generico di tutti i `specialist`
- nessun mapping generico di tutti gli `assistant`
- mapping abilitato solo su pattern clinici espliciti (`staff nurse`, `licensed vocational nurse`, `clinical social worker`, `mental health therapist`, `clinical therapist`, `behavior analyst`)

## Coverage (nuove regole)
- `health_staff_nurse`: `93`
- `health_mental_or_clinical_therapist`: `60`
- `health_clinical_social_worker`: `54`
- `health_licensed_vocational_nurse`: `9`
- `health_behavior_analyst`: `4`
- totale nuovi match v15 (healthcare-focused): `220`

## Sample titoli coperti
- `Licensed Vocational Nurse (LVN)` -> `licensed_practical_nurse` (`8`)
- `Staff Nurse - Emergency Department` -> `registered_nurse` (`5`)
- `Licensed Clinical Social Worker (LCSW) - Remote` -> `psychotherapist` (`3`)
- `Mental Health Therapist` -> `psychotherapist` (`4`)
- `Clinical Therapist` -> `psychotherapist` (`4`)
- `Behavior Analyst (BCBA)` -> `behavioral_support_specialist` (`2`)

## Top residual `other` (post-v15)
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
11. `restaurant general manager` (19)
12. `manager, software engineering` (18)
13. `cultivation associate` (18)
14. `k-5th grade teacher - sy 26-27` (17)
15. `leader in training` (17)
16. `outside sales representative - roofing` (17)
17. `data science manager` (16)
18. `principal engineer` (16)
19. `bilingual member services representative (remote, spanish speaking)` (16)
20. `intelligence operations integrator` (16)

## Healthcare residual ancora scoperti (top)
- `Personal Care Specialist (Part Time)` (26)
- `Clinical Trial Manager` (11)
- `Ambulatory Care Pharmacist` (11)
- `Community Health Worker` (10)
- `Certified Nurse Midwife (CNM) (PRN)` (8)
- `Remote Primary Care Coordinator` (7)
- `Medical Director` (6)
- `Associate, Medical Economics` (6)
- `Speech Language Pathologist, Clinical Fellow` (5)
- `Clinical Field Specialist` (5)

## Cluster consigliato per v16
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Healthcare clinical edge pass (midwife / care coordinator / clinical trial manager) con guardrail forti
3. Operations/service ambiguity (`member services`, `cultivation associate`) con regole conservative

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v15/*`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `29 passed`

# Title Coverage Recovery Pass v18 — Education Expansion

## Scope
Pass focalizzato solo su `education` residuale ad alto volume, con espansione pragmatica e controllata su sottocluster education espliciti.

## Before / After
- Total rows: `81,011`
- `other` before (v17): `40,073` (`49.47%`)
- `other` after (v18): `39,984` (`49.36%`)
- Delta `other`: `-89`

## Education Cluster Delta
- `education` residual before (v17): `411`
- `education` residual after (v18): `325`
- Delta education residual: `-86`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `teacher` -> `education`
- `assistant_teacher` -> `education`

## Regole aggiunte (sottocluster high-ROI)
- `education_grade_specific_teacher` -> `teacher`
  - grade-band teacher (`k-5`, `6-8`, `9-12`, `1st/2nd/... grade teacher`)
  - `title i teacher`
  - `special education teacher` / `virtual special education teacher`
  - `p.e. teacher`
- `education_instructional_aide_paraprofessional` -> `assistant_teacher`
  - `instructional aide` (incl. `1:1 instructional aide`)
  - `teacher aide`
  - `classroom/school aide`
  - `paraprofessional`

## Guardrail rispettati
- nessun mapping generico di tutti i `teacher`
- nessun mapping generico di tutti gli `assistant`
- nessun mapping generico di tutti i `counselor`
- contesto richiesto forte (grade-band / special-education / instructional-aide)
- nessun allargamento su `instructor` tecnico (es. `A&P Mechanic Instructor` resta `other`)

## Coverage (nuove regole)
- `education_grade_specific_teacher`: `69`
- `education_instructional_aide_paraprofessional`: `20`
- totale nuovi match v18 (education-focused): `89`

## Sample titoli coperti
- `K-5th Grade Teacher - SY 26-27` -> `teacher` (`17`)
- `6-8th Grade Teacher - SY 26-27` -> `teacher` (`12`)
- `9-12th Grade Teacher - SY 26-27` -> `teacher` (`6`)
- `Instructional Aide` -> `assistant_teacher` (`14`)
- `1:1 Instructional Aide` -> `assistant_teacher` (`2`)
- `Virtual Special Education Teacher` -> `teacher` (`4`)
- `Special Education Teacher` -> `teacher` (`3`)
- `Title I Teacher` -> `teacher` (`3`)

## Top residual `other` (post-v18)
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
14. `leader in training` (17)
15. `outside sales representative - roofing` (17)
16. `data science manager` (16)
17. `principal engineer` (16)
18. `bilingual member services representative (remote, spanish speaking)` (16)
19. `intelligence operations integrator` (16)
20. `senior firmware engineer` (15)

## Education residual ancora scoperti (top)
- `A&P Mechanic Instructor` (11)
- `Principal Instructor - ArcGIS Enterprise` (8)
- `Sr. Instructor` (8)
- `Aircraft Maintenance Instructor` (8)
- `*AMT Instructor*` (8)
- `Aircraft Mechanic - Instructor` (7)
- `School Director` (6)
- `Children's English Teacher in Japan` (6)
- `School Leadership` (5)
- `School Counselor` / `Virtual School Counselor` (6 totale)

## Cluster consigliato per v19
1. Generic managerial/program precision (`general manager`, strategy/program evergreen)
2. Education edge precision (`school counselor`, `school director`) con pattern stretti
3. Instructor ambiguity split (technical/aviation instructors vs education-school roles)

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v18/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v18.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `32 passed`

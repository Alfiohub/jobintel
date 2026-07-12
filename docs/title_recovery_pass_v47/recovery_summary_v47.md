# Title Coverage Recovery Pass v47 — Corporate Paralegal Variants

## Cluster scelto
`corporate_paralegal` variants (sottocluster legale corporate ad alta chiarezza).

## Before / After
- Total rows: `81,011`
- `other` before (v46): `36,788` (`45.41%`)
- `other` after (v47): `36,767` (`45.39%`)
- Delta `other`: `-21`

## Nuove label introdotte
- `paralegal` -> `legal`

## Regola aggiunta (precision)
- `legal_corporate_paralegal_v47`
  - pattern stretti su:
    - `corporate paralegal` (+ seniority/suffix)
    - `paralegal II, corporate` (e varianti roman numerals)
    - `corporate governance paralegals ...`
  - nessun allargamento a `paralegal` generico

## Coverage (nuova regola)
- `legal_corporate_paralegal_v47`: `21`
- `paralegal` in `other` prima: `50`
- `paralegal` in `other` dopo: `29`

## Sample titoli coperti
- `Corporate Paralegal` (`9`)
- `Paralegal II, Corporate` (`6`)
- `Senior Corporate Paralegal` (`4`)
- `Corporate Governance Paralegals (Remote, Toronto-based)` (`1`)
- `Corporate Paralegal Chicago` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `paralegal`
- contesto forte obbligatorio su `corporate paralegal` o forma equivalente
- test negativi su titoli legali non-equivalenti/generici:
  - `Paralegal`
  - `Litigation Paralegal`
  - `Paralegal, US Immigration`
  - `Trade Compliance Paralegal`

## Varianti lasciate volutamente in `other`
- `Paralegal` (`6`) — troppo generico
- `Litigation Paralegal` (`6`) — specialty legale diversa
- `Paralegal, US Immigration` (`1`)
- `Paralegal, Intellectual Property (IP)` (`1`)
- `Senior Paralegal, Global Litigation & Compliance` (`1`)

## Top residual `other` (post-v47)
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

## Cluster consigliato per il pass successivo
1. `support_engineer` core (`Support Engineer`, `Senior Support Engineer`, `L2/L3`) con guardrail IT stretti.
2. `producer` event-edge (`Sr. Producer, General Session`, `Sr. Producer, Trade Shows`) come micro-pass precision.
3. `paralegal` specialty edges (litigation/immigration) solo se si vuole espandere il dominio legal in modo esplicito.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `src/jobintel_next/pipelines/titles/taxonomy.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v47/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v47.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `53 passed`

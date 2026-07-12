# Title Coverage Recovery Pass v36 — Compliance / Risk Governance & Controls Edge Pass

## Cluster scelto
`compliance_risk` edge su governance/controls/compliance execution con pattern espliciti non-engineering.

## Before / After
- Total rows: `81,011`
- `other` before (v35): `38,728` (`47.81%`)
- `other` after (v36): `38,705` (`47.78%`)
- Delta `other`: `-23`

## Compliance/Risk Cluster Delta
- `compliance_risk` residual before (v35): `394`
- `compliance_risk` residual after (v36): `375`
- Delta compliance_risk residual: `-19`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `compliance_specialist` -> `compliance_risk`
- `compliance_manager` -> `compliance_risk`

## Regole aggiunte (precision)
- `compliance_governance_controls_specialist_edge_v36`
  - pattern espliciti:
    - `associate operational controls`
    - `manager, compliance execution & enablement`
    - `compliance coordinator` / `contract compliance coordinator`
    - `senior analyst, government compliance`
    - `product lead - compliance`
- `compliance_governance_controls_manager_edge_v36`
  - pattern espliciti:
    - `international trade compliance leader`
    - `sr/senior team manager, compliance`
    - `vice president, compliance`

## Coverage (nuove regole)
- `compliance_governance_controls_specialist_edge_v36`: `15`
- `compliance_governance_controls_manager_edge_v36`: `8`
- totale nuovi match v36: `23`

## Sample titoli coperti
- `Associate, Operational Controls` (`4`)
- `Manager, Compliance Execution & Enablement` (`3`)
- `Contract Compliance Coordinator` (`2`)
- `Senior Analyst, Government Compliance` (`2`)
- `International Trade Compliance Leader - APAC` (`3`)
- `Sr. Team Manager, Compliance` (`2`)
- `Vice President, Compliance` (`1`)
- `Vice President, Compliance (APAC)` (`1`)

## Guardrail rispettati
- nessun mapping generico di tutti i `controls`
- nessun mapping generico di tutti gli `specialist`
- nessun mapping generico di tutti i `manager`
- contesto forte obbligatorio (`compliance|risk|governance|controls|execution|enablement` con pattern specifici)
- esclusi pattern engineering/technical tramite test negativi:
  - `Senior Controls Engineer`
  - `Controls Engineer`
  - `Control Systems Engineer - Site Services`
  - `Controls & Automation Engineer`
  - `Automation & Controls Engineer`
  - `Staff Controls Engineer`

## Varianti lasciate volutamente in `other`
- `Senior Controls Engineer` (`4`)
- `Controls & Automation Engineer` (`3`)
- `Sr Manager, InfoSec Governance Risk and Compliance (GRC)` (`3`)
- `Microsoft 365 Governance Administrator` (`5`)
- `Regulatory Manager - Senior Regulatory Manager - Clinical Trials` (`7`)

Motivo: rischio overmatch tecnico/engineering o cluster troppo ampio/ambiguo in questo pass edge.

## Top residual `other` (post-v36)
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

## Cluster consigliato per v37
1. `customer_service` edge su `support specialist` non-IT (client/member support) con guardrail anti-overmatch.
2. `design_creative` edge su `producer` contestuale forte (video/content/editorial), lasciando `producer` nudo in `other`.
3. `compliance_risk` micro-edge su GRC non-engineering (`grc analyst/consultant` espliciti) con esclusioni tecniche forti.

## Files changed
- `src/jobintel_next/pipelines/titles/rules.py`
- `tests/pipelines/test_titles_stage_step12.py`
- eval output: `docs/title_recovery_pass_v36/*`
- output dataset: `data/jobs/jobs_titled_en_recovery_v36.jsonl`

## Test status
- `tests/pipelines/test_titles_stage_step12.py`
- `tests/pipelines/test_titles_eval_step13.py`
- `tests/test_cli_titles_step12.py`

Result: `42 passed`

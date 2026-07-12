# Title Coverage Recovery Pass v27 — Skilled Trades Precision Pass

## Cluster scelto
`skilled_trades` (sottocluster ad alta chiarezza: auto-body repair/prepper/inspector + paintless dent repair + rim repair con contesto forte).

## Before / After
- Total rows: `81,911`
- `other` before (v26 baseline): `24,532` (`29.95%`)
- `other` after (v27): `24,470` (`29.87%`)
- Delta `other`: `-62`

## Nuove label introdotte
- Nessuna nuova label.

Scelta: riuso mapping esistente su:
- `mechanic` -> `skilled_trades`

## Regole aggiunte (precision)
- `trades_auto_body_repair_precision_v27`
  - match solo su pattern espliciti:
    - `auto body` / `autobody` + (`repair|prepper|inspector|tech|technician|painter|paint prep`)
    - `paintless dent repair tech/technician`
    - `rim repair tech/technician` (incluse varianti automotive/wheel-rim)
    - `automotive interior repair ... glass repair ... tech/technician`

## Coverage (nuove regole)
- `trades_auto_body_repair_precision_v27`: `227`

Nota: una parte dei nuovi match ha sostituito mapping precedenti già non-`other`; il delta netto su `other` resta `-62`.

## Sample titoli coperti
- `Auto Body Repair Technician` (`26`)
- `Entry-level Auto Body Repair Technician` (`11`)
- `Rim Repair Technician` (`6`)
- `Mid-Level Paintless Dent Repair Technician` (`5`)
- `Mid-Level Auto Interior Repair - Glass Repair Technician - $4,000 Bonus` (`4`)
- `Auto Body Prepper` (`4`)

## Guardrail rispettati
- nessun mapping generico di tutti i `technician`
- nessun mapping generico di tutti i `mechanic`
- nessun mapping generico di tutti gli `engineer`
- contesto forte obbligatorio su auto-body/repair/rim/dent/glass
- test negativi su:
  - `IT Services Technician`
  - `Engineering Technician`
  - `Robotics Field Service Engineer`

## Top residual `other` (post-v27)
1. `General Manager` (36)
2. `Implementation Manager` (19)
3. `Sonder Responder` (19)
4. `Team Lead` (16)
5. `Assistant General Manager` (15)
6. `Machine Learning Researcher` (15)
7. `General Interest` (14)
8. `Licensed Real Estate Agent - Fully Vetted Leads Provided` (14)
9. `Budtender PT` (14)
10. `Creative Director` (13)

## Sottocluster skilled_trades ancora scoperti (top)
- `Plumbing & HVAC Service Manager (Sign-On & Relocation Offered!!!)` (8)
- `Warehouse & Fleet Manager (Relocation & Sign-On Offered!!!)` (8)
- `Plumbing - Fire Protection III` (5)
- `General Manager (Pump, Power & HVAC)` (5)
- `HVAC Lead Installer (Relocation Offered!!!)` (5)
- `Lead Plumber (Relocation & Sign On Offered!!!)` (5)
- `Licensed Plumber` (5)
- `Automotive Prepper` (4)
- `Automotive State Inspector` (4)

## Cluster consigliato per v28
1. `skilled_trades` edge su `plumbing/hvac` con pattern stretti e anti-manager overmatch.
2. `compliance_risk` edge (`regulatory/compliance specialist` con contesto forte).
3. `education` edge (`school support` esplicito) solo con pattern conservativi.

## Files changed
- `automation/microsaas/titles/title_rules.py`
- `tests/microsaas/titles/test_title_classifier_rules.py`
- eval output: `docs/title_recovery_pass_v27/*`

## Test status
- `PYTHONPATH=. uv run --active pytest -q tests/microsaas/titles/test_title_classifier_rules.py tests/microsaas/titles/test_title_classifier_fallback.py tests/microsaas/titles/test_title_taxonomy.py`
- Result: `58 passed`

# Title Coverage Recovery Pass v24 — Logistics Edge Expansion

## Cluster scelto
`logistics` edge (delivery business non-tech, fulfillment ops, fleet ops esplicite).

## Before / After
- `other` before (v23): `39,417` (`48.66%`)
- `other` after (v24): `39,388` (`48.62%`)
- Delta `other`: `-29`

## Nuove label introdotte
- Nessuna nuova label.

## Regole aggiunte
- `logistics_delivery_business_edge` -> `logistics_manager`
- `logistics_fulfillment_ops_edge` -> `logistics_coordinator`
- `logistics_fulfillment_management_edge` -> `logistics_manager`

## Coverage (nuove regole)
- totale nuovi match v24: `29`
  - delivery business edge: `9`
  - fulfillment/fleet ops edge: `15`
  - fulfillment management edge: `5`

## Sample titoli coperti
- `Manager, Delivery Excellence` (`3`)
- `Fleet Operator` (`3`)
- `Director, Delivery` (`2`)
- `Manager, Delivery Services` (`2`)
- `Fulfillment Associate` (`2`)
- `Data Center Logistics Specialist` (`2`)
- `Area Manager, Fulfillment Operations` (`2`)

## Guardrail / limiti
- pattern ancorati su forme business esplicite
- esclusi pattern delivery ambigui/tech nei test (`Technical Delivery Manager`, `Service Delivery Manager`, `Staff Cloud Architect (Delivery)`)
- pass volutamente conservativo (delta moderato)

## Top residual `other` (post-v24)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)

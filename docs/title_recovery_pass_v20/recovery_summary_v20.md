# Title Coverage Recovery Pass v20 — Skilled Trades Explicit Technician Expansion

## Cluster scelto
`skilled_trades` (sottocluster espliciti ad alto volume su technician non-IT).

## Before / After
- `other` before (v19): `39,892` (`49.24%`)
- `other` after (v20): `39,805` (`49.14%`)
- Delta `other`: `-87`

## Nuove label introdotte
- Nessuna nuova label.

## Regole aggiunte
- `trades_high_volume_technician_explicit` -> `technician`
  - `field service technician`
  - `facilities technician`
  - `manufacturing technician`
  - `cultivation technician`
  - `assembly technician` (+ contract)
  - `fire systems technician`
  - `auto airbrush technician`
  - `heavy body technician` (varianti con shift/bonus)
  - `master service technician` (varianti con bonus)

## Coverage (nuova regola)
- `trades_high_volume_technician_explicit`: `87`

## Sample titoli coperti
- `Field Service Technician` (`10`)
- `Facilities Technician` (`9`)
- `Auto Airbrush Technician` (`9`)
- `Cultivation Technician` (`9`)
- `Assembly Technician (Contract)` (`7`)
- `Fire Systems Technician` (`7`)

## Guardrail
- nessun mapping generico di tutti i `technician`
- esclusi pattern ingegneristici/IT nei test (`Field Service Engineer`, `IT Services Technician`, `Data Center Engineer`)

## Top residual `other` (post-v20)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)

## Limiti
- coda `skilled_trades` ancora ampia e mista (healthcare tech, IT tech, instructor tecnici).

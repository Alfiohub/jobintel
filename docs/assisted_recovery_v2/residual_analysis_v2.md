# Assisted Recovery v2 — Residual Analysis

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v31.jsonl`
- rows_total: `81,011`
- other baseline: `39,108`

## Strumenti usati (analysis assistita)
1. Frequency analysis su titoli `other`.
2. Token analysis (unigrammi) su `title_clean` normalizzato.
3. N-gram analysis (bigrammi/trigrammi) per pattern ricorrenti.
4. Clustering lessicale pragmatico (chiave = prime 2 parole informative dopo normalizzazione).
5. Pattern probe per cluster candidati (`media_planning`, `creative_strategist`, `onboarding_specialist`, `regulatory_ops`, `tool_trailer_diesel`).

Nota: nessun classificatore ML/online e nessun mapping automatico da fonti esterne.

## Top cluster residuali promettenti (shortlist)

### 1) `media_planning` (design/creative-adjacent)
- volume stimato: `77`
- esempi: `Media Manager`, `Senior Media Manager`, `Media Planner`, `Programmatic Media Supervisor`
- chiarezza semantica: alta
- rischio overmatch: medio-basso (contesto `media/planner/programmatic` forte)
- ROI: alto
- azione consigliata: `map_to_existing` -> `marketing_specialist`

### 2) `onboarding_specialist` (compliance/ops edge)
- volume stimato: `34`
- esempi: `Onboarding Specialist`, `Onboarding Support Specialist`, `Customer Onboarding Specialist`
- chiarezza semantica: media
- rischio overmatch: medio (onboarding non sempre compliance)
- ROI: medio
- azione consigliata: `keep_other_for_now` (serve split più fine per dominio)

### 3) `creative_strategist`
- volume stimato: `26`
- esempi: `Creative Strategist`, `Senior Creative Strategist`
- chiarezza semantica: medio-alta
- rischio overmatch: medio (overlap con marketing/performance)
- ROI: medio
- azione consigliata: `map_to_existing` (solo con guardrail più stretti in pass dedicato)

### 4) `regulatory_ops` (compliance_risk edge)
- volume stimato: `10`
- esempi: `Senior Analyst, UM Regulatory Operations`, `Director, Regulatory Operations`
- chiarezza semantica: alta
- rischio overmatch: medio-basso
- ROI: medio-basso (volume ridotto)
- azione consigliata: `map_to_existing` -> `compliance_specialist` (pass dedicato)

### 5) `tool_trailer_diesel`
- volume stimato: `2`
- esempi: `Diesel Fleet Technician`
- chiarezza semantica: alta
- rischio overmatch: basso
- ROI: basso (tail)
- azione consigliata: `map_to_existing` -> skilled trades (pass opportunistico)

## Cluster da evitare per ora (`avoid_for_now`)
- `general manager` variants
- `business analyst`
- `quantitative researcher`
- generic `designer`
- generic `producer`
- generic `engineer` / `manager` without domain context

## Cluster scelto per il first guided pass
- scelto: `media_planning`
- motivazione: miglior compromesso volume/chiarezza/rischio nel residuo corrente.

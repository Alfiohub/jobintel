# Extraction Salary Hardening - Step 11

## Cosa è stato cambiato
- Esteso `ExtractedAttributes` con `salary_period: str | None`.
- Rafforzato il parser salary per rilevare anche il periodo quando presente:
  - `hour`: `per hour`, `hourly`, `/hr`, `/hour`
  - `year`: `per year`, `annually`, `annual salary`, `/year`
  - `day`: `per day`, `daily`, `/day`
  - `month`: `per month`, `monthly`, `/month`
  - `week`: `per week`, `weekly`, `/week`
- Aggiornato report extraction per mostrare anche `salary_period` nei fill rate e sample.

## Perché era necessario
`salary_min/salary_max/salary_currency` senza periodo può essere fuorviante.

Esempio:
- testo: `$140-$180 per hour`
- prima: `140-180 USD` (semantica incompleta)
- ora: `140-180 USD`, `salary_period=hour`

## Limiti attuali
- Parsing salary ancora rule-based, non copre tutti i formati possibili.
- Il periodo è rilevato in finestra locale vicino al match salary; se il periodo è lontano può restare `None`.
- Se c'è range salary ma nessun periodo esplicito, `salary_period` resta `None` per prudenza.

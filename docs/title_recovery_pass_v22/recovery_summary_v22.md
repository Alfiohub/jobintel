# Title Coverage Recovery Pass v22 — Healthcare Support Technician Precision

## Cluster scelto
`healthcare_clinical` (sottocluster ad alta chiarezza: CNA, pharmacy technician, patient care technician).

## Before / After
- `other` before (v21): `39,670` (`48.97%`)
- `other` after (v22): `39,508` (`48.77%`)
- Delta `other`: `-162`

## Nuove label introdotte
- `certified_nursing_assistant` -> `healthcare_clinical`
- `pharmacy_technician` -> `healthcare_clinical`
- `patient_care_technician` -> `healthcare_clinical`

## Regole aggiunte
- `health_certified_nursing_assistant`
- `health_pharmacy_technician`
- `health_patient_care_technician`

## Coverage (nuove regole)
- `health_pharmacy_technician`: `78`
- `health_certified_nursing_assistant`: `54`
- `health_patient_care_technician`: `30`
- totale nuovi match v22: `162`

## Sample titoli coperti
- `Specialty Pharmacy Technician` (`15`)
- `Float Pool Certified Nursing Assistant (CNA)` (`12`)
- `Pharmacy Technician Closed Door Pharmacy` (`7`)
- `Certified Nursing Assistant (CNA) Full-Time 8-Hour Evening Shift` (`7`)
- `Patient Care Technician - HVU - FT - D - N` (`3`)

## Guardrail
- nessun mapping generico di tutti i `technician`
- contesto clinico obbligatorio (`pharmacy`, `certified nursing assistant|cna`, `patient care technician`)
- test negativi su `IT Services Technician`, `Engineering Technician`, `Medical Director`

## Top residual `other` (post-v22)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (27)

## Limiti
- `personal care specialist` e blocchi manageriali restano in `other` per evitare overmatch.

# Title Eval Step 13

Input: `data/jobs/jobs_titled_en_recovery_v47.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- matched: 44244
- other: 36767

## Top Matched Titles
- Psychiatric Mental Health Nurse Practitioner (PMHNP): 381
- Psychiatrist (MD): 324
- Senior Software Engineer: 285
- CDL Drivers: 279
- Future Technicians: 279
- Territory Account Managers: 273
- Senior Data Engineer: 224
- Sales Development Representative: 204
- Account Executive: 202
- Psychotherapist: 177
- Enterprise Account Executive: 157
- Staff Software Engineer: 143
- Software Engineer: 131
- Customer Success Manager: 127
- Senior Performance Copywriter, Personal Finance: 118
- Senior Product Manager: 115
- Business Development Representative: 114
- Lead Data Engineer: 114
- Heavy Equipment Field Technician (Mechanic): 103
- Retail Sales Associate - Part Time: 102

## Top Other Titles
- General Manager: 40
- Senior Market Strategy and Partnerships Manager: 36
- Hair Color Bar Assistant, Licensed Cosmetologist: 32
- General Application: 31
- Producer: 27
- Social Enterprise and Program Delivery-Evergreen: 27
- Personal Care Specialist (Part Time): 26
- Quantitative Researcher: 24
- Business Analyst: 20
- Sonder Responder: 19
- Restaurant General Manager: 19
- Manager, Software Engineering: 18
- Cultivation Associate: 18
- Leader in Training: 17
- Outside Sales Representative - Roofing: 17
- Data Science Manager: 16
- Principal Engineer: 16
- Intelligence Operations Integrator: 16
- Senior Firmware Engineer: 15
- Manager, Paid Social: 15

## Other Clusters
- other_long_tail: 32811 | action=keep_other
- skilled_trades: 1142 | action=add_new_normalized_title
- healthcare_clinical: 691 | action=add_new_normalized_title
- design_creative: 665 | action=map_to_existing
- logistics: 397 | action=add_new_normalized_title
- compliance_risk: 370 | action=add_new_normalized_title
- education: 316 | action=add_new_normalized_title
- retail_sales: 151 | action=add_new_normalized_title
- customer_service: 130 | action=map_to_existing
- engineering_leadership: 94 | action=add_new_normalized_title

## Sample Files
- matched: `docs/title_recovery_pass_v47/sample_title_matched_step13.jsonl`
- other: `docs/title_recovery_pass_v47/sample_title_other_step13.jsonl`
- clusters: `docs/title_recovery_pass_v47/title_other_clusters_step13.json`
# Title Eval Step 13

Input: `data/jobs/jobs_titled_en_recovery_v6.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- other: 41968
- matched: 39043

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
- Stylist (Retail) (Part-time): 27
- Personal Care Specialist (Part Time): 26
- Senior Systems Engineer: 25
- Floor Lead (Retail) (Part-time): 25
- Inside Sales Representative: 24
- Quantitative Researcher: 24
- Senior Network Engineer: 23
- Network Engineer: 22
- Business Analyst: 20
- Board Certified Behavior Analyst: 20
- Field Technician (Mechanic) (Pump, Power & HVAC): 20
- Solution Specialist: 20
- Senior People Business Partner: 19
- Solution Engineer: 19

## Other Clusters
- other_long_tail: 36042 | action=keep_other
- skilled_trades: 1682 | action=add_new_normalized_title
- design_creative: 1353 | action=map_to_existing
- healthcare_clinical: 832 | action=add_new_normalized_title
- compliance_risk: 636 | action=add_new_normalized_title
- logistics: 503 | action=add_new_normalized_title
- education: 411 | action=add_new_normalized_title
- retail_sales: 218 | action=add_new_normalized_title
- customer_service: 197 | action=map_to_existing
- engineering_leadership: 94 | action=add_new_normalized_title

## Sample Files
- matched: `docs/title_recovery_pass_v6/sample_title_matched_step13.jsonl`
- other: `docs/title_recovery_pass_v6/sample_title_other_step13.jsonl`
- clusters: `docs/title_recovery_pass_v6/title_other_clusters_step13.json`
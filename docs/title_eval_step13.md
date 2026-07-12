# Title Eval Step 13

Input: `data/jobs/jobs_titled_en.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- other: 46813
- matched: 34198

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
- Sales Manager_Chinese Vertical: 62
- General Manager: 40
- Senior Market Strategy and Partnerships Manager: 36
- Hair Color Bar Assistant, Licensed Cosmetologist: 32
- General Application: 31
- Senior Electrical Engineer: 28
- Producer: 27
- Production Technician: 27
- Social Enterprise and Program Delivery-Evergreen: 27
- Stylist (Retail) (Part-time): 27
- Manager, Sales Development: 26
- Senior Mechanical Engineer: 26
- Personal Care Specialist (Part Time): 26
- Licensed Mental Health Therapist - Remote: 26
- Senior Systems Engineer: 25
- Lead Preschool Teacher: 25
- Floor Lead (Retail) (Part-time): 25
- Per Diem Clinical Research Nurse - Home Visits: 25
- Operations Manager: 24
- Inside Sales Representative: 24

## Other Clusters
- other_long_tail: 39916 | action=keep_other
- skilled_trades: 2065 | action=add_new_normalized_title
- design_creative: 1381 | action=map_to_existing
- healthcare_clinical: 1010 | action=add_new_normalized_title
- compliance_risk: 649 | action=add_new_normalized_title
- logistics: 513 | action=add_new_normalized_title
- education: 470 | action=add_new_normalized_title
- retail_sales: 397 | action=add_new_normalized_title
- customer_service: 318 | action=map_to_existing
- engineering_leadership: 94 | action=add_new_normalized_title

## Sample Files
- matched: `docs/sample_title_matched_step13.jsonl`
- other: `docs/sample_title_other_step13.jsonl`
- clusters: `docs/title_other_clusters_step13.json`
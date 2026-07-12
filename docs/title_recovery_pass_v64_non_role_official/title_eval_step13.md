# Title Eval Step 13

Input: `data/jobs/jobs_titled_en_recovery_v64_non_role_official.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- matched: 45399
- other: 35273
- non_role: 339

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
- Producer: 27
- Social Enterprise and Program Delivery-Evergreen: 27
- Personal Care Specialist (Part Time): 26
- Quantitative Researcher: 24
- Business Analyst: 20
- Sonder Responder: 19
- Restaurant General Manager: 19
- Cultivation Associate: 18
- Leader in Training: 17
- Data Science Manager: 16
- Principal Engineer: 16
- Intelligence Operations Integrator: 16
- Senior Firmware Engineer: 15
- Manager, Paid Social: 15
- Senior Technical Enablement Architect: 15
- Chief of Staff: 14
- Restaurant Manager: 14

## Top Non-Role Titles
- General Application: 31
- Don’t see what you’re looking for?: 11
- Join Our Talent Community: 10
- Open Application: 8
- Don't see what you're looking for?: 8
- Join our Talent Community: 7
- Submit Your Application for Future Consideration: 6
- Don't see what you're looking for? Join the LightForce Talent Community: 5
- Join our Talent Community!: 4
- Talent Community: 4
- Join AlphaSense India Talent Community: 4
- Join Our Talent Community!: 4
- Sonder Responder - Expression of Interest: 4
- Language Coordinator - Open Application: 4
- Don't See What You're Looking For?: 3
- No roles that match our current openings? We still want to hear from you-join the CIQ Talent Community!: 3
- Talent Pool: 3
- Future Opportunity: Sales Development Representative META (Arabic Speaker): 3
- General Applications: 2
- Future Opportunities: 2

## Other Clusters
- other_long_tail: 31424 | action=keep_other
- skilled_trades: 1140 | action=add_new_normalized_title
- healthcare_clinical: 680 | action=add_new_normalized_title
- design_creative: 665 | action=map_to_existing
- logistics: 396 | action=add_new_normalized_title
- compliance_risk: 370 | action=add_new_normalized_title
- education: 314 | action=add_new_normalized_title
- retail_sales: 146 | action=add_new_normalized_title
- customer_service: 129 | action=map_to_existing
- engineering_leadership: 9 | action=add_new_normalized_title

## Sample Files
- matched: `docs/title_recovery_pass_v64_non_role_official/sample_title_matched_step13.jsonl`
- other: `docs/title_recovery_pass_v64_non_role_official/sample_title_other_step13.jsonl`
- clusters: `docs/title_recovery_pass_v64_non_role_official/title_other_clusters_step13.json`
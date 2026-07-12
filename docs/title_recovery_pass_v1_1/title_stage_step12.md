# Title Stage Step 12

Input cleaned: `data/jobs/jobs_indexed_en.jsonl`
Input extracted: `None`
Output: `data/jobs/jobs_titled_en_recovery_v1_1.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- other: 43533
- matched: 37478

## Top Other Titles
- General Manager: 40
- Senior Market Strategy and Partnerships Manager: 36
- Hair Color Bar Assistant, Licensed Cosmetologist: 32
- General Application: 31
- Senior Electrical Engineer: 28
- Producer: 27
- Production Technician: 27
- Social Enterprise and Program Delivery-Evergreen: 27
- Stylist (Retail) (Part-time): 27
- Senior Mechanical Engineer: 26
- Personal Care Specialist (Part Time): 26
- Licensed Mental Health Therapist - Remote: 26
- Senior Systems Engineer: 25
- Lead Preschool Teacher: 25
- Floor Lead (Retail) (Part-time): 25
- Per Diem Clinical Research Nurse - Home Visits: 25
- Inside Sales Representative: 24
- Electrical Engineer: 24
- Quantitative Researcher: 24
- Behavioral Interventionist: 23

## Known Limits
- Minimal taxonomy/rule set by design in step12.
- Classifier is title-centric; extracted context is optional and lightweight.
- Policy is conservative: ambiguous titles go to other.
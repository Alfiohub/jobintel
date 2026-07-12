# Title Stage Step 12

Input cleaned: `data/jobs/jobs_indexed_en.jsonl`
Input extracted: `None`
Output: `data/jobs/jobs_titled_en_recovery_v3.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- other: 42243
- matched: 38768

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
- Lead Preschool Teacher: 25
- Floor Lead (Retail) (Part-time): 25
- Inside Sales Representative: 24
- Quantitative Researcher: 24
- Senior Network Engineer: 23
- Network Engineer: 22
- Lead Infant Teacher: 22
- Mid-Level Automotive Parts Associate: 21
- Business Analyst: 20
- Board Certified Behavior Analyst: 20
- Field Technician (Mechanic) (Pump, Power & HVAC): 20

## Known Limits
- Minimal taxonomy/rule set by design in step12.
- Classifier is title-centric; extracted context is optional and lightweight.
- Policy is conservative: ambiguous titles go to other.
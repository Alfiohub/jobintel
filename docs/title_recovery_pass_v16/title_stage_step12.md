# Title Stage Step 12

Input cleaned: `data/jobs/jobs_indexed_en.jsonl`
Input extracted: `None`
Output: `data/jobs/jobs_titled_en_recovery_v16.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- matched: 40770
- other: 40241

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
- K-5th Grade Teacher - SY 26-27: 17
- Leader in Training: 17
- Outside Sales Representative - Roofing: 17
- Data Science Manager: 16
- Principal Engineer: 16
- Bilingual Member Services Representative (Remote, Spanish Speaking): 16
- Intelligence Operations Integrator: 16

## Known Limits
- Minimal taxonomy/rule set by design in step12.
- Classifier is title-centric; extracted context is optional and lightweight.
- Policy is conservative: ambiguous titles go to other.
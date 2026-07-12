# Title Stage Step 12

Input cleaned: `data/jobs/jobs_indexed_en.jsonl`
Input extracted: `None`
Output: `data/jobs/jobs_titled_en_recovery_v9.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- other: 41390
- matched: 39621

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
- Board Certified Behavior Analyst: 20
- Solution Specialist: 20
- Sonder Responder: 19
- Restaurant General Manager: 19
- Story Desk Editor: 19
- Manager, Software Engineering: 18
- Cultivation Associate: 18
- K-5th Grade Teacher - SY 26-27: 17
- Technical Writer: 17
- Leader in Training: 17
- Outside Sales Representative - Roofing: 17

## Known Limits
- Minimal taxonomy/rule set by design in step12.
- Classifier is title-centric; extracted context is optional and lightweight.
- Policy is conservative: ambiguous titles go to other.
# Title Stage Step 12

Input cleaned: `data/jobs/jobs_cleaned_en.jsonl`
Input extracted: `data/jobs/jobs_extracted_en.jsonl`
Output: `data/jobs/jobs_titled_en_recovery_v66_partner_lane_candidate.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Counts by Status
- matched: 45417
- other: 35255
- non_role: 339

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

## Known Limits
- Minimal taxonomy/rule set by design in step12.
- Classifier is title-centric; extracted context is optional and lightweight.
- Policy is conservative: ambiguous titles go to other.
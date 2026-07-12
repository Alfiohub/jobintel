# Phase E.11.3 — Customer Success Shadow Scoring v1

## Goal
Run the first shadow scoring pass on the refined `customer_success_manager` promotable subset from `E.11.2`.

## Input
- subset: `experiments/title_context_layer/reports/phase_e11_customer_success_promotable_v1.jsonl`
- rows: `40`

## Output
- scoring JSON: `experiments/title_context_layer/reports/phase_e11_customer_success_scoring_v1.json`

## Decision Counts
- `shadow_match`: `25`
- `review_only`: `1`
- `exclude`: `14`

## Top Shadow Titles
- `Onboarding Specialist`: `11`
- `Customer Onboarding Specialist`: `2`
- `Manager, Customer Adoption & Success (EMEA)`: `2`
- `Customer Onboarding Specialist - French Market`: `1`
- `Technical Onboarding Specialist [Contract]`: `1`
- `SaaS Onboarding Specialist`: `1`
- `Onboarding Specialist III`: `1`
- `Service Enablement Manager, CX`: `1`
- `AI Onboarding Specialist`: `1`
- `AI Onboarding Specialist - Automotive`: `1`
- `AI Onboarding Specialist - Home Services`: `1`
- `AI Onboarding Specialist - Medspa`: `1`

## Top Excluded Titles
- `Client Retention Specialist (Remote)`: `5`
- `Onboarding Specialist`: `2`
- `Counterparty Onboarding Specialist`: `1`
- `Data Onboarding Specialist`: `1`
- `Bilingual Client Retention Specialist`: `1`
- `Client Retention Specialist`: `1`
- `Client Onboarding Specialist`: `1`
- `Patient Onboarding Specialist`: `1`
- `Vendor Onboarding Specialist`: `1`

## Reading
The customer-success lane is now materially stronger than before:
- a real shadow-matchable subset exists
- it is not just `Onboarding Specialist`
- but the exclusions are also informative and necessary

What the exclusions show:
- finance/compliance onboarding should not be forced into customer success
- procurement/vendor onboarding should stay out
- healthcare/patient onboarding should stay out
- some debt/financial-retention roles remain too compliance-adjacent for a safe customer-success promotion

## Recommendation
- move to a true `E.11.4` shadow batch using only the `25` `shadow_match` rows as the positive seed
- keep the `14` excluded rows as explicit negative tests/examples
- keep the broad engagement-manager family outside the first customer-success pilot

# Phase E.11.4 — Customer Success Shadow Batch v1

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- other before: `35732`

## Shadow Result
- shadow matches added: `12`
- other after shadow: `35720`
- delta other: `-12`

## Sample Matches
- `Customer Onboarding Specialist - French Market` | target `customer_success_manager/customer_success` | url `https://job-boards.eu.greenhouse.io/amenitiz/jobs/4765645101`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | url `https://job-boards.eu.greenhouse.io/cision/jobs/4745539101`
- `Technical Onboarding Specialist [Contract]` | target `customer_success_manager/customer_success` | url `https://www.clever.com/about/careers?gh_jid=7600446`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/glossgenius/jobs/7581091003`
- `SaaS Onboarding Specialist` | target `customer_success_manager/customer_success` | url `https://www.housecallpro.com/careers/open-positions/?gh_jid=4286314004`
- `Customer Onboarding Specialist` | target `customer_success_manager/customer_success` | url `https://www.hubspot.com/careers/jobs/7589346?gh_jid=7589346`
- `Manager, Customer Adoption & Success (EMEA)` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/lightspeedhq/jobs/7620025`
- `Manager, Customer Adoption & Success (EMEA)` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/lightspeedhq/jobs/7757924`
- `Onboarding Specialist III` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/m3/jobs/7592709003`
- `Service Enablement Manager, CX` | target `customer_success_manager/customer_success` | url `https://boards.eu.greenhouse.io/nice/jobs/4795139101?gh_jid=4795139101`
- `AI Onboarding Specialist` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/podium81/jobs/7597038`
- `AI Onboarding Specialist - Automotive` | target `customer_success_manager/customer_success` | url `https://job-boards.greenhouse.io/podium81/jobs/7557676`

## Recommendation
- `customer_success_shadow_lane_needs_more_work`
- reason: Signal exists, but the narrowed customer-success subset is still too small for the next production-candidate review.

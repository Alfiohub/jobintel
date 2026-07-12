# Phase 11.5 — Shadow Context-Gated Rules Tuning

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- other before: `35952`

## Shadow Result
- shadow matches added: `37`
- other after shadow: `35915`
- delta other: `-37`

## Rule Hits
- `ctx_onboarding_specialist_customer_success_v2`: `11`
- `ctx_producer_content_v1`: `26`

## Sample Matches
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, adoption` | exclusions `employee`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, creative, campaign` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, creative` | exclusions `none`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, implementation, onboarding, platform, product, software, saas, adoption, customer success, implementation process, sales` | exclusions `aml, employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`
- `Onboarding Specialist` | target `customer_success_manager/customer_success` | rule `ctx_onboarding_specialist_customer_success_v2` | evidence `customer, client, implementation, onboarding, platform, product, software, saas, sales` | exclusions `employee`

## Excluded Samples
- `Producer` | evidence `creative` | exclusions `game, jira, scrum, engineers`
- `Onboarding Specialist` | evidence `customer, merchant, onboarding, platform, product` | exclusions `kyc, underwriting, compliance`
- `Onboarding Specialist` | evidence `client, onboarding` | exclusions `compliance, employee`

## Recommendation
- `shadow_context_rules_viable_for_review`
- reason: Tuned context-gated rules generated enough shadow matches to justify formal review before any production candidate patch.

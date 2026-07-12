# Phase 11.4 — Shadow Context-Gated Rules Draft

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- other before: `35952`

## Shadow Result
- shadow matches added: `26`
- other after shadow: `35926`
- delta other: `-26`

## Rule Hits
- `ctx_producer_content_v1`: `26`

## Sample Matches
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, creative, campaign` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, creative` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast, creative, video` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast, creative, video` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast, creative, video` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast, creative, video` | exclusions `none`
- `Producer` | target `content_producer/content` | rule `ctx_producer_content_v1` | evidence `content, news, broadcast` | exclusions `none`

## Excluded Samples
- `Producer` | evidence `creative` | exclusions `game, jira, scrum, engineers`
- `Onboarding Specialist` | evidence `customer, merchant, onboarding` | exclusions `kyc`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `client, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `customer, implementation, onboarding` | exclusions `employee, aml`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`
- `Onboarding Specialist` | evidence `customer, client, implementation, onboarding` | exclusions `employee`

## Recommendation
- `shadow_context_rules_need_more_tuning`
- reason: Signal exists but current gated rules need more tuning before formal review.

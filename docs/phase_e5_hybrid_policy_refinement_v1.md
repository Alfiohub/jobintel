# Phase 11.2 — Context Scoring Refinement

## Priority Titles
### `Onboarding Specialist`
- volume: `13`
- dominant family: `customer_success`
- dominant share: `0.9231`
- high-confidence examples: `10`
- conflicting examples: `1`
- recommended target: `customer_success_manager/customer_success`
- decision: `ready_for_tight_rule`
- sample evidence:
  - `adyen` | family `customer_success` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/adyen/jobs/7422228`
  - `cision` | family `customer_success` | conf `high` | score `5` | url `https://job-boards.eu.greenhouse.io/cision/jobs/4745539101`
  - `focusfinancialpartners` | family `people_operations` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/focusfinancialpartners/jobs/5704625004`

### `Partner Manager`
- volume: `9`
- dominant family: `sales`
- dominant share: `1.0`
- high-confidence examples: `1`
- conflicting examples: `0`
- recommended target: `account_manager/sales`
- decision: `review_only_keep_context`
- sample evidence:
  - `beyondtrust` | family `sales` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/beyondtrust/jobs/7397198`
  - `elastic` | family `sales` | conf `high` | score `5` | url `https://jobs.elastic.co/jobs?gh_jid=7343843&gh_jid=7343843`
  - `esri` | family `sales` | conf `medium` | score `3` | url `https://www.esri.com/careers/5036435007?gh_jid=5036435007`

### `Producer`
- volume: `27`
- dominant family: `content`
- dominant share: `0.963`
- high-confidence examples: `13`
- conflicting examples: `1`
- recommended target: `content_producer/content`
- decision: `ready_for_tight_rule`
- sample evidence:
  - `2k` | family `software_engineering` | conf `high` | score `5` | url `https://job-boards.greenhouse.io/2k/jobs/7564923003`
  - `dept` | family `content` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/dept/jobs/7740135`
  - `eucalyptus` | family `content` | conf `medium` | score `2` | url `https://job-boards.greenhouse.io/eucalyptus/jobs/4651418005`

## Final Recommendation
- `ready_for_context_gated_rule_design`
- reason: At least two priority ambiguous titles have dominant context families strong enough to justify drafting future gated production rules.

# Phase 11.1 — Hybrid Title + Context Pilot Review

## Pilot Summary
- joined rows: `83`
- target titles: `Designer, Implementation Engineer, Onboarding Specialist, Operations Analyst, Partner Manager, Producer`

## Cluster Review
### `Designer`
- volume: `11`
- dominant context family: `design`
- dominant family count: `11`
- recommended action: `needs_tighter_rule`
- rationale: context repeatedly points to `design`
- sample evidence:
  - `billiontoone` | family `design` | conf `high` | score `6` | url `https://job-boards.greenhouse.io/billiontoone/jobs/4589731005`
  - `hovercraft` | family `design` | conf `high` | score `4` | url `https://job-boards.greenhouse.io/hovercraft/jobs/4091424009`
  - `landor` | family `design` | conf `high` | score `4` | url `https://job-boards.greenhouse.io/landor/jobs/7676342`

### `Implementation Engineer`
- volume: `13`
- dominant context family: `customer_success`
- dominant family count: `9`
- recommended action: `needs_context_not_title_only`
- rationale: context repeatedly points to `customer_success`
- sample evidence:
  - `adyen` | family `customer_success` | conf `high` | score `4` | url `https://job-boards.greenhouse.io/adyen/jobs/7105787`
  - `adyen` | family `customer_success` | conf `high` | score `4` | url `https://job-boards.greenhouse.io/adyen/jobs/7270730`
  - `adyen` | family `customer_success` | conf `high` | score `4` | url `https://job-boards.greenhouse.io/adyen/jobs/7641067`

### `Onboarding Specialist`
- volume: `13`
- dominant context family: `customer_success`
- dominant family count: `12`
- recommended action: `needs_tighter_rule`
- rationale: context repeatedly points to `customer_success`
- sample evidence:
  - `adyen` | family `customer_success` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/adyen/jobs/7422228`
  - `cision` | family `customer_success` | conf `high` | score `5` | url `https://job-boards.eu.greenhouse.io/cision/jobs/4745539101`
  - `focusfinancialpartners` | family `people_operations` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/focusfinancialpartners/jobs/5704625004`

### `Operations Analyst`
- volume: `10`
- dominant context family: `operations`
- dominant family count: `5`
- recommended action: `needs_context_not_title_only`
- rationale: context repeatedly points to `operations`
- sample evidence:
  - `correlationone` | family `operations` | conf `high` | score `5` | url `https://job-boards.greenhouse.io/correlationone/jobs/5821153004`
  - `correlationone` | family `operations` | conf `high` | score `5` | url `https://job-boards.greenhouse.io/correlationone/jobs/5821155004`
  - `correlationone` | family `operations` | conf `high` | score `5` | url `https://job-boards.greenhouse.io/correlationone/jobs/5823584004`

### `Partner Manager`
- volume: `9`
- dominant context family: `sales`
- dominant family count: `9`
- recommended action: `needs_tighter_rule`
- rationale: context repeatedly points to `sales`
- sample evidence:
  - `beyondtrust` | family `sales` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/beyondtrust/jobs/7397198`
  - `elastic` | family `sales` | conf `high` | score `5` | url `https://jobs.elastic.co/jobs?gh_jid=7343843&gh_jid=7343843`
  - `esri` | family `sales` | conf `medium` | score `3` | url `https://www.esri.com/careers/5036435007?gh_jid=5036435007`

### `Producer`
- volume: `27`
- dominant context family: `content`
- dominant family count: `26`
- recommended action: `needs_tighter_rule`
- rationale: context repeatedly points to `content`
- sample evidence:
  - `2k` | family `software_engineering` | conf `high` | score `5` | url `https://job-boards.greenhouse.io/2k/jobs/7564923003`
  - `dept` | family `content` | conf `medium` | score `3` | url `https://job-boards.greenhouse.io/dept/jobs/7740135`
  - `eucalyptus` | family `content` | conf `medium` | score `2` | url `https://job-boards.greenhouse.io/eucalyptus/jobs/4651418005`

## Recommendation
- `ready_for_hybrid_pilot`
- reason: At least two ambiguous title families now show repeated context patterns that could support a future gated rule.

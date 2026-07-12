# Phase E.15.4 — Partner Lane Shadow Batch v2

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v64_non_role_official.jsonl`
- other before: `35273`

## Shadow Result
- shadow matches added: `27`
- other after shadow: `35246`
- delta other: `-27`

## Sample Matches
- `Partner Growth Manager` | target `account_manager/sales` | url `https://job-boards.greenhouse.io/affirm/jobs/7589306003`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://job-boards.greenhouse.io/affirm/jobs/7589308003`
- `Partner Development Manager - Mandarin Speaker` | target `account_manager/sales` | url `https://careers.appsflyer.com/jobs/position/8349704002?gh_jid=8349704002`
- `Regional Partner Director - Northeast` | target `account_manager/sales` | url `https://bigid.com/company/careers/job-details/8440277002?gh_jid=8440277002`
- `Strategic Partner Director` | target `account_manager/sales` | url `https://www.bill.com/job?5705206004&gh_jid=5705206004`
- `Partner Director, IBM - APAC` | target `account_manager/sales` | url `https://www.cockroachlabs.com/careers/job/?gh_jid=7622194`
- `Strategic SI Partner Development Manager` | target `account_manager/sales` | url `https://www.fivetran.com/careers/job?gh_jid=7654642003`
- `Strategic SI Partner Development Manager` | target `account_manager/sales` | url `https://www.fivetran.com/careers/job?gh_jid=7653220003`
- `Strategic SI Partner Development Manager` | target `account_manager/sales` | url `https://www.fivetran.com/careers/job?gh_jid=7653223003`
- `Core Partner Development Manager - UKI` | target `account_manager/sales` | url `https://www.hubspot.com/careers/jobs/7721764?gh_jid=7721764`
- `Core Partner Development Manager - UKI` | target `account_manager/sales` | url `https://www.hubspot.com/careers/jobs/7721773?gh_jid=7721773`
- `Core Partner Development Manager - UKI` | target `account_manager/sales` | url `https://www.hubspot.com/careers/jobs/7694606?gh_jid=7694606`

## Recommendation
- `partner_lane_shadow_viable_for_review`
- reason: The narrowed partner-only subset produces enough shadow matches to justify production-candidate review.

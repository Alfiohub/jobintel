# Phase E.15.2 — Account Manager Shadow Batch v1

## Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`
- other before: `35581`

## Shadow Result
- shadow matches added: `19`
- other after shadow: `35562`
- delta other: `-19`

## Sample Matches
- `Partner Growth Manager` | target `account_manager/sales` | url `https://job-boards.greenhouse.io/affirm/jobs/7589306003`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://job-boards.greenhouse.io/affirm/jobs/7589308003`
- `Partner Development Manager - Mandarin Speaker` | target `account_manager/sales` | url `https://careers.appsflyer.com/jobs/position/8349704002?gh_jid=8349704002`
- `Strategic Partner Director` | target `account_manager/sales` | url `https://www.bill.com/job?5705206004&gh_jid=5705206004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784181004?gh_jid=5784181004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784175004?gh_jid=5784175004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784180004?gh_jid=5784180004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784182004?gh_jid=5784182004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784166004?gh_jid=5784166004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784170004?gh_jid=5784170004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784171004?gh_jid=5784171004`
- `Partner Growth Manager` | target `account_manager/sales` | url `https://connecteam.com/careers/5784174004?gh_jid=5784174004`

## Recommendation
- `account_manager_shadow_lane_viable`
- reason: The partner/client-strategy subset produces enough shadow matches to justify formal review for a production-candidate context gate.

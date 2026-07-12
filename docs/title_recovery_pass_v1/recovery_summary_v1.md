# Title Coverage Recovery Pass v1

## Scope
Pass dedicato solo a riduzione `other` tramite aggiornamento rules/title taxonomy behavior (no UI/prodotto).

## Artifacts
- `docs/title_recovery_pass_v1/title_stage_step12.json`
- `docs/title_recovery_pass_v1/title_stage_step12.md`
- `docs/title_recovery_pass_v1/title_eval_step13.json`
- `docs/title_recovery_pass_v1/title_eval_step13.md`
- `docs/title_recovery_pass_v1/title_other_clusters_step13.json`
- `data/jobs/jobs_titled_en_recovery_v1.jsonl`

## Before / After
- Total rows: `81,011`
- `other` before: `46,813` (`57.79%`)
- `other` after: `42,487` (`52.45%`)
- Delta `other`: `-4,326`
- Matched (non-other) before: `34,198`
- Matched (non-other) after: `38,524`

## Cluster focus covered in this pass
- software / infra / platform / security
- data / analytics
- sales / account / bizdev
- marketing
- finance / accounting / compliance
- operations / support

## New normalized titles introduced
- `sales_manager` (`role_family=sales`)

Rationale: cluster ad alto volume su `sales manager / regional sales director / director of sales`
con semantica chiara e distinta da `account_manager`.

## Top residual `other` (post-pass)
1. `general manager` (40)
2. `senior market strategy and partnerships manager` (36)
3. `hair color bar assistant, licensed cosmetologist` (32)
4. `general application` (31)
5. `producer` (28)
6. `senior electrical engineer` (28)
7. `production technician` (27)
8. `social enterprise and program delivery-evergreen` (27)
9. `stylist (retail) (part-time)` (27)
10. `senior mechanical engineer` (26)

## Suggested next clusters (Recovery Pass v2)
1. Skilled trades / industrial engineering (`electrical/mechanical/manufacturing/maintenance/auto technician`)
2. Healthcare support (`LPN`, `medical assistant`, `behavioral interventionist`, therapist variants)
3. Education / childcare (`lead preschool teacher`, `lead infant teacher`, aides)
4. Retail/restaurant operations (`stylist retail`, `floor lead`, `restaurant manager`)
5. Generic leadership/program titles (`general manager`, strategy/program evergreen) with stricter anti-overmatch rules.

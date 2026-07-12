# Phase E.10 — Batch Execution v58

## Goal
Execute the first recoverability-driven safe batch on the official title pipeline, using only in-taxonomy, title-only candidates with narrow deterministic patterns.

## Input Baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows_total: `81,011`
- other before: `35,952`

## Shortlist Refinement
The raw Phase E.10 shortlist was narrowed before implementation.

Promoted in v58:
- `engineering_manager`
  - `Engineering Director`
  - `Manager, Software Development ...`
  - `Manager, Software Engineering ...`
- `it_support_specialist`
  - `Associate IT Specialist`
  - `Application Support Specialist` variants
  - `Windows Platform Support (L1/L2/L3)`
  - `AWS Cloud Administrator`
  - `Business Applications Administrator`
  - `Virtual Platform Administrator`
- `sales_manager`
  - `Director, Sales ...`
  - `Director, Enterprise Sales ...`
  - `Sales Director ...`
  - `VP, Sales`

Deferred from the shortlist:
- `software_engineer`
  - volume is high, but the cluster is too heterogeneous for a narrow rule batch
- `systems_administrator` as a standalone target
  - not an official taxonomy label; only the narrow admin variants above were promoted to `it_support_specialist`
- ambiguous sales/leadership variants without explicit sales/software markers

## Rules Added
- `eng_software_manager_variants_v58`
- `it_specialist_and_support_variants_v58`
- `it_admin_variants_v58`
- `sales_director_variants_v58`

## Tests
Command:
```bash
uv run pytest tests/pipelines/test_titles_stage_step12.py tests/pipelines/test_titles_eval_step13.py tests/test_cli_titles_step12.py
```

Result:
- `73 passed`

## Output
- output dataset: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- report dir: `docs/title_recovery_pass_v58_recoverability_batch`

## Outcome
- matched after: `45,279`
- other after: `35,732`
- delta matched: `+220`
- delta other: `-220`

## Rule Attribution
Changed rows by new rule:
- `eng_software_manager_variants_v58`: `105`
- `sales_director_variants_v58`: `105`
- `it_specialist_and_support_variants_v58`: `7`
- `it_admin_variants_v58`: `3`

## Reading
This batch is useful and clean, but it also confirms the next-order pattern:
- high-signal leadership/sales clusters can still be recovered with title-only rules
- IT/admin recoverability exists, but in smaller pockets when constrained to low-risk forms
- the larger remaining opportunity is still in the `recoverable_with_context` and `taxonomy_gap` backlogs

## Recommendation
- accept v58 as a valid safe-batch candidate
- keep `software_engineer` out of the next title-only batch until it is split into narrower subclusters
- use the next cycle for:
  1. a context-backed batch on `customer_success_manager / account_manager / project_manager`
  2. a taxonomy decision review on `quantitative_researcher / credit_analyst / market_access_director`

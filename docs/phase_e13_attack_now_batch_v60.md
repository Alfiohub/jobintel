# Phase E.13 — Attack-Now Batch v60

## Goal
Execute the next safe `attack_now` batch after `v58`, using only narrow title-only rules with existing taxonomy support.

## Input baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl`
- baseline `other`: `35,732`

## New rules added
- `finance_fpna_core_v60`
- `finance_strategic_finance_core_v60`
- `finance_credit_analyst_core_v60`
- `industrial_thermal_engineer_v60`
- `industrial_fluids_engineer_v60`
- `industrial_physical_design_engineer_v60`

## Targets
- `financial_analyst / finance`
- `credit_analyst / finance`
- `mechanical_engineer / industrial_engineering`
- `electrical_engineer / industrial_engineering`

## Why this batch
The residual audit and the `v58` residual scan showed real title-only volume in four narrow lanes:
- `FP&A`
- `Strategic Finance`
- `Credit Analyst`
- `Thermal / Fluids / Physical Design Engineer`

These were still landing in `other`, while the target labels already existed in taxonomy.

## Test status
Command:
- `uv run pytest tests/pipelines/test_titles_stage_step12.py tests/pipelines/test_titles_eval_step13.py tests/test_cli_titles_step12.py`

Result:
- `75 passed`

## Output dataset
- `data/jobs/jobs_titled_en_recovery_v60_attack_now_batch.jsonl`

## Eval output
- `docs/title_recovery_pass_v60_attack_now_batch/title_eval_step13.md`

## Delta
- baseline `other`: `35,732`
- `v60` `other`: `35,620`
- absolute delta: `-112`

## Attribution of changed rows
- `finance_fpna_core_v60`: `49`
- `finance_strategic_finance_core_v60`: `20`
- `industrial_physical_design_engineer_v60`: `15`
- `industrial_thermal_engineer_v60`: `13`
- `finance_credit_analyst_core_v60`: `8`
- `industrial_fluids_engineer_v60`: `7`

## Example recovered titles
### Finance
- `Senior FP&A Specialist`
- `Head of FP&A`
- `FP&A Business Partner`
- `Head of Strategic Finance`
- `Director, Strategic Finance`
- `Senior Credit Analyst`
- `Credit Analyst`

### Industrial engineering
- `Senior Thermal Engineer`
- `Launch Fluids Engineer II`
- `Physical Design Engineer`
- `AI Silicon Physical Design Engineer`
- `Silicon Physical Design Engineer`

## Guardrails kept out
- `Strategic Finance & Analytics Manager - USA - Remote`
- `Analyst, Customer Support, Strategic Finance`
- `Finance Expert - Private Credit`
- `Private Credit Reporter`
- `Private Credit Lawyer (London)`
- `Principal Hardware Design Engineer`
- `Hardware Design Engineer, Systems Engineering`

## Reading
This batch is smaller than `v58` but still worthwhile.
The strongest residual title-only value is currently in:
- finance specialist variants
- narrow industrial engineering specialist titles

It does not solve the broader residual problem, but it converts a real slice of `other` without widening the classifier aggressively.

## Decision
- `v60_safe_batch_viable`

## Next sensible moves
1. continue with a new `attack_now` batch on the next tight title-only lanes
2. or return to `recoverable_with_context` lanes once title-only ROI drops again

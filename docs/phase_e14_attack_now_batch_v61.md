# Phase E.14 — Attack-Now Batch v61

## Goal
Execute one more narrow title-only recovery batch after `v60`, focused on lanes with existing taxonomy support and low ambiguity.

## Input baseline
- input dataset: `data/jobs/jobs_titled_en_recovery_v60_attack_now_batch.jsonl`
- baseline `other`: `35,620`

## New rules added
- widened `content_technical_writer`
- `finance_quantitative_researcher_core_v61`

## Targets
- `technical_writer / content`
- `quantitative_researcher / finance`

## Why this batch
The `v60` residual still contained two narrow lanes with clean title signals:
- explicit `technical writer` titles with suffixes
- finance-flavored `quantitative researcher` titles containing signals such as `options`, `equities`, `commodities`, `trading`, or `systematic`

The batch deliberately avoided:
- generic `Quantitative Researcher`
- healthcare / education / ML research variants
- generic writer/editor titles

## Test status
Command:
- `uv run pytest tests/pipelines/test_titles_stage_step12.py tests/pipelines/test_titles_eval_step13.py tests/test_cli_titles_step12.py`

Result:
- `76 passed`

## Output dataset
- `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`

## Eval output
- `docs/title_recovery_pass_v61_attack_now_batch/title_eval_step13.md`

## Delta
- baseline `other`: `35,620`
- `v61` `other`: `35,581`
- absolute delta: `-39`

## Attribution of changed rows
- `content_technical_writer`: `21`
- `finance_quantitative_researcher_core_v61`: `18`

## Example recovered titles
### Content
- `Sr. Technical Writer, API Docs`
- `Lead Technical Writer, Intelligence Systems`
- `Technical Writer, Defense Hardware & Systems`
- `Technical Writer - SaaS`

### Finance
- `Senior Quantitative Researcher - Options Market Making`
- `Quant Researcher - Systematic Equites`
- `Quantitative Researcher - Commodities`
- `Quantitative Researcher - Trading team`
- `Quantitative Researcher, Trading Research`

## Guardrails kept out
- `Quantitative Researcher`
- `Junior Quantitative Researcher`
- `Quantitative Researcher, Healthcare Innovations`
- `Quantitative Research Associate, Educational Measurement`
- `Quantitative Researcher - Machine Learning`
- `Writer`
- `Content Writer`

## Reading
`v61` is a valid batch, but the title-only ROI is now clearly dropping.
The remaining residual still has recoverable value, but it is increasingly concentrated in:
- context-dependent lanes
- taxonomy-dependent lanes
- broader ambiguous titles

## Decision
- `v61_safe_batch_viable_but_low_yield`

## Next sensible moves
1. switch back to the `recoverable_with_context` lane
2. or keep title-only work only for very narrow exact-title pockets

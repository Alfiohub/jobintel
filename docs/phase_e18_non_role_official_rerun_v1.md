# Phase E.18 — Non-Role Official Rerun v1

## Goal
Measure the real impact of promoting `non_role_recruiting_entry` into the official title engine.

## Baseline
- prior official-like comparison dataset: `data/jobs/jobs_titled_en_recovery_v61_attack_now_batch.jsonl`
- rows_total: `81,011`
- matched: `45,430`
- other: `35,581`

## New Official Rerun
- output dataset: `data/jobs/jobs_titled_en_recovery_v64_non_role_official.jsonl`
- report dir: `docs/title_recovery_pass_v64_non_role_official/`

## Result
- matched: `45,399`
- other: `35,273`
- non_role: `339`

## Delta vs v61
- `other`: `-308`
- `matched`: `-31`
- `non_role`: `+339`

## Interpretation
This is the expected title-only effect:
- many recruiting placeholders are detectable directly from title text
- but title-only official promotion is narrower than the earlier shadow pass
- the difference vs shadow is explained by description-based cues that are not part of the official title engine

Comparison with earlier shadow estimate:
- shadow non_role total: `563`
- official title-only non_role total: `339`
- missing from official title-only: largely description-driven cases such as generic future-opportunity or talent-pool postings without explicit placeholder titles

## Practical Effect
- the occupational residual becomes cleaner
- a real subset of fake jobs is now officially separated from plain `other`
- downstream compatibility is preserved because `non_role` is still excluded through `title_is_other = true`

## Recommendation
- `official_non_role_promotion_validated`
- next correct step: `E.15.6 — Partner Lane Production-Candidate Rule Proposal`

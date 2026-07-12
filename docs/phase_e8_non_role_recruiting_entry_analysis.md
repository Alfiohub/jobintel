# Phase E.8 — Non-Role Recruiting Entry Analysis

## Goal
Measure how much of the current dataset is made of recruiting placeholders or non-role entries that should be separated from occupational coding.

## Input
- dataset: `data/jobs/jobs_titled_en_recovery_v55_semantic_batch.jsonl`
- rows total: `81,011`
- official current `other`: `35,952`

## Detection Logic
Shadow-only detection using title and description patterns such as:
- `general application`
- `general interest`
- `talent community`
- `talent pool`
- `future opportunities`
- `future opportunity`
- `expression of interest`
- `open application`
- `apply here`
- `don't see what you're looking for`
- `send us your resume`
- `keep your information on file`

## Result
- total non-role recruiting entry candidates: `563`
- share of full dataset: `0.69%`

### Candidate status split
- currently in `other`: `459`
- currently in `matched`: `104`

## Impact if isolated from occupational residual
If we treat these as a separate macro-class and remove only the current `other` candidates from the occupational residual:
- current `other`: `35,952`
- less non-role candidates in `other`: `459`
- adjusted occupational `other`: `35,493`

This is a reduction of:
- `-459` absolute
- about `-1.28%` of the current residual

## Important Observation
The analysis shows two things:
1. there is a real non-role slice inside `other`
2. some recruiting-placeholder titles are currently being matched as real occupations

This means the correct long-term treatment is not only:
- “remove some noise from `other`”

but rather:
- introduce a pre-classification or early-routing macro-class for non-role recruiting entries

## Pattern Examples
High-signal examples:
- `General Application`
- `Join our Talent Community`
- `General Interest - Future Consideration`
- `Future Opportunities at Comet`
- `Don’t see what you’re looking for?`
- `Talent Community`
- `Open Application`

Borderline but still likely non-role recruiting entries:
- `Expression of Interest: Machine Learning Engineer`
- `Associate, Business Development - Talent Pool`
- `Program Manager (Future Opportunity)`

These include role hints, but still describe recruiting funnel entries rather than concrete openings.

## Recommendation
- introduce a shadow macro-class: `non_role_recruiting_entry`
- apply it before occupational title normalization
- review the matched subset separately, because they are the highest-risk contamination cases

## Decision
- `macro_class_worth_pursuing`

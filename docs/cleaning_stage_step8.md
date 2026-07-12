# Cleaning Stage Step 8

Input: `data/jobs/jobs_en_filtered.jsonl`
Output: `data/jobs/jobs_cleaned_en.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Rules Used
- title_clean: trim whitespace + normalize separators
- description_clean: html unescape + strip html tags + whitespace normalization
- location_clean: trim/normalize whitespace
- requirements/responsibilities: simple heading/sentence heuristics
- content_hash: stable sha256 over cleaned text fields

## Known Limits
- No semantic normalization in cleaning stage
- Section extraction is heuristic and may miss implicit sections
- description_clean is linearized text (structure reduced)

## Sample Cleaned Rows
- url: https://job-boards.greenhouse.io/found/jobs/4652575005
  - title_clean: Data Analytics Director
  - content_hash: c3e42e5611fcc6c53b920caa113a25ed616d764554fd247e02a7050989f3280e
- url: https://job-boards.greenhouse.io/found/jobs/4665181005
  - title_clean: Growth Marketing Manager
  - content_hash: 7ff55bd39896138e7dc407397e2437c11bd5b2f802e54324f9f91a540874db10
- url: https://job-boards.greenhouse.io/found/jobs/4668478005
  - title_clean: Marketing Creative Operations & Design Manager
  - content_hash: dfa9fe9d61cd5bcabd89ddf46ea1f3178b8f172ab3808e70448e3ec0b93bf17f
- url: https://job-boards.greenhouse.io/found/jobs/4668477005
  - title_clean: Social Media Manager
  - content_hash: a94e808f62dc8829adde1013970dc66db57d9b86594ee3f45f367c4427000243
- url: https://job-boards.greenhouse.io/found/jobs/4501664005
  - title_clean: Telehealth Provider (MD & DO)
  - content_hash: 09fcb696c0b175b55e91c7f2c966e4a8a2e579f6175746a84ec100a2f47d65b1
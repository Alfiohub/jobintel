# Indexed Job Stage Step 14

## Input Files
- canonical: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/canonical.jsonl`
- language: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/language.jsonl`
- cleaned: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/cleaned.jsonl`
- extracted: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/extracted.jsonl`
- titled: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/titled.jsonl`
- output: `/tmp/pytest-of-afio/pytest-24/test_run_indexed_stage_treats_0/jobs_indexed_en.jsonl`

## Counts
- rows_total: 1
- missing_components: 0

## Field Fill Rates
- normalized_title: 1 (100.0%)
- role_family: 1 (100.0%)
- title_clean: 1 (100.0%)
- title_is_other: 1 (100.0%)

## Completeness Flags
- has_salary: 0 (0.0%)
- has_skills: 0 (0.0%)
- has_location: 0 (0.0%)
- title_is_other: 1 (100.0%)

## Sample Indexed Rows
- https://example.com/non-role | title=General Application | normalized=non_role_recruiting_entry | language=en | has_salary=False | has_skills=False | has_location=False | title_is_other=True

## Known Limits
- No ranking or semantic retrieval in this step.
- Composition requires URL-level alignment across upstream artifacts.
- Quality flags are lightweight and deterministic by design.
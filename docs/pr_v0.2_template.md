# PR Template - v0.2

## Title
`v0.2: modularize normalization/tagging and add quality eval artifacts`

## Description
This PR advances the MVP pipeline with v0.2 hardening focused on maintainability and measurable quality, without changing core product scope.

## What’s included

- Refactor: split title normalization into dedicated module
  - `automation/microsaas/title_normalization.py`
- Refactor: split tag extraction into dedicated module
  - `automation/microsaas/tag_extraction.py`
- Go-live reliability: unified smoke E2E script with quality gates
  - `automation/microsaas/smoke_e2e_mvp.sh`
- Title normalization evaluation tooling + artifacts
  - `automation/microsaas/eval_title_normalization.py`
  - `docs/title_normalization_eval.md`
  - `docs/title_normalization_unmatched_top50.csv`
- Skills taxonomy v1 + alias normalization + eval tooling
  - `automation/microsaas/skills_aliases_v1.json`
  - `docs/skills_taxonomy_v1.md`
  - `automation/microsaas/eval_skills_taxonomy.py`
  - `docs/skills_taxonomy_eval.md`
- Documentation updates (technical + checklist + release notes)
  - `docs/mvp_technical_documentation.md`
  - `docs/mvp_go_live_checklist.md`
  - `docs/release_notes_v0.1.0-mvp.md`
  - `docs/title_taxonomy.md`
  - `docs/jobs_indexed_contract.md`

## Quality outcomes

- `other_like` reduced from `21.5%` to `10.75%` on 2000 jobs
- salary outliers (`salary_max > 1,000,000`) = `0`
- tests passing: `24 passed` (`tests/test_microsaas_pipeline_rules.py`)
- smoke E2E passing:
  - pipeline run
  - quality gates
  - API checks (`/v1/indexed/jobs`, `/v1/indexed/filters/options`, semantic fields)

## Scope notes

- No new user-facing features added.
- Behavior preserved while improving internal modularity and evaluation coverage.
- This PR prepares cleaner iteration for post-MVP ranking/taxonomy improvements.

## How to run

```bash
MAX_ROWS=2000 EMBEDDING_MODE=hash ./automation/microsaas/smoke_e2e_mvp.sh \
  data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl \
  data/microsaas/run_smoke \
  data/jobintel_microsaas_smoke.sqlite
```

```bash
PYTHONPATH=. uv run --active pytest -q tests/test_microsaas_pipeline_rules.py
```

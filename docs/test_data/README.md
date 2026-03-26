# Test Data (2k)

This folder contains the canonical 2k test input used for MVP validation.

- file: `raw_jobs_2k.jsonl`
- rows: 2000 JSONL records
- sha256: `f7d85c89f2d8746136ddb2b30ce33eaab0476e5894f134c2081caae29834ba53`

## Rebuild indexed DB from this test set

```bash
uv run --active python automation/microsaas/run_microsaas_pipeline.py \
  --input docs/test_data/raw_jobs_2k.jsonl \
  --output-dir data/microsaas/run_from_docs_test_data_2k \
  --db data/jobintel_microsaas_from_docs_test_data_2k.sqlite \
  --max-rows 2000 \
  --embedding-mode none
```

## Run search quality eval

```bash
uv run --active python automation/microsaas/eval_search_quality.py \
  --db data/jobintel_microsaas_from_docs_test_data_2k.sqlite \
  --queries docs/search_quality_queries_v1.json \
  --out-dir docs/search_quality_eval_v1 \
  --top-k 5 \
  --relevant-threshold 0.75
```

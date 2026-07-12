# Shadow Pipeline v1 (ESCO/O*NET-assisted)

This experiment is separated from the official title classifier and is designed to benchmark a small ESCO/O*NET-assisted recovery batch against a fixed baseline dataset.

## Steps

1. `analyze_residual.py`
2. `esco_lookup.py`
3. `onet_lookup.py`
4. `generate_candidate_clusters.py`
5. `run_shadow_batch.py`

## Example

```bash
uv run --with rapidfuzz python experiments/title_shadow_pipeline/analyze_residual.py \
  --input data/jobs/jobs_titled_en_recovery_v46.jsonl \
  --outdir experiments/title_shadow_pipeline/reports

uv run python experiments/title_shadow_pipeline/esco_lookup.py \
  --esco-dir "ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv" \
  --outdir experiments/title_shadow_pipeline/reports

uv run --with openpyxl python experiments/title_shadow_pipeline/onet_lookup.py \
  --onet-dir ONETfiles \
  --outdir experiments/title_shadow_pipeline/reports

uv run --with rapidfuzz python experiments/title_shadow_pipeline/generate_candidate_clusters.py \
  --input data/jobs/jobs_titled_en_recovery_v46.jsonl \
  --esco-lookup experiments/title_shadow_pipeline/reports/esco_lookup.jsonl \
  --onet-lookup experiments/title_shadow_pipeline/reports/onet_lookup.jsonl \
  --outdir experiments/title_shadow_pipeline/reports

uv run python experiments/title_shadow_pipeline/run_shadow_batch.py \
  --input data/jobs/jobs_titled_en_recovery_v46.jsonl \
  --candidate-report experiments/title_shadow_pipeline/reports/candidate_clusters.json \
  --output data/jobs/jobs_titled_en_shadow_esco_onet_v1.jsonl
```

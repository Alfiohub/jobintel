# Microsaas Eval Runbook (Safe Flow)

Use this sequence to avoid wasting long autolabel runs on invalid inputs.

## 1) Preflight (mandatory)

```bash
uv run --active python automation/microsaas/preflight_eval_check.py \
  --db data/jobintel_microsaas_loccheck_2k_v4.sqlite \
  --min-title-coverage 95 \
  --min-description-coverage 95 \
  --min-country-coverage 20 \
  --strict \
  --out-json docs/review_analysis_locv4/preflight_db.json
```

If this does not print `SAFE TO RUN`, stop and fix data first.

## 2) Build eval sample from validated DB

```bash
uv run --active python automation/microsaas/build_gold_eval_set.py \
  --db data/jobintel_microsaas_loccheck_2k_v4.sqlite \
  --out docs/gold_eval_set_v1_en_locv4.csv \
  --size 800 \
  --seed 42 \
  --source greenhouse \
  --language en \
  --control-seniority \
  --control-location-type \
  --control-salary-presence \
  --target-other-title-share 0.06
```

## 3) Preflight eval CSV (mandatory)

```bash
uv run --active python automation/microsaas/preflight_eval_check.py \
  --db data/jobintel_microsaas_loccheck_2k_v4.sqlite \
  --eval-csv docs/gold_eval_set_v1_en_locv4.csv \
  --min-title-coverage 95 \
  --min-description-coverage 95 \
  --min-eval-rows 800 \
  --strict \
  --out-json docs/review_analysis_locv4/preflight_eval_csv.json
```

## 4) Initialize autolabel output once

```bash
cp docs/gold_eval_set_v1_en_locv4.csv docs/gold_eval_set_v1_en_locv4_autolabeled.csv
```

## 5) Run autolabel in resume mode (safe profile)

Important: use the same file for `--input` and `--out` to resume correctly.

```bash
uv run --active python automation/microsaas/autolabel_gold_eval.py \
  --input docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --out docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --model qwen2.5:7b \
  --min-confidence 0.65 \
  --num-thread 1 \
  --pause-ms 400 \
  --flush-every 5
```

Progress check:

```bash
uv run --active python - <<'PY'
import csv
p="docs/gold_eval_set_v1_en_locv4_autolabeled.csv"
rows=list(csv.DictReader(open(p,encoding="utf-8")))
filled=sum(1 for r in rows if (r.get("label_confidence") or "").strip())
print("rows:",len(rows),"labeled:",filled,"remaining:",len(rows)-filled)
PY
```

## 6) Analyze review categories

```bash
uv run --active python analyze_review_cases.py \
  --input docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --outdir docs/review_analysis_locv4
```

## 7) Compare against baseline

Baseline:
- `docs/review_analysis/review_summary.json`

New:
- `docs/review_analysis_locv4/review_summary.json`

Focus metrics:
- `total_review_rows`
- `counts_by_category.location_without_country`
- `counts_by_primary_review_category.location_without_country`
- top category combinations containing `location_without_country`

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR"

# Optional .env loading
if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

DB_PATH="${1:-data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite}"
RUN_TS="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="docs/taxonomy_nightly/${RUN_TS}"
mkdir -p "$OUT_DIR"

# 1) Expand candidates from current OTHER pool
uv run --active python automation/microsaas/auto_expand_taxonomy.py \
  --db "$DB_PATH" \
  --table jobs_indexed \
  --where "lower(coalesce(normalized_title,''))='other'" \
  --only-other \
  --allow-extend \
  --min-cluster-size 3 \
  --min-confidence 0.65 \
  --out-expansion-csv "$OUT_DIR/taxonomy_expansion_candidates.csv" \
  --out-map-csv "$OUT_DIR/taxonomy_map_existing_candidates.csv" \
  --out-patch-py "$OUT_DIR/taxonomy_patch_candidates.py" \
  --out-summary-md "$OUT_DIR/taxonomy_expansion_summary.md"

# 2) Auto-approve only safe map_existing and apply
uv run --active python automation/microsaas/apply_map_existing_safe.py \
  --candidates-csv "$OUT_DIR/taxonomy_expansion_candidates.csv" \
  --out-patch "$OUT_DIR/taxonomy_patch_map_existing_safe.py" \
  --report-json "$OUT_DIR/taxonomy_map_existing_safe_report.json" \
  --min-confidence 0.85 \
  --min-count 5 \
  --apply

echo "Nightly taxonomy job completed: $OUT_DIR"

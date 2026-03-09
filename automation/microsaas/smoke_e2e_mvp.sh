#!/usr/bin/env bash
set -euo pipefail

INPUT_PATH="${1:-data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl}"
OUT_DIR="${2:-data/microsaas/run_smoke}"
DB_PATH="${3:-data/jobintel_microsaas_smoke.sqlite}"
MAX_ROWS="${MAX_ROWS:-2000}"
EMBEDDING_MODE="${EMBEDDING_MODE:-hash}"
API_PORT="${API_PORT:-8001}"

echo "[1/5] Unit tests (rules)"
PYTHONPATH=. uv run --active pytest -q tests/test_microsaas_pipeline_rules.py

echo "[2/5] Pipeline run"
MAX_ROWS="${MAX_ROWS}" EMBEDDING_MODE="${EMBEDDING_MODE}" \
  ./automation/microsaas/run_microsaas.sh "${INPUT_PATH}" "${OUT_DIR}" "${DB_PATH}"

INDEXED_JSONL="${OUT_DIR}/jobs_indexed.jsonl"
REPORT_JSON="${OUT_DIR}/pipeline_report.json"
if [[ ! -f "${INDEXED_JSONL}" ]]; then
  echo "Missing output: ${INDEXED_JSONL}" >&2
  exit 1
fi
if [[ ! -f "${REPORT_JSON}" ]]; then
  echo "Missing output: ${REPORT_JSON}" >&2
  exit 1
fi

echo "[3/5] Quality gates"
uv run python - <<'PY' "${INDEXED_JSONL}"
import json
import sys
from pathlib import Path

p = Path(sys.argv[1])
rows = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
if not rows:
    raise SystemExit("No indexed rows found")

total = len(rows)
other_like = sum(
    1 for r in rows
    if (r.get("normalized_title") == "other" or r.get("role_family") == "other" or r.get("occupation_group") == "other")
)
salary_outlier = sum(
    1 for r in rows
    if isinstance(r.get("salary_max"), int) and r["salary_max"] > 1_000_000
)
other_pct = round((other_like * 100.0) / total, 2)
print(f"rows={total} other_like={other_like} ({other_pct}%) salary_outlier_gt1M={salary_outlier}")
if other_pct > 12.0:
    raise SystemExit(f"FAIL: other_like {other_pct}% > 12.0%")
if salary_outlier > 0:
    raise SystemExit(f"FAIL: salary_outlier_gt1M {salary_outlier} > 0")
print("PASS: quality gates")
PY

uv run python - <<'PY' "${REPORT_JSON}"
import json
import sys
from pathlib import Path

report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
required = ["processed", "skipped", "updated", "failed", "cache_hits", "runtime_seconds"]
missing = [k for k in required if k not in report]
if missing:
    raise SystemExit(f"FAIL: missing report keys: {missing}")
print(
    "PASS: pipeline report",
    f"processed={report['processed']}",
    f"skipped={report['skipped']}",
    f"updated={report['updated']}",
    f"failed={report['failed']}",
)
PY

echo "[4/5] API smoke"
uv run --active uvicorn jobintel.api:app --port "${API_PORT}" >/tmp/jobintel_smoke_api.log 2>&1 &
API_PID=$!
trap 'kill ${API_PID} >/dev/null 2>&1 || true' EXIT
sleep 2

BASE="http://127.0.0.1:${API_PORT}"
curl -fsS "${BASE}/v1/indexed/jobs?db_path=${DB_PATH}&limit=5" >/tmp/smoke_jobs.json
curl -fsS "${BASE}/v1/indexed/filters/options?db_path=${DB_PATH}" >/tmp/smoke_filters.json
curl -fsS "${BASE}/v1/indexed/jobs?db_path=${DB_PATH}&semantic_query=senior+data+engineer&limit=5" >/tmp/smoke_semantic.json

uv run python - <<'PY'
import json
from pathlib import Path

jobs = json.loads(Path("/tmp/smoke_jobs.json").read_text(encoding="utf-8"))
filters = json.loads(Path("/tmp/smoke_filters.json").read_text(encoding="utf-8"))
semantic = json.loads(Path("/tmp/smoke_semantic.json").read_text(encoding="utf-8"))

def items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("items"), list):
            return payload["items"]
        if isinstance(payload.get("rows"), list):
            return payload["rows"]
    raise AssertionError("items missing")

jobs_items = items(jobs)
semantic_items = items(semantic)

assert isinstance(jobs_items, list), "jobs items invalid"
assert isinstance(filters, dict), "filters payload invalid"
assert isinstance(semantic_items, list), "semantic items invalid"
if semantic_items:
    row = semantic_items[0]
    assert "semantic_score" in row, "semantic_score missing"
    assert "hybrid_score" in row, "hybrid_score missing"
    assert "mismatch_penalty" in row, "mismatch_penalty missing"
print("PASS: api smoke")
PY

echo "[5/5] Done"
echo "Smoke E2E OK"
echo "DB: ${DB_PATH}"
echo "Indexed: ${INDEXED_JSONL}"
echo "Report: ${REPORT_JSON}"

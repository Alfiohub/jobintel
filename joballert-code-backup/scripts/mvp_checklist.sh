#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Checking required files..."
required=(
  "automation/microsaas/search_api.py"
  "automation/microsaas/run_microsaas_pipeline.py"
  "data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite"
  "data/reference/country_aliases.csv"
  "docs/mvp_docker_runbook.md"
)
for f in "${required[@]}"; do
  [[ -f "$f" ]] || { echo "Missing: $f"; exit 1; }
done

echo "[2/5] Checking Python/uv environment..."
uv --version >/dev/null


echo "[3/5] Checking DB readability..."
uv run --active python - <<'PY'
import sqlite3
from pathlib import Path
p = Path("data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite")
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute("select name from sqlite_master where type='table' order by name")
tables = [r[0] for r in cur.fetchall()]
print("tables:", len(tables))
print("sample:", ", ".join(tables[:8]))
conn.close()
PY


echo "[4/5] Checking Search API import..."
uv run --active python - <<'PY'
from automation.microsaas.search_api import app
print("search_api_ok:", bool(app))
PY


echo "[5/5] MVP checklist passed."

#!/usr/bin/env sh
set -eu

APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
INDEXED_INPUT="${JOBINTEL_INDEXED_INPUT:-data/demo/jobs_indexed_demo.jsonl}"
SQLITE_PATH="${JOBINTEL_SQLITE_PATH:-}"
SAVED_DB="${JOBINTEL_SAVED_DB_PATH:-data/jobs/saved_searches.db}"
JOB_STATE_DB="${JOBINTEL_JOB_STATE_DB_PATH:-data/jobs/job_state.db}"
ALERT_RUNS_DIR="${JOBINTEL_ALERT_RUNS_DIR:-data/alerts/runs}"

if [ ! -f "$INDEXED_INPUT" ]; then
  echo "[startup-error] indexed dataset not found: $INDEXED_INPUT" >&2
  exit 1
fi

if [ -n "$SQLITE_PATH" ] && [ ! -f "$SQLITE_PATH" ]; then
  echo "[startup-error] sqlite storage not found: $SQLITE_PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$SAVED_DB")"
mkdir -p "$(dirname "$JOB_STATE_DB")"
mkdir -p "$ALERT_RUNS_DIR"

exec uvicorn jobintel_next.app.api.app:app --host "$APP_HOST" --port "$APP_PORT"

#!/usr/bin/env bash
set -euo pipefail

INPUT_PATH="${1:-data/ner/phase1_greenhouse/all_greenhouse_jobs_en.jsonl}"
OUTPUT_DIR="${2:-data/microsaas/run}"
DB_PATH="${3:-data/jobintel_microsaas.sqlite}"
MAX_ROWS="${MAX_ROWS:-}"
EMBEDDING_MODE="${EMBEDDING_MODE:-hash}"
OPENAI_EMBEDDING_MODEL="${OPENAI_EMBEDDING_MODEL:-text-embedding-3-small}"
GEMINI_EMBEDDING_MODEL="${GEMINI_EMBEDDING_MODEL:-text-embedding-004}"
EMBEDDING_TIMEOUT_SEC="${EMBEDDING_TIMEOUT_SEC:-30}"
EMBEDDING_MAX_CHARS="${EMBEDDING_MAX_CHARS:-4000}"

CMD=(
  uv run python automation/microsaas/run_microsaas_pipeline.py
  --input "$INPUT_PATH"
  --output-dir "$OUTPUT_DIR"
  --db "$DB_PATH"
  --embedding-mode "$EMBEDDING_MODE"
  --openai-embedding-model "$OPENAI_EMBEDDING_MODEL"
  --gemini-embedding-model "$GEMINI_EMBEDDING_MODEL"
  --embedding-timeout-sec "$EMBEDDING_TIMEOUT_SEC"
  --embedding-max-chars "$EMBEDDING_MAX_CHARS"
)

if [[ -n "$MAX_ROWS" ]]; then
  CMD+=(--max-rows "$MAX_ROWS")
fi

echo "+ ${CMD[*]}"
"${CMD[@]}"

echo
echo "Indexed JSONL: $OUTPUT_DIR/jobs_indexed.jsonl"
echo "SQLite DB: $DB_PATH"

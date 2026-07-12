FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data/demo ./data/demo
COPY scripts/container_start.sh ./scripts/container_start.sh

RUN pip install --no-cache-dir .

ENV APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    JOBINTEL_INDEXED_INPUT=data/demo/jobs_indexed_demo.jsonl \
    JOBINTEL_SQLITE_PATH=data/demo/jobs_indexed_demo.db \
    JOBINTEL_SAVED_DB_PATH=data/demo/saved_searches_demo.db \
    JOBINTEL_JOB_STATE_DB_PATH=data/demo/job_state_demo.db \
    JOBINTEL_ALERT_RUNS_DIR=data/demo/alerts/runs \
    JOBINTEL_SESSION_MAX_AGE=43200 \
    JOBINTEL_SESSION_COOKIE_NAME=jobintel_session \
    JOBINTEL_SESSION_HTTPS_ONLY=false \
    JOBINTEL_SESSION_SAME_SITE=lax \
    JOBINTEL_REQUIRE_SESSION_SECRET=false

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status == 200 else 1)"

CMD ["./scripts/container_start.sh"]

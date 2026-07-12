.PHONY: help setup install-dev test lint \
	ingest-export ingest-run build-index \
	run-api run-alerts send-alert-email cleanup-alerts \
	dev smoke demo demo-build demo-init-saved demo-api demo-alerts \
	docker-build docker-run docker-compose-up docker-compose-down \
	run-prod-like deploy-local beta-smoke

PYTHON := uv run
INDEXED_JSON ?= data/jobs/jobs_indexed_en.jsonl
INDEXED_DB ?= data/jobs/jobs_indexed_en.db
SAVED_DB ?= data/jobs/saved_searches.db
ALERT_RUNS_DIR ?= data/alerts/runs
DEMO_INDEXED_JSON ?= data/demo/jobs_indexed_demo.jsonl
DEMO_INDEXED_DB ?= data/demo/jobs_indexed_demo.db
DEMO_SAVED_DB ?= data/demo/saved_searches_demo.db
DEMO_ALERT_RUNS_DIR ?= data/demo/alerts/runs
CONFIG ?= config/default.yml
BOARD ?= found
INGEST_OUT ?= data/jobs/jobs_raw.jsonl
RUN_JSON ?=
EMAIL_TO ?=
DOCKER_IMAGE ?= jobintel-next:demo
ENV_FILE ?= .env
PROD_ENV_FILE ?= .env.production.example
APP_HOST ?= 127.0.0.1
APP_PORT ?= 8000

help:
	@echo "Targets disponibili:"
	@echo "  make setup              -> crea venv e installa dipendenze dev"
	@echo "  make test               -> esegue test"
	@echo "  make lint               -> ruff check"
	@echo "  make ingest-export      -> export board singola (BOARD=$(BOARD))"
	@echo "  make ingest-run         -> ingest YAML (CONFIG=$(CONFIG))"
	@echo "  make build-index        -> build SQLite index da INDEXED_JSON"
	@echo "  make run-api            -> avvia API + Admin UI (APP_PORT=8000 override)"
	@echo "  make run-alerts         -> run-all saved searches abilitate"
	@echo "  make send-alert-email   -> invia email da RUN_JSON (serve EMAIL_TO)"
	@echo "  make cleanup-alerts     -> cleanup artifact alert (KEEP_LAST=20)"
	@echo "  make dev                -> alias di run-api"
	@echo "  make smoke              -> smoke flow MVP minimale"
	@echo "  make demo               -> prepara demo pack (build DB + seed saved searches)"
	@echo "  make demo-api           -> avvia API + Admin UI demo (APP_PORT=8000 override)"
	@echo "  make demo-alerts        -> esegue run-all su dataset demo"
	@echo "  make docker-build       -> build immagine Docker demo"
	@echo "  make docker-run         -> run container API/UI con mount ./data"
	@echo "  make docker-compose-up  -> avvio via docker compose"
	@echo "  make docker-compose-down-> stop compose"
	@echo "  make run-prod-like      -> run Docker single-container con env prod-like"
	@echo "  make deploy-local       -> docker compose up con env prod-like"
	@echo "  make beta-smoke         -> smoke test suite per beta readiness"

setup: install-dev

install-dev:
	uv venv .venv --python 3.11
	. .venv/bin/activate && uv pip install -e .[dev]

test:
	$(PYTHON) pytest -q

lint:
	$(PYTHON) ruff check src tests

ingest-export:
	$(PYTHON) jobintel-next ingest export --source greenhouse --board $(BOARD) --out $(INGEST_OUT)

ingest-run:
	$(PYTHON) jobintel-next ingest run --config $(CONFIG) --out $(INGEST_OUT)

build-index:
	$(PYTHON) jobintel-next storage build-index --input $(INDEXED_JSON) --sqlite $(INDEXED_DB)

run-api:
	JOBINTEL_SQLITE_PATH=$(INDEXED_DB) \
	JOBINTEL_SAVED_DB_PATH=$(SAVED_DB) \
	JOBINTEL_ALERT_RUNS_DIR=$(ALERT_RUNS_DIR) \
	$(PYTHON) uvicorn jobintel_next.app.api.app:app --reload --host $(APP_HOST) --port $(APP_PORT)

dev: run-api

run-alerts:
	$(PYTHON) jobintel-next saved-search run-all \
		--saved-db $(SAVED_DB) \
		--input $(INDEXED_JSON) \
		--sqlite $(INDEXED_DB) \
		--outdir $(ALERT_RUNS_DIR)

send-alert-email:
	@if [ -z "$(RUN_JSON)" ]; then echo "RUN_JSON richiesto"; exit 1; fi
	@if [ -z "$(EMAIL_TO)" ]; then echo "EMAIL_TO richiesto"; exit 1; fi
	$(PYTHON) jobintel-next alerts send-email \
		--run-json $(RUN_JSON) \
		--to $(EMAIL_TO) \
		--smtp-host $$JOBINTEL_SMTP_HOST \
		--smtp-port $${JOBINTEL_SMTP_PORT:-587} \
		--smtp-user $$JOBINTEL_SMTP_USER \
		--smtp-password $$JOBINTEL_SMTP_PASSWORD \
		--from-email $$JOBINTEL_SMTP_FROM

KEEP_LAST ?= 20
cleanup-alerts:
	$(PYTHON) jobintel-next alerts cleanup --outdir $(ALERT_RUNS_DIR) --keep-last $(KEEP_LAST)

smoke:
	$(PYTHON) jobintel-next serve count --input $(INDEXED_JSON) --sqlite $(INDEXED_DB)
	$(PYTHON) jobintel-next saved-search list --saved-db $(SAVED_DB)

demo-build:
	$(PYTHON) jobintel-next storage build-index --input $(DEMO_INDEXED_JSON) --sqlite $(DEMO_INDEXED_DB)

demo-init-saved:
	rm -f $(DEMO_SAVED_DB)
	$(PYTHON) jobintel-next saved-search create \
		--saved-db $(DEMO_SAVED_DB) \
		--name "Demo Python Tech" \
		--query-type filters \
		--filters-json '{"skills_contains":["python"],"title_is_other":false}'
	$(PYTHON) jobintel-next saved-search create \
		--saved-db $(DEMO_SAVED_DB) \
		--name "Demo Remote Data Jobs" \
		--query-type pack \
		--pack-name remote_data_jobs
	$(PYTHON) jobintel-next saved-search create \
		--saved-db $(DEMO_SAVED_DB) \
		--name "Demo High Confidence Tech" \
		--query-type pack \
		--pack-name high_confidence_tech_jobs

demo-alerts:
	$(PYTHON) jobintel-next saved-search run-all \
		--saved-db $(DEMO_SAVED_DB) \
		--input $(DEMO_INDEXED_JSON) \
		--sqlite $(DEMO_INDEXED_DB) \
		--outdir $(DEMO_ALERT_RUNS_DIR)

demo-api:
	JOBINTEL_INDEXED_INPUT=$(DEMO_INDEXED_JSON) \
	JOBINTEL_SQLITE_PATH=$(DEMO_INDEXED_DB) \
	JOBINTEL_SAVED_DB_PATH=$(DEMO_SAVED_DB) \
	JOBINTEL_ALERT_RUNS_DIR=$(DEMO_ALERT_RUNS_DIR) \
	$(PYTHON) uvicorn jobintel_next.app.api.app:app --reload --host $(APP_HOST) --port $(APP_PORT)

demo: demo-build demo-init-saved
	@echo "Demo dataset pronto."
	@echo "Prossimi step:"
	@echo "  1) make demo-alerts"
	@echo "  2) make demo-api"

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	docker run --rm -p $(APP_PORT):$(APP_PORT) \
		-v "$(PWD)/data:/app/data" \
		--env-file $(ENV_FILE) \
		$(DOCKER_IMAGE)

docker-compose-up:
	docker compose --env-file $(ENV_FILE) up --build

docker-compose-down:
	docker compose --env-file $(ENV_FILE) down

run-prod-like:
	docker run --rm -p $(APP_PORT):$(APP_PORT) \
		-v "$(PWD)/data:/app/data" \
		--env-file $(PROD_ENV_FILE) \
		$(DOCKER_IMAGE)

deploy-local:
	docker compose --env-file $(PROD_ENV_FILE) up --build -d

beta-smoke:
	$(PYTHON) pytest -q \
		tests/api/test_auth_session_step43.py \
		tests/api/test_account_preferences_step45.py \
		tests/api/test_saved_searches_api_step27.py \
		tests/api/test_alert_ops_polish_step29.py \
		tests/api/test_admin_ui_step30.py \
		tests/api/test_pilot_readiness_step55.py \
		tests/api/test_deploy_hardening_step54.py \
		tests/product/test_scheduling_step47.py \
		tests/product/test_digest_email_step48.py

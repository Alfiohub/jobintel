# MVP Docker Runbook

## 1) Build + start

```bash
docker compose up --build -d
```

## 2) Open app

- Landing: `http://localhost:8000/`
- Browse: `http://localhost:8000/browse`
- API docs: `http://localhost:8000/docs`

DB default inside container:
- `data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite`

To change DB:

```bash
JOBINTEL_DB_PATH=data/jobintel_microsaas_loccheck_2k_prod_candidate.sqlite docker compose up -d
```

## 3) Logs / stop

```bash
docker compose logs -f mvp-api
docker compose down
```

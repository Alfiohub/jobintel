# Manuale Operativo Pipeline (Microsaas Jobs)

Questo documento spiega **cosa stiamo facendo**, **perché**, e **come eseguire i passi** senza confusione.

## 1) Obiettivo
Trasformare annunci grezzi in dati affidabili per:
- ricerca (`search_api.py`)
- ranking (`ranking.py`)
- analisi qualità continua (eval + review)

## 2) Cosa significa "eval"
`eval` = dataset di controllo (gold set) usato per misurare la qualità dell'estrazione.

File principali:
- `docs/gold_eval_set_v1_en_locv4.csv` = input eval
- `docs/gold_eval_set_v1_en_locv4_autolabeled.csv` = output con predizioni/label
- `docs/review_analysis_locv4/review_summary.json` = metriche finali review

## 3) Cosa significa "review"
`review` = casi sospetti o incompleti (es. country mancante, titolo mancante, salario incompleto).

Le categorie review principali da monitorare:
- `location_without_country`
- `salary_without_period`
- `missing_normalized_title`
- `missing_role_family`

## 4) Flusso standard (ordine corretto)
1. Preflight (sanity check)
2. Autolabel
3. Analyze review
4. Backfill deterministici
5. Analyze review di nuovo
6. (Opzionale) review manuale su coda residua
7. Benchmark search/ranking

## 5) Comandi standard (copy/paste)

### 5.1 Preflight
```bash
uv run --active python automation/microsaas/preflight_eval_check.py \
  --db data/jobintel_microsaas_loccheck_2k_v4.sqlite \
  --eval-csv docs/gold_eval_set_v1_en_locv4.csv \
  --min-title-coverage 95 \
  --min-description-coverage 95 \
  --min-country-coverage 20 \
  --min-eval-rows 800 \
  --strict \
  --out-json docs/review_analysis_locv4/preflight_eval_csv.json
```

### 5.2 Autolabel (resume safe sullo stesso file)
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

### 5.3 Analyze review
```bash
uv run --active python analyze_review_cases.py \
  --input docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --outdir docs/review_analysis_locv4
```

### 5.4 Backfill salario period (deterministico)
```bash
uv run --active python automation/microsaas/backfill_salary_period.py \
  --input docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --output docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --backup \
  --strict \
  --report-json docs/review_analysis_locv4/salary_backfill_apply.json \
  --report-txt docs/review_analysis_locv4/salary_backfill_apply.txt
```

### 5.5 Backfill canonical title (deterministico)
```bash
uv run --active python automation/microsaas/backfill_gold_title_canonical.py \
  --input docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --output docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --backup \
  --strict \
  --queue-csv docs/manual_review_queue.csv \
  --report-json docs/review_analysis_locv4/title_canonical_backfill_apply.json \
  --report-txt docs/review_analysis_locv4/title_canonical_backfill_apply.txt
```

### 5.6 Applica queue manuale (quando pronta)
```bash
uv run --active python automation/microsaas/apply_manual_review_queue.py \
  --gold-csv docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --queue-csv docs/manual_review_queue_filled.csv \
  --output docs/gold_eval_set_v1_en_locv4_autolabeled.csv \
  --backup \
  --strict \
  --report-json docs/review_analysis_locv4/manual_queue_apply.json \
  --report-txt docs/review_analysis_locv4/manual_queue_apply.txt
```

### 5.7 Confronto baseline vs attuale
```bash
uv run --active python - <<'PY'
import json
b=json.load(open('docs/review_analysis/review_summary.json',encoding='utf-8'))
n=json.load(open('docs/review_analysis_locv4/review_summary.json',encoding='utf-8'))
def g(d,k,name): return int(d.get(k,{}).get(name,0))
print('total_review_rows:', b['total_review_rows'], '->', n['total_review_rows'])
for c in ['location_without_country','salary_without_period','missing_normalized_title','missing_role_family']:
    print(c, g(b,'counts_by_category',c), '->', g(n,'counts_by_category',c))
PY
```

## 6) Search/Ranking benchmark rapido

Avvia API:
```bash
uv run --active uvicorn automation.microsaas.search_api:app --host 127.0.0.1 --port 8000
```

Test con DB corretto:
```bash
mkdir -p docs/search_checks
curl -s "http://127.0.0.1:8000/search?db_path=data/jobintel_microsaas_loccheck_2k_v4.sqlite&normalized_title=backend_engineer&country=US&limit=20" > docs/search_checks/q1_backend_us.json
curl -s "http://127.0.0.1:8000/search?db_path=data/jobintel_microsaas_loccheck_2k_v4.sqlite&normalized_title=data_analyst&country=US&location_type=remote&limit=20" > docs/search_checks/q2_data_remote_us.json
curl -s "http://127.0.0.1:8000/search?db_path=data/jobintel_microsaas_loccheck_2k_v4.sqlite&role_family=customer_success&country=US&limit=20" > docs/search_checks/q3_cs_us.json

for f in docs/search_checks/*.json; do
  echo "=== $f ==="
  jq '{total_matched, returned_count, top: (.results[0] // {})}' "$f"
done
```

## 7) Errori comuni e significato
- `skipped: 800` in autolabel: tutte le righe erano già etichettate (comportamento normale).
- `CSV not found`: path sbagliato o file non creato.
- `0 match` su search: spesso DB sbagliato (`db_path` non passato).

## 8) Regola pratica per migliorare qualità
Prima sempre:
1. fix deterministici (ripetibili)
2. poi QA manuale sui residui

Mai il contrario, altrimenti perdi tempo e coerenza.

## 9) Stato corrente (riassunto)
- location migliorata in modo netto
- salary period sistemato
- title canonical migliorato
- ranking/search operativo su DB loccheck_2k_v4
- review manuale residua rinviata (ok)


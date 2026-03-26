# Titles Subsystem

Nuovo sottosistema dedicato solo alla comprensione dei titoli job.

Flusso:
1. `title_raw` -> `title_clean` (`title_cleaning.py`)
2. regole ordinate + fallback controllato (`title_rules.py`, `title_classifier.py`)
3. validazione finale contro tassonomia interna (`title_taxonomy.py`)
4. output spiegabile (`title_schema.py`)

## Responsabilita
- `title_schema.py`: contratti input/output (`TitleInput`, `TitleNormalizationResult`)
- `title_taxonomy.py`: carica `docs/taxonomy_v1_final.csv`, valida mapping
- `title_cleaning.py`: cleaning deterministico del titolo
- `title_rules.py`: regole esplicite con `rule_id`, priorita, note
- `title_classifier.py`: motore end-to-end di classificazione
- `title_evaluation.py`: coverage/reporting
- `title_cli.py`: CLI per test rapidi e batch

## Cosa NON fa
- non gestisce ranking/search/salary/skills
- non persiste su DB
- non usa LLM/ML nel core classifier
- non usa ESCO/O*NET come schema principale

## Esempi CLI

Classifica un titolo:
```bash
uv run --active python -m automation.microsaas.titles.title_cli classify-one --title "Regional Vice President, Sales"
```

Classifica un CSV:
```bash
uv run --active python -m automation.microsaas.titles.title_cli classify-file \
  --input docs/source_job_title_2k.csv \
  --format csv \
  --column title_clean \
  --out docs/title_classification_results.json
```

Coverage report:
```bash
uv run --active python -m automation.microsaas.titles.title_cli coverage-report \
  --input docs/source_job_title_2k.csv \
  --format csv \
  --column title_clean \
  --out docs/title_coverage_report.json
```

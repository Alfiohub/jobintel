# Skills Taxonomy v1

Questa tassonomia definisce il vocabolario canonico skills usato nel pipeline microsaas.

## Obiettivo
- ridurre rumore nei filtri skill
- normalizzare alias/sinonimi in una forma unica
- mantenere compatibilità con estrazione rules-based

## Policy
- Ogni skill estratta viene normalizzata tramite alias map (`skills_aliases_v1.json`).
- I valori canonici sono in `snake_case` dove serve (`power_bi`, `machine_learning`).
- Se un alias non è noto, il valore resta quello estratto.
- Gli aggiornamenti devono essere backward-compatible (no rename distruttivi senza migrazione).

## Canonical Skills (v1)

### Languages
- `python`
- `javascript`
- `typescript`
- `java`
- `sql`

### Data & Analytics
- `postgresql`
- `mysql`
- `snowflake`
- `bigquery`
- `dbt`
- `spark`
- `airflow`
- `databricks`
- `tableau`
- `power_bi`
- `excel`

### Cloud & Platform
- `aws`
- `azure`
- `gcp`
- `docker`
- `kubernetes`
- `terraform`

### Web
- `react`
- `nodejs`

### AI/ML
- `machine_learning`
- `llm`

## Alias Map
- File: `automation/microsaas/skills_aliases_v1.json`
- Esempi:
  - `py` -> `python`
  - `js` -> `javascript`
  - `ts` -> `typescript`
  - `k8s` -> `kubernetes`
  - `node.js` -> `nodejs`
  - `powerbi` -> `power_bi`
  - `ml` -> `machine_learning`

## Change Management
- aggiungere nuovi alias: OK
- aggiungere nuove canonical skill: OK (se usata in almeno N annunci o richiesta prodotto)
- rinominare canonical skill: solo con migrazione dati e update filtri frontend/API

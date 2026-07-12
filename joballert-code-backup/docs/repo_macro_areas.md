# Repo Macro Areas (MVP vs Research)

Data: 2026-03-24

## 1) Core Runtime (MVP candidate)
- `automation/microsaas/`
  - Pipeline ingestion/normalization/autolabel/QA utilities
  - Search API (`search_api.py`) usabile per demo MVP
- `data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite`
  - DB più aggiornato per run MVP
- `docs/mvp_docker_runbook.md`
  - Runbook Docker per test clienti

Uso: questa è l'area da congelare e hardenizzare per rilascio MVP.

## 2) Legacy Runtime (da tenere ma non evolvere ora)
- `src/jobintel/`
  - Vecchia runtime/API/pipeline

Uso: riferimento storico o fallback; non è il target principale per il nuovo MVP.

## 3) Modularization Track (ricerca/medio termine)
- `modules/`
  - Piano di migrazione architetturale
  - Componentizzazione progressiva

Uso: ramo research; non blocca la consegna MVP della settimana.

## 4) Evaluation / QA / Taxonomy Ops
- `automation/microsaas/*taxonomy*`
- `automation/microsaas/auto_expand_taxonomy.py`
- `docs/review_analysis*`
- `docs/taxonomy_*`

Uso: miglioramento qualità modello e riduzione `other`.

## 5) Reference Data
- `data/reference/country_aliases.csv`
- `data/ner/` (dataset input)

Uso: regole deterministiche e dataset sorgente.

## 6) Archived Historical Artifacts
- `docs/archive/20260324_mvp_cleanup/top_level/`
- `data/archive/20260324_mvp_cleanup/db_snapshots/`

Uso: storico completo; non entra nel flusso quotidiano MVP.

## 7) Active MVP Working Set (consigliato)
Lavorare quotidianamente solo su:
- `automation/microsaas/`
- `data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite`
- `data/reference/country_aliases.csv`
- `docs/mvp_docker_runbook.md`
- `docs/mvp_baseline_v2_manifest.json`
- `docs/repo_macro_areas.md`

## 8) Branch Strategy (pratica)
- `main` (o branch base): stabile
- `mvp/prod-hardening`: solo cambi necessari a demo/rilascio
- `research/taxonomy-and-model`: esperimenti, tuning, espansioni tassonomia

Regola:
- dal ramo research al ramo MVP arrivano solo patch piccole, misurate e con rollback semplice.

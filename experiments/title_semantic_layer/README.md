# Title Semantic Layer (Phase E Bootstrap)

Semantic assistance layer in shadow mode for title normalization.

## Scope
- Does **not** modify the official classifier.
- Does **not** auto-promote production rules.
- Generates semantic candidate retrieval + ranking + reviewer artifacts for residual `other`.
- Can apply an experimental taxonomy overlay for semantic-only aliasing and proposed labels.

## Pipeline steps
1. Build internal corpus from taxonomy/rules and matched examples.
1.5. Merge semantic taxonomy overlay aliases/proposed labels into the internal corpus.
2. Build ESCO occupation index.
3. Build O*NET occupation index.
4. Build embedding manifest (semantic-lite fallback).
5. Run semantic retrieval over residual `other` titles.
6. Rank candidates with transparent weighted scoring.
7. Produce reviewer output and strategic report.

## Run
```bash
uv run --with openpyxl --with rapidfuzz python -m experiments.title_semantic_layer.run_semantic_bootstrap
```

```bash
uv run --with openpyxl --with rapidfuzz python -m experiments.title_semantic_layer.phase_e3_targeted_cleanup
```

## Inputs
- Baseline dataset: `data/jobs/jobs_titled_en_recovery_v53_safe.jsonl`
- ESCO: `ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv/*`
- O*NET: `ONETfiles/db_30_2_excel/*.xlsx`

## Outputs
- `experiments/title_semantic_layer/reports/internal_title_corpus.json`
- `experiments/title_semantic_layer/reports/esco_index.jsonl`
- `experiments/title_semantic_layer/reports/onet_index.jsonl`
- `experiments/title_semantic_layer/reports/semantic_retrieval.json`
- `experiments/title_semantic_layer/reports/ranked_candidates.json`
- `experiments/title_semantic_layer/reports/reviewer_output.json`
- `experiments/title_semantic_layer/reports/phase_e_bootstrap_report.json`
- `experiments/title_semantic_layer/reports/phase_e_bootstrap_report_baseline_no_overlay.json`
- `experiments/title_semantic_layer/reports/phase_e_bootstrap_report_overlay_e3.json`
- `experiments/title_semantic_layer/reports/phase_e3_targeted_cleanup_report.json`
- `docs/title_semantic_layer_bootstrap_v1.md`
- `docs/phase_e3_targeted_taxonomy_cleanup_patch.md`

## Notes
- Embedding approach currently uses deterministic local semantic-lite vectors (`hashed_char_trigram_cosine`).
- If stronger local embeddings are added later, keep output format stable for comparability.
- The overlay lives in [taxonomy_overlay.py](/home/afio/Documenti/Code/Python_code/Jinaj/joballert2/experiments/title_semantic_layer/taxonomy_overlay.py) and is branch-local experimentation, not production taxonomy.

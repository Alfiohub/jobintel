# NER Experiments Archive

NER work is preserved for reference but is no longer the primary delivery path.

## Current Decision
- Primary path: micro-SaaS indexing/search pipeline (`ingest -> clean -> normalize_title -> tag -> embed -> index`).
- NER training/annotation assets are experimental and optional.

## Experimental Assets (kept, not deleted)
- `automation/legacy_ner/train_ner_baseline.py`
- `automation/legacy_ner/merge_ner_datasets.py`
- `automation/legacy_ner/split_ner_dataset.py`
- `automation/legacy_ner/run_ner_pipeline.py`
- `automation/legacy_ner/build_ner_subset.py`
- `automation/legacy_ner/weak_label_greenhouse_phase2.py`
- `automation/legacy_ner/export_to_label_studio.py`
- `automation/legacy_ner/import_from_label_studio.py`
- `automation/legacy_ner/export_ner_audit_csv.py`
- `docs/ner_*.md` files
- `data/ner/*`

## Rule
- Do not expand NER scripts as part of the critical production path.
- If revisiting NER, use `data/ner/label_studio/greenhouse_phase2_200_reviewed.jsonl` as benchmark seed.

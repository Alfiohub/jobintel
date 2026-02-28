# NER Pipeline

This pipeline supports the workflow:
- import external labeled data
- merge with internal data
- split into train/valid/test

## One-command pipeline
```bash
uv run --active python scripts/run_ner_pipeline.py \
  --manifest config/examples/ner_pipeline_manifest_example.json \
  --internal-input data/ner/train_preannotated_backfilled.jsonl \
  --work-dir data/ner/pipeline \
  --min-entities 1
```

## Without manifest
If your external data is already converted:
```bash
uv run --active python scripts/run_ner_pipeline.py \
  --internal-input data/ner/train_preannotated_backfilled.jsonl \
  --external-converted data/ner/external/converted/sample_converted.jsonl \
  --work-dir data/ner/pipeline
```

## Outputs
- `data/ner/pipeline/merged.jsonl`
- `data/ner/pipeline/split/train.jsonl`
- `data/ner/pipeline/split/valid.jsonl`
- `data/ner/pipeline/split/test.jsonl`

# Colab Baseline Training

Use the internal baseline split already prepared in this repo:
- `data/ner/pipeline_internal_baseline/split/train.jsonl`
- `data/ner/pipeline_internal_baseline/split/valid.jsonl`
- `data/ner/pipeline_internal_baseline/split/test.jsonl`

## 1. Upload to Colab
Upload these files plus:
- `automation/legacy_ner/train_ner_baseline.py`

## 2. Install deps
```bash
!pip install transformers datasets evaluate seqeval accelerate sentencepiece
```

## 3. Run baseline training
```bash
!python train_ner_baseline.py \
  --train train.jsonl \
  --valid valid.jsonl \
  --test test.jsonl \
  --base-model xlm-roberta-base \
  --output-dir artifacts/ner/baseline_xlmr \
  --epochs 3 \
  --batch-size 4 \
  --learning-rate 3e-5
```

## Notes
- This is a weak-label baseline, not a gold-standard model.
- First goal: get a working model and metrics.
- If Colab RAM is tight, reduce `--batch-size` to `2`.

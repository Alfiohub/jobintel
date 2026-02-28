from __future__ import annotations

import argparse
import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LABELS = [
    'ROLE',
    'SENIORITY',
    'SKILL',
    'WORKPLACE_TYPE',
    'EMPLOYMENT_TYPE',
    'LOCATION',
    'SALARY',
    'FUNCTION_FAMILY',
]


@dataclass(frozen=True)
class PreparedRecord:
    text: str
    entities: list[dict[str, Any]]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:
                raise ValueError(f'invalid JSON at {path}:{line_no}: {e}') from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def build_combined_text(row: dict[str, Any]) -> PreparedRecord:
    title = str(row.get('title') or '')
    description = str(row.get('description_text') or '')
    location = str(row.get('location_raw') or '')
    sections = [
        ('title', title),
        ('description_text', description),
        ('location_raw', location),
    ]

    parts: list[str] = []
    offsets: dict[str, int] = {}
    cursor = 0
    for name, text in sections:
        offsets[name] = cursor
        parts.append(text)
        cursor += len(text)
        parts.append('\n\n')
        cursor += 2
    combined = ''.join(parts[:-1]) if parts else ''

    entities: list[dict[str, Any]] = []
    for ent in row.get('entities', []) if isinstance(row.get('entities'), list) else []:
        if not isinstance(ent, dict):
            continue
        label = str(ent.get('label') or '').strip().upper()
        source_field = str(ent.get('source_field') or '').strip()
        start = ent.get('start')
        end = ent.get('end')
        if label not in LABELS or source_field not in offsets:
            continue
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        shifted_start = offsets[source_field] + start
        shifted_end = offsets[source_field] + end
        if shifted_start < 0 or shifted_end <= shifted_start or shifted_end > len(combined):
            continue
        entities.append(
            {
                'label': label,
                'start': shifted_start,
                'end': shifted_end,
            }
        )
    return PreparedRecord(text=combined, entities=entities)


def to_hf_dataset_dict(path: Path) -> dict[str, list[Any]]:
    rows = read_jsonl(path)
    out = {
        'id': [],
        'text': [],
        'entities': [],
    }
    for idx, row in enumerate(rows):
        prepared = build_combined_text(row)
        out['id'].append(str(row.get('id') or idx))
        out['text'].append(prepared.text)
        out['entities'].append(prepared.entities)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description='Train baseline NER model from project JSONL schema.')
    ap.add_argument('--train', required=True)
    ap.add_argument('--valid', required=True)
    ap.add_argument('--test', required=True)
    ap.add_argument('--base-model', default='xlm-roberta-base')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--epochs', type=int, default=3)
    ap.add_argument('--batch-size', type=int, default=4)
    ap.add_argument('--learning-rate', type=float, default=3e-5)
    ap.add_argument('--max-length', type=int, default=512)
    args = ap.parse_args()

    try:
        import numpy as np
        from datasets import Dataset, DatasetDict
        import evaluate
        from transformers import (
            AutoModelForTokenClassification,
            AutoTokenizer,
            DataCollatorForTokenClassification,
            Trainer,
            TrainingArguments,
        )
    except ModuleNotFoundError as e:
        raise RuntimeError(
            'Missing training dependencies. Install in Colab/local with: '\
            'pip install transformers datasets evaluate seqeval accelerate sentencepiece'
        ) from e

    label_list = ['O']
    for label in LABELS:
        label_list.append(f'B-{label}')
        label_list.append(f'I-{label}')
    label_to_id = {label: i for i, label in enumerate(label_list)}
    id_to_label = {i: label for label, i in label_to_id.items()}

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)

    dataset = DatasetDict(
        {
            'train': Dataset.from_dict(to_hf_dataset_dict(Path(args.train))),
            'valid': Dataset.from_dict(to_hf_dataset_dict(Path(args.valid))),
            'test': Dataset.from_dict(to_hf_dataset_dict(Path(args.test))),
        }
    )

    def tokenize_and_align_labels(batch: dict[str, list[Any]]) -> dict[str, Any]:
        tokenized = tokenizer(
            batch['text'],
            truncation=True,
            max_length=args.max_length,
            return_offsets_mapping=True,
        )
        labels_batch: list[list[int]] = []
        for i, offsets in enumerate(tokenized['offset_mapping']):
            entities = batch['entities'][i]
            word_ids = tokenized.word_ids(batch_index=i)
            labels: list[int] = []
            prev_word_id = None
            for token_idx, (start, end) in enumerate(offsets):
                word_id = word_ids[token_idx]
                if word_id is None or (start == 0 and end == 0):
                    labels.append(-100)
                    continue
                token_label = 'O'
                for ent in entities:
                    ent_start = int(ent['start'])
                    ent_end = int(ent['end'])
                    ent_label = str(ent['label'])
                    if start >= ent_start and end <= ent_end:
                        prefix = 'I'
                        if start == ent_start or word_id != prev_word_id:
                            prefix = 'B' if start == ent_start else 'I'
                        token_label = f'{prefix}-{ent_label}'
                        break
                labels.append(label_to_id.get(token_label, 0))
                prev_word_id = word_id
            labels_batch.append(labels)
        tokenized['labels'] = labels_batch
        tokenized.pop('offset_mapping', None)
        return tokenized

    encoded = dataset.map(tokenize_and_align_labels, batched=True, remove_columns=dataset['train'].column_names)

    metric = evaluate.load('seqeval')

    def compute_metrics(eval_pred: Any) -> dict[str, float]:
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        true_predictions: list[list[str]] = []
        true_labels: list[list[str]] = []
        for pred_row, lab_row in zip(predictions, labels):
            pred_labels: list[str] = []
            true_lab_labels: list[str] = []
            for pred_id, lab_id in zip(pred_row, lab_row):
                if lab_id == -100:
                    continue
                pred_labels.append(id_to_label[int(pred_id)])
                true_lab_labels.append(id_to_label[int(lab_id)])
            true_predictions.append(pred_labels)
            true_labels.append(true_lab_labels)
        result = metric.compute(predictions=true_predictions, references=true_labels)
        return {
            'precision': float(result.get('overall_precision', 0.0)),
            'recall': float(result.get('overall_recall', 0.0)),
            'f1': float(result.get('overall_f1', 0.0)),
            'accuracy': float(result.get('overall_accuracy', 0.0)),
        }

    model = AutoModelForTokenClassification.from_pretrained(
        args.base_model,
        num_labels=len(label_list),
        id2label=id_to_label,
        label2id=label_to_id,
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        eval_strategy='epoch',
        save_strategy='epoch',
        logging_strategy='steps',
        logging_steps=50,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        greater_is_better=True,
        save_total_limit=2,
        report_to='none',
    )

    trainer = Trainer(
        **(
            {
                'model': model,
                'args': training_args,
                'train_dataset': encoded['train'],
                'eval_dataset': encoded['valid'],
                'data_collator': DataCollatorForTokenClassification(tokenizer=tokenizer),
                'compute_metrics': compute_metrics,
                # Newer transformers versions replaced `tokenizer=` with `processing_class=`.
                ('processing_class' if 'processing_class' in inspect.signature(Trainer.__init__).parameters else 'tokenizer'): tokenizer,
            }
        )
    )

    trainer.train()
    test_metrics = trainer.evaluate(encoded['test'])
    print('Test metrics:', test_metrics)
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == '__main__':
    main()

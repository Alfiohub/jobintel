from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            obj = json.loads(s)
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def build_text(row: dict[str, Any]) -> str:
    return "\n\n".join(
        [
            str(row.get('title') or ''),
            str(row.get('description_text') or ''),
            str(row.get('location_raw') or ''),
        ]
    )


def main() -> None:
    ap = argparse.ArgumentParser(description='Inspect NER model predictions on JSONL rows.')
    ap.add_argument('--model-dir', required=True)
    ap.add_argument('--input', required=True)
    ap.add_argument('--limit', type=int, default=3)
    ap.add_argument('--threshold', type=float, default=0.5)
    args = ap.parse_args()

    try:
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
    except ModuleNotFoundError as e:
        raise RuntimeError('Install NER extras first: uv pip install -e ".[ner]"') from e

    model_dir = Path(args.model_dir)
    rows = read_jsonl(Path(args.input))[: max(0, args.limit)]
    if not rows:
        raise ValueError('No input rows found')

    tokenizer = AutoTokenizer.from_pretrained(str(model_dir), use_fast=True)
    model = AutoModelForTokenClassification.from_pretrained(str(model_dir))
    device = 0 if torch.cuda.is_available() else -1
    ner = pipeline(
        'token-classification',
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy='simple',
        device=device,
    )

    for idx, row in enumerate(rows, start=1):
        text = build_text(row)
        preds = ner(text)
        print(f'--- row {idx} id={row.get("id")} title={row.get("title")}')
        print(f'gold_entities={len(row.get("entities", [])) if isinstance(row.get("entities"), list) else 0}')
        kept = [p for p in preds if float(p.get('score', 0.0)) >= args.threshold]
        print(f'pred_entities={len(kept)} threshold={args.threshold}')
        for p in kept[:20]:
            print({
                'entity_group': p.get('entity_group'),
                'score': round(float(p.get('score', 0.0)), 4),
                'word': p.get('word'),
                'start': p.get('start'),
                'end': p.get('end'),
            })


if __name__ == '__main__':
    main()

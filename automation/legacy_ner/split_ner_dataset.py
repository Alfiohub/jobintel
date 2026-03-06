from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def group_value(row: dict[str, Any], group_key: str) -> str:
    if group_key == 'company_name':
        value = row.get('company_name') or row.get('company') or ''
    elif group_key == 'source':
        value = row.get('source') or ''
    else:
        value = row.get(group_key) or ''
    txt = str(value).strip()
    if txt:
        return txt
    return f"__missing__:{row.get('id') or hash(str(row))}"


def main() -> None:
    ap = argparse.ArgumentParser(description='Split NER JSONL dataset by group key to reduce leakage.')
    ap.add_argument('--input', required=True, help='Merged JSONL path')
    ap.add_argument('--output-dir', required=True, help='Output directory')
    ap.add_argument('--train-ratio', type=float, default=0.8)
    ap.add_argument('--valid-ratio', type=float, default=0.1)
    ap.add_argument('--test-ratio', type=float, default=0.1)
    ap.add_argument('--group-key', default='company_name', help='Grouping field for anti-leak split')
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    total = args.train_ratio + args.valid_ratio + args.test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError('train/valid/test ratios must sum to 1.0')

    rows = read_jsonl(Path(args.input))
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(group_value(row, args.group_key), []).append(row)

    keys = list(buckets)
    rnd = random.Random(args.seed)
    rnd.shuffle(keys)

    total_rows = len(rows)
    train_target = total_rows * args.train_ratio
    valid_target = total_rows * args.valid_ratio

    train_rows: list[dict[str, Any]] = []
    valid_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    for key in keys:
        bucket = buckets[key]
        if len(train_rows) < train_target:
            train_rows.extend(bucket)
        elif len(valid_rows) < valid_target:
            valid_rows.extend(bucket)
        else:
            test_rows.extend(bucket)

    out_dir = Path(args.output_dir)
    write_jsonl(out_dir / 'train.jsonl', train_rows)
    write_jsonl(out_dir / 'valid.jsonl', valid_rows)
    write_jsonl(out_dir / 'test.jsonl', test_rows)

    print(f'Input rows: {len(rows)}')
    print(f'Train rows: {len(train_rows)}')
    print(f'Valid rows: {len(valid_rows)}')
    print(f'Test rows: {len(test_rows)}')
    print(f'Wrote: {out_dir}')


if __name__ == '__main__':
    main()

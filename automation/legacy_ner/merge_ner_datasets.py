from __future__ import annotations

import argparse
import hashlib
import json
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


def row_key(row: dict[str, Any]) -> str:
    rid = str(row.get('id') or '').strip()
    if rid:
        return f'id:{rid}'

    payload = '|'.join(
        [
            str(row.get('source') or ''),
            str(row.get('company_name') or ''),
            str(row.get('title') or ''),
            str(row.get('location_raw') or ''),
            str(row.get('description_text') or '')[:500],
        ]
    )
    return 'fp:' + hashlib.sha1(payload.encode('utf-8')).hexdigest()[:20]


def entity_count(row: dict[str, Any]) -> int:
    entities = row.get('entities')
    return len(entities) if isinstance(entities, list) else 0


def score_row(row: dict[str, Any]) -> tuple[int, int]:
    status = str(row.get('annotation_status') or '').strip().lower()
    status_rank = {
        'openai_annotated': 5,
        'converted': 4,
        'preannotated': 3,
        'todo': 2,
        'openai_error': 1,
    }.get(status, 0)
    return (status_rank, entity_count(row))


def choose_better(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    return new if score_row(new) > score_row(old) else old


def main() -> None:
    ap = argparse.ArgumentParser(description='Merge NER JSONL datasets with simple dedup.')
    ap.add_argument('--input', dest='inputs', action='append', required=True, help='Input JSONL path (repeatable)')
    ap.add_argument('--output', required=True, help='Merged output JSONL path')
    ap.add_argument('--min-entities', type=int, default=0, help='Keep only rows with at least N entities')
    ap.add_argument('--require-nonempty-text', action='store_true', help='Drop rows without title and description_text')
    args = ap.parse_args()

    merged: dict[str, dict[str, Any]] = {}
    seen_inputs = 0

    for raw_path in args.inputs:
        path = Path(raw_path)
        rows = read_jsonl(path)
        seen_inputs += len(rows)
        for row in rows:
            if args.require_nonempty_text:
                title = str(row.get('title') or '').strip()
                desc = str(row.get('description_text') or '').strip()
                if not title and not desc:
                    continue
            if entity_count(row) < args.min_entities:
                continue
            key = row_key(row)
            prev = merged.get(key)
            merged[key] = row if prev is None else choose_better(prev, row)

    out_rows = list(merged.values())
    out_rows.sort(key=lambda r: (
        str(r.get('source') or ''),
        str(r.get('company_name') or ''),
        str(r.get('title') or ''),
        str(r.get('id') or ''),
    ))
    write_jsonl(Path(args.output), out_rows)

    print(f'Input rows: {seen_inputs}')
    print(f'Output rows: {len(out_rows)}')
    print(f'Wrote: {args.output}')


if __name__ == '__main__':
    main()

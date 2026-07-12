from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ENGLISH_HINTS = {
    'the',
    'and',
    'with',
    'experience',
    'requirements',
    'job',
    'description',
    'qualifications',
    'skills',
    'work',
    'team',
    'role',
    'responsible',
    'years',
    'degree',
    'preferred',
    'benefits',
    'salary',
    'location',
}


def _extract_text_for_language(row: dict[str, Any]) -> str:
    raw_payload = row.get('raw_payload')
    raw_content = ''
    raw_location = ''
    if isinstance(raw_payload, dict):
        content = raw_payload.get('content')
        if isinstance(content, str):
            raw_content = content[:2000]
        location = raw_payload.get('location')
        if isinstance(location, dict):
            raw_location = str(location.get('name') or '')
        elif isinstance(location, str):
            raw_location = location
    return ' '.join(
        [
            str(row.get('title') or ''),
            str(row.get('description_text') or '')[:2000],
            raw_content,
            str(row.get('location_raw') or ''),
            raw_location,
        ]
    ).lower()


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


def looks_english(row: dict[str, Any], min_hits: int) -> bool:
    language = str(row.get('language') or '').strip().lower()
    if language.startswith('en'):
        return True
    raw_payload = row.get('raw_payload')
    if isinstance(raw_payload, dict):
        raw_language = str(raw_payload.get('language') or '').strip().lower()
        if raw_language.startswith('en'):
            return True

    text = _extract_text_for_language(row)
    tokens = re.findall(r'[a-z]+', text)
    if not tokens:
        return False
    hits = sum(token in ENGLISH_HINTS for token in tokens)
    return hits >= min_hits


def main() -> None:
    ap = argparse.ArgumentParser(description='Build a filtered NER subset from project JSONL data.')
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--source', help='Keep only a specific source value, e.g. greenhouse')
    ap.add_argument('--english-only', action='store_true', help='Apply a lightweight English heuristic')
    ap.add_argument('--min-english-hits', type=int, default=5)
    ap.add_argument('--min-entities', type=int, default=0)
    args = ap.parse_args()

    rows = read_jsonl(Path(args.input))
    kept: list[dict[str, Any]] = []
    for row in rows:
        if args.source and str(row.get('source') or '').strip().lower() != args.source.strip().lower():
            continue
        entities = row.get('entities')
        entity_count = len(entities) if isinstance(entities, list) else 0
        if entity_count < args.min_entities:
            continue
        if args.english_only and not looks_english(row, args.min_english_hits):
            continue
        kept.append(row)

    write_jsonl(Path(args.output), kept)
    print(f'Input rows: {len(rows)}')
    print(f'Output rows: {len(kept)}')
    print(f'Wrote: {args.output}')


if __name__ == '__main__':
    main()

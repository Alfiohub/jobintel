from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {e}") from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def sample_rows(rows: list[dict[str, Any]], sample_size: int, seed: int) -> list[dict[str, Any]]:
    if sample_size >= len(rows):
        return list(rows)
    rnd = random.Random(seed)
    idxs = sorted(rnd.sample(range(len(rows)), sample_size))
    return [rows[i] for i in idxs]


def build_combined_text(row: dict[str, Any]) -> tuple[str, dict[str, int]]:
    title = str(row.get("title") or "")
    location = str(row.get("location_raw") or "")
    description = str(row.get("description_text") or "")
    sections = [
        ("title", title),
        ("location_raw", location),
        ("description_text", description),
    ]
    parts: list[str] = []
    offsets: dict[str, int] = {}
    cursor = 0
    for name, text in sections:
        offsets[name] = cursor
        parts.append(text)
        cursor += len(text)
        parts.append("\n\n")
        cursor += 2
    combined = "".join(parts[:-1]) if parts else ""
    return combined, offsets


def convert_entities(row: dict[str, Any], text: str, offsets: dict[str, int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    entities = row.get("entities")
    if not isinstance(entities, list):
        return out

    for idx, ent in enumerate(entities):
        if not isinstance(ent, dict):
            continue
        source_field = str(ent.get("source_field") or "").strip()
        label = str(ent.get("label") or "").strip()
        start = ent.get("start")
        end = ent.get("end")
        if source_field not in offsets or not label:
            continue
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        global_start = offsets[source_field] + start
        global_end = offsets[source_field] + end
        if global_start < 0 or global_end <= global_start or global_end > len(text):
            continue
        span_text = text[global_start:global_end]
        out.append(
            {
                "id": f"ent-{row.get('id') or 'row'}-{idx}",
                "type": "labels",
                "from_name": "label",
                "to_name": "text",
                "origin": "prediction",
                "value": {
                    "start": global_start,
                    "end": global_end,
                    "text": span_text,
                    "labels": [label],
                },
            }
        )
    return out


def to_label_studio_task(row: dict[str, Any]) -> dict[str, Any]:
    text, offsets = build_combined_text(row)
    predictions = convert_entities(row, text, offsets)
    task = {
        "data": {
            "id": str(row.get("id") or ""),
            "text": text,
            "title": str(row.get("title") or ""),
            "company_name": str(row.get("company_name") or ""),
            "location_raw": str(row.get("location_raw") or ""),
            "url": str(row.get("url") or ""),
        },
        "meta": {
            "source": str(row.get("source") or ""),
            "annotation_status": str(row.get("annotation_status") or ""),
            "language": str(row.get("language") or ""),
        },
    }
    if predictions:
        task["predictions"] = [{"model_version": "phase2_weak_labels", "result": predictions}]
    return task


def write_json(path: Path, tasks: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Export project NER JSONL to Label Studio import JSON.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--sample-size", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = read_jsonl(Path(args.input))
    sampled = sample_rows(rows, max(1, args.sample_size), args.seed)
    tasks = [to_label_studio_task(row) for row in sampled]
    write_json(Path(args.output), tasks)
    print(f"Input rows: {len(rows)}")
    print(f"Sample rows: {len(tasks)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

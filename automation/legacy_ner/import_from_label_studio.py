from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_offsets(row: dict[str, Any]) -> dict[str, tuple[int, int]]:
    title = str(row.get("title") or "")
    location = str(row.get("location_raw") or "")
    description = str(row.get("description_text") or "")
    sections = [
        ("title", title),
        ("location_raw", location),
        ("description_text", description),
    ]
    out: dict[str, tuple[int, int]] = {}
    cursor = 0
    for name, text in sections:
        start = cursor
        end = start + len(text)
        out[name] = (start, end)
        cursor = end + 2
    return out


def find_source_field(offsets: dict[str, tuple[int, int]], start: int, end: int) -> tuple[str, int, int] | None:
    for field_name in ("title", "location_raw", "description_text"):
        field_start, field_end = offsets[field_name]
        if start >= field_start and end <= field_end:
            return field_name, start - field_start, end - field_start
    return None


def latest_active_annotation(task: dict[str, Any]) -> dict[str, Any] | None:
    annotations = task.get("annotations")
    if not isinstance(annotations, list):
        return None
    active = [ann for ann in annotations if isinstance(ann, dict) and not ann.get("was_cancelled")]
    if not active:
        return None
    active.sort(key=lambda ann: str(ann.get("updated_at") or ann.get("created_at") or ""))
    return active[-1]


def convert_results(task: dict[str, Any], row: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = latest_active_annotation(task)
    if annotation is None:
        return []
    results = annotation.get("result")
    if not isinstance(results, list):
        return []

    offsets = build_offsets(row)
    entities: list[dict[str, Any]] = []
    seen: set[tuple[str, int, int, str]] = set()

    for result in results:
        if not isinstance(result, dict):
            continue
        if result.get("type") != "labels":
            continue
        value = result.get("value")
        if not isinstance(value, dict):
            continue
        labels = value.get("labels")
        if not isinstance(labels, list) or len(labels) != 1:
            continue
        label = str(labels[0] or "").strip()
        start = value.get("start")
        end = value.get("end")
        if not isinstance(start, int) or not isinstance(end, int) or end <= start:
            continue
        found = find_source_field(offsets, start, end)
        if found is None:
            continue
        source_field, local_start, local_end = found
        field_text = str(row.get(source_field) or "")
        span_text = field_text[local_start:local_end]
        key = (source_field, local_start, local_end, label)
        if key in seen or not span_text.strip():
            continue
        seen.add(key)
        entities.append(
            {
                "label": label,
                "text": span_text,
                "source_field": source_field,
                "start": local_start,
                "end": local_end,
            }
        )

    entities.sort(key=lambda ent: (str(ent["source_field"]), int(ent["start"]), int(ent["end"]), str(ent["label"])))
    return entities


def main() -> None:
    ap = argparse.ArgumentParser(description="Import Label Studio JSON export back into project JSONL format.")
    ap.add_argument("--label-studio-export", required=True)
    ap.add_argument("--base-input", required=True, help="Original project JSONL used to create Label Studio tasks")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    tasks = read_json(Path(args.label_studio_export))
    if not isinstance(tasks, list):
        raise ValueError("Label Studio export must be a JSON list")
    base_rows = read_jsonl(Path(args.base_input))
    rows_by_id = {str(row.get("id") or "").strip(): row for row in base_rows}

    out_rows: list[dict[str, Any]] = []
    skipped_missing = 0
    skipped_unannotated = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        data = task.get("data")
        if not isinstance(data, dict):
            continue
        row_id = str(data.get("id") or "").strip()
        base_row = rows_by_id.get(row_id)
        if base_row is None:
            skipped_missing += 1
            continue
        entities = convert_results(task, base_row)
        if not entities:
            skipped_unannotated += 1
            continue
        new_row = dict(base_row)
        new_row["entities"] = entities
        new_row["annotation_status"] = "preannotated"
        out_rows.append(new_row)

    write_jsonl(Path(args.output), out_rows)
    print(f"Input tasks: {len(tasks)}")
    print(f"Output rows: {len(out_rows)}")
    print(f"Skipped missing ids: {skipped_missing}")
    print(f"Skipped without active annotations: {skipped_unannotated}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

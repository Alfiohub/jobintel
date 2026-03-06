from __future__ import annotations

import argparse
import csv
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


def format_entities(row: dict[str, Any]) -> str:
    parts: list[str] = []
    entities = row.get("entities")
    if not isinstance(entities, list):
        return ""
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        label = str(entity.get("label") or "").strip()
        text = str(entity.get("text") or "").strip().replace("\n", " ")
        if label and text:
            parts.append(f"{label}: {text}")
    return " | ".join(parts)


def preview(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def sample_rows(rows: list[dict[str, Any]], sample_size: int, seed: int) -> list[dict[str, Any]]:
    if sample_size >= len(rows):
        return list(rows)
    rnd = random.Random(seed)
    idxs = sorted(rnd.sample(range(len(rows)), sample_size))
    return [rows[i] for i in idxs]


def write_csv(path: Path, rows: list[dict[str, Any]], preview_chars: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "company_name",
                "title",
                "location_raw",
                "url",
                "description_preview",
                "current_entities",
                "audit_status",
                "missing_labels",
                "wrong_labels",
                "correct_labels_to_add",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": str(row.get("id") or ""),
                    "company_name": str(row.get("company_name") or ""),
                    "title": str(row.get("title") or ""),
                    "location_raw": str(row.get("location_raw") or ""),
                    "url": str(row.get("url") or ""),
                    "description_preview": preview(str(row.get("description_text") or ""), preview_chars),
                    "current_entities": format_entities(row),
                    "audit_status": "",
                    "missing_labels": "",
                    "wrong_labels": "",
                    "correct_labels_to_add": "",
                    "notes": "",
                }
            )


def main() -> None:
    ap = argparse.ArgumentParser(description="Export a human-friendly CSV sample for manual NER audit.")
    ap.add_argument("--input", required=True, help="Input JSONL dataset")
    ap.add_argument("--output", required=True, help="Output CSV path")
    ap.add_argument("--sample-size", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--preview-chars", type=int, default=700)
    args = ap.parse_args()

    rows = read_jsonl(Path(args.input))
    sampled = sample_rows(rows, sample_size=max(1, args.sample_size), seed=args.seed)
    write_csv(Path(args.output), sampled, preview_chars=max(100, args.preview_chars))
    print(f"Input rows: {len(rows)}")
    print(f"Sample rows: {len(sampled)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

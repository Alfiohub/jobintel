from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_LABELS = {
    "ROLE",
    "SENIORITY",
    "SKILL",
    "WORKPLACE_TYPE",
    "EMPLOYMENT_TYPE",
    "LOCATION",
    "SALARY",
    "FUNCTION_FAMILY",
}
ALLOWED_SOURCE_FIELDS = {"title", "description_text", "location_raw"}

BUILTIN_LABEL_MAP = {
    "TITLE": "ROLE",
    "JOB_TITLE": "ROLE",
    "POSITION": "ROLE",
    "EXPERIENCE": "SENIORITY",
    "LEVEL": "SENIORITY",
    "WORK_MODE": "WORKPLACE_TYPE",
    "WORKPLACE": "WORKPLACE_TYPE",
    "CONTRACT": "EMPLOYMENT_TYPE",
    "EMPLOYMENT": "EMPLOYMENT_TYPE",
    "CITY": "LOCATION",
    "COUNTRY": "LOCATION",
    "GPE": "LOCATION",
    "MONEY": "SALARY",
    "DEPARTMENT": "FUNCTION_FAMILY",
    "FUNCTION": "FUNCTION_FAMILY",
    "SKILLS": "SKILL",
    "TECH_SKILL": "SKILL",
    "SOFT_SKILL": "SKILL",
}

SOURCE_FIELD_MAP = {
    "title": "title",
    "job_title": "title",
    "description": "description_text",
    "description_text": "description_text",
    "text": "description_text",
    "body": "description_text",
    "location": "location_raw",
    "location_raw": "location_raw",
}


def read_input(path: Path) -> list[dict[str, Any]]:
    sfx = path.suffix.lower()
    if sfx == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, list):
            return [r for r in obj if isinstance(r, dict)]
        if isinstance(obj, dict) and isinstance(obj.get("data"), list):
            return [r for r in obj["data"] if isinstance(r, dict)]
        raise ValueError("JSON input must be a list of objects or {data:[...]} ")

    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            txt = line.strip()
            if not txt:
                continue
            try:
                obj = json.loads(txt)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON at line {line_no}: {e}") from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _pick_text(row: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        v = row.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def _normalize_source_field(raw: Any, default_source_field: str) -> str:
    key = str(raw or "").strip().lower()
    if key in SOURCE_FIELD_MAP:
        return SOURCE_FIELD_MAP[key]
    if default_source_field in ALLOWED_SOURCE_FIELDS:
        return default_source_field
    return "description_text"


def _normalize_label(raw: Any, extra_label_map: dict[str, str]) -> str:
    label = str(raw or "").strip().upper()
    if not label:
        return ""
    if label in extra_label_map:
        label = extra_label_map[label]
    elif label in BUILTIN_LABEL_MAP:
        label = BUILTIN_LABEL_MAP[label]
    return label


def _extract_entities_from_spans(
    row: dict[str, Any],
    default_source_field: str,
    extra_label_map: dict[str, str],
) -> tuple[list[dict[str, Any]], int]:
    spans = row.get("entities")
    if not isinstance(spans, list):
        spans = row.get("spans")
    if not isinstance(spans, list):
        spans = row.get("annotations")
    if not isinstance(spans, list):
        return [], 0

    title = _pick_text(row, ["title", "job_title"])
    description_text = _pick_text(row, ["description_text", "description", "text", "body"])
    location_raw = _pick_text(row, ["location_raw", "location"])
    source_text = {
        "title": title,
        "description_text": description_text,
        "location_raw": location_raw,
    }

    out: list[dict[str, Any]] = []
    skipped = 0
    seen: set[tuple[str, str, int, int]] = set()

    for ent in spans:
        if not isinstance(ent, dict):
            skipped += 1
            continue

        label = _normalize_label(ent.get("label") or ent.get("type") or ent.get("tag"), extra_label_map)
        source_field = _normalize_source_field(ent.get("source_field") or ent.get("field"), default_source_field)
        start = ent.get("start")
        end = ent.get("end")
        if start is None:
            start = ent.get("begin")
        if end is None:
            end = ent.get("stop")

        if label not in ALLOWED_LABELS or source_field not in ALLOWED_SOURCE_FIELDS:
            skipped += 1
            continue
        if not isinstance(start, int) or not isinstance(end, int):
            skipped += 1
            continue
        text = source_text.get(source_field, "")
        if start < 0 or end <= start or end > len(text):
            skipped += 1
            continue

        span_text = text[start:end]
        if not span_text.strip():
            skipped += 1
            continue

        key = (label, source_field, start, end)
        if key in seen:
            continue
        seen.add(key)

        out.append(
            {
                "label": label,
                "text": span_text,
                "source_field": source_field,
                "start": start,
                "end": end,
            }
        )

    out.sort(key=lambda x: (x["source_field"], x["start"], x["end"], x["label"]))
    return out, skipped


def _extract_entities_from_bio(
    row: dict[str, Any],
    default_source_field: str,
    extra_label_map: dict[str, str],
) -> tuple[list[dict[str, Any]], str, int]:
    tokens = row.get("tokens")
    tags = row.get("ner_tags")
    if not isinstance(tags, list):
        tags = row.get("tags")
    if not isinstance(tags, list):
        tags = row.get("labels")
    if not isinstance(tokens, list) or not isinstance(tags, list) or len(tokens) != len(tags):
        return [], "", 0

    token_text = [str(t) for t in tokens]
    text = " ".join(token_text)

    offsets: list[tuple[int, int]] = []
    pos = 0
    for tok in token_text:
        start = pos
        end = start + len(tok)
        offsets.append((start, end))
        pos = end + 1

    out: list[dict[str, Any]] = []
    skipped = 0
    i = 0
    source_field = default_source_field if default_source_field in ALLOWED_SOURCE_FIELDS else "description_text"

    while i < len(tags):
        raw = str(tags[i])
        if raw == "O":
            i += 1
            continue

        if "-" in raw:
            prefix, lbl_raw = raw.split("-", 1)
            prefix = prefix.upper()
        else:
            prefix = "B"
            lbl_raw = raw

        label = _normalize_label(lbl_raw, extra_label_map)
        if label not in ALLOWED_LABELS:
            skipped += 1
            i += 1
            continue

        if prefix not in {"B", "I"}:
            i += 1
            continue

        start_idx = i
        end_idx = i
        i += 1
        while i < len(tags):
            nxt = str(tags[i])
            if "-" in nxt:
                nxt_prefix, nxt_lbl_raw = nxt.split("-", 1)
                nxt_prefix = nxt_prefix.upper()
            else:
                nxt_prefix = "B"
                nxt_lbl_raw = nxt
            nxt_label = _normalize_label(nxt_lbl_raw, extra_label_map)
            if nxt_prefix == "I" and nxt_label == label:
                end_idx = i
                i += 1
                continue
            break

        start = offsets[start_idx][0]
        end = offsets[end_idx][1]
        span_text = text[start:end]
        if not span_text.strip():
            skipped += 1
            continue

        out.append(
            {
                "label": label,
                "text": span_text,
                "source_field": source_field,
                "start": start,
                "end": end,
            }
        )

    return out, text, skipped


def _load_label_map(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    p = Path(path)
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("label map must be a JSON object")

    out: dict[str, str] = {}
    for k, v in obj.items():
        kk = str(k).strip().upper()
        vv = str(v).strip().upper()
        if not kk or vv not in ALLOWED_LABELS:
            continue
        out[kk] = vv
    return out


def convert_row(
    row: dict[str, Any],
    idx: int,
    dataset_name: str,
    default_source_field: str,
    status: str,
    extra_label_map: dict[str, str],
    id_prefix: str,
) -> tuple[dict[str, Any], int]:
    row_id = row.get("id") or row.get("uuid") or row.get("job_id") or f"{id_prefix}-{idx}"

    title = _pick_text(row, ["title", "job_title"])
    description_text = _pick_text(row, ["description_text", "description", "text", "body"])
    location_raw = _pick_text(row, ["location_raw", "location"])

    entities, skipped_spans = _extract_entities_from_spans(
        row=row,
        default_source_field=default_source_field,
        extra_label_map=extra_label_map,
    )

    skipped_bio = 0
    if not entities:
        bio_entities, bio_text, skipped_bio = _extract_entities_from_bio(
            row=row,
            default_source_field=default_source_field,
            extra_label_map=extra_label_map,
        )
        if bio_entities:
            entities = bio_entities
            if not description_text and default_source_field == "description_text":
                description_text = bio_text

    out = {
        "id": str(row_id),
        "source": str(row.get("source") or dataset_name or "external"),
        "url": str(row.get("url") or ""),
        "company_name": str(row.get("company_name") or row.get("company") or ""),
        "title": title,
        "description_text": description_text,
        "location_raw": location_raw,
        "entities": entities,
        "annotation_status": status,
        "external_meta": {
            "dataset": dataset_name,
            "original_id": row.get("id") or row.get("uuid") or row.get("job_id"),
        },
    }
    return out, skipped_spans + skipped_bio


def main() -> None:
    ap = argparse.ArgumentParser(description="Import external NER annotations into project JSONL schema.")
    ap.add_argument("--input", required=True, help="External dataset path (.json or .jsonl)")
    ap.add_argument("--output", required=True, help="Output JSONL path in project schema")
    ap.add_argument("--dataset-name", required=True, help="Dataset identifier (e.g. skillspan_v1)")
    ap.add_argument(
        "--default-source-field",
        default="description_text",
        choices=sorted(ALLOWED_SOURCE_FIELDS),
        help="Fallback source_field when missing",
    )
    ap.add_argument(
        "--annotation-status",
        default="converted",
        choices=["todo", "preannotated", "converted", "openai_annotated", "openai_error"],
        help="Status set on imported rows",
    )
    ap.add_argument("--label-map", default=None, help="Optional JSON file mapping external labels -> internal labels")
    ap.add_argument("--id-prefix", default="ext", help="Generated id prefix when missing")
    ap.add_argument("--max-records", type=int, default=None, help="Import at most N rows")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    rows = read_input(in_path)
    if args.max_records is not None:
        rows = rows[: max(0, args.max_records)]

    label_map = _load_label_map(args.label_map)

    converted: list[dict[str, Any]] = []
    total_entities = 0
    rows_with_entities = 0
    skipped_entities = 0

    for i, row in enumerate(rows, start=1):
        out_row, row_skipped = convert_row(
            row=row,
            idx=i,
            dataset_name=args.dataset_name,
            default_source_field=args.default_source_field,
            status=args.annotation_status,
            extra_label_map=label_map,
            id_prefix=args.id_prefix,
        )
        converted.append(out_row)

        n = len(out_row.get("entities", []))
        total_entities += n
        if n > 0:
            rows_with_entities += 1
        skipped_entities += row_skipped

    write_jsonl(out_path, converted)

    print(f"Input rows: {len(rows)}")
    print(f"Output rows: {len(converted)}")
    print(f"Rows with entities: {rows_with_entities}")
    print(f"Total entities: {total_entities}")
    print(f"Skipped/invalid entities: {skipped_entities}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

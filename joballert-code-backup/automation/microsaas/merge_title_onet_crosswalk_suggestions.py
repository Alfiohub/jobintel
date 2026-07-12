from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


BASE_FIELDS = [
    "normalized_title",
    "onet_soc_code",
    "onet_title",
    "mapping_confidence",
    "mapping_source",
]
EXTRA_FIELDS = ["suggestion_source", "suggestion_score", "merge_decision"]


def _s(value: Any) -> str:
    return str(value or "").strip()


def _to_float(value: Any) -> float | None:
    raw = _s(value)
    if not raw:
        return None
    try:
        return float(raw)
    except Exception:
        return None


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _normalize_title_key(row: dict[str, str]) -> str:
    return _s(row.get("normalized_title")).lower()


def _base_to_out_row(row: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k in BASE_FIELDS:
        out[k] = _s(row.get(k))
    out["suggestion_source"] = ""
    out["suggestion_score"] = ""
    out["merge_decision"] = "kept_base"
    return out


def _suggestion_to_out_row(row: dict[str, str]) -> dict[str, str]:
    score_raw = _s(row.get("suggested_match_score"))
    return {
        "normalized_title": _s(row.get("normalized_title")).lower(),
        "onet_soc_code": _s(row.get("suggested_onet_soc_code")),
        "onet_title": _s(row.get("suggested_onet_title")),
        "mapping_confidence": score_raw,
        "mapping_source": "suggestion_auto",
        "suggestion_source": _s(row.get("suggested_source_table")),
        "suggestion_score": score_raw,
        "merge_decision": "added_from_suggestion",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge title_onet_crosswalk suggestions into base CSV (non-destructive)")
    ap.add_argument("--base-csv", default="docs/title_onet_crosswalk.csv", help="Base manual crosswalk CSV")
    ap.add_argument(
        "--suggestions-csv",
        default="docs/title_onet_crosswalk_suggestions.csv",
        help="Suggestions CSV produced by suggest_title_onet_crosswalk.py",
    )
    ap.add_argument("--out-csv", default="docs/title_onet_crosswalk_merged.csv", help="Output merged CSV")
    ap.add_argument("--min-score", type=float, default=0.75, help="Minimum suggestion score to be eligible")
    ap.add_argument(
        "--only-empty-base",
        action="store_true",
        help="Only add suggestions when base CSV is empty (safe mode)",
    )
    ap.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Allow replacing existing base rows with suggestions (opt-in)",
    )
    args = ap.parse_args()

    base_path = Path(args.base_csv)
    sug_path = Path(args.suggestions_csv)
    out_path = Path(args.out_csv)

    if not base_path.exists():
        raise RuntimeError(f"Base CSV not found: {base_path}")
    if not sug_path.exists():
        raise RuntimeError(f"Suggestions CSV not found: {sug_path}")

    min_score = max(0.0, min(1.0, float(args.min_score)))

    base_rows = _read_csv(base_path)
    sug_rows = _read_csv(sug_path)

    out_rows: list[dict[str, str]] = []
    index: dict[str, int] = {}

    for row in base_rows:
        key = _normalize_title_key(row)
        if not key:
            continue
        out_row = _base_to_out_row(row)
        if key in index:
            out_rows[index[key]]["merge_decision"] = "kept_base_duplicate"
            continue
        index[key] = len(out_rows)
        out_rows.append(out_row)

    base_is_empty = len(out_rows) == 0

    added = 0
    skipped_existing = 0
    skipped_low_score = 0
    skipped_invalid = 0
    overwritten = 0

    for srow in sug_rows:
        key = _normalize_title_key(srow)
        if not key:
            skipped_invalid += 1
            continue

        score = _to_float(srow.get("suggested_match_score"))
        soc = _s(srow.get("suggested_onet_soc_code"))
        title = _s(srow.get("suggested_onet_title"))

        if score is None or score < min_score:
            skipped_low_score += 1
            continue
        if not soc or not title:
            skipped_invalid += 1
            continue

        if args.only_empty_base and not base_is_empty:
            skipped_existing += 1
            continue

        if key in index and not args.overwrite_existing:
            skipped_existing += 1
            continue

        candidate = _suggestion_to_out_row(srow)

        if key in index and args.overwrite_existing:
            prev_decision = out_rows[index[key]].get("merge_decision", "kept_base")
            candidate["merge_decision"] = f"overwritten_from_suggestion(prev={prev_decision})"
            out_rows[index[key]] = candidate
            overwritten += 1
            continue

        index[key] = len(out_rows)
        out_rows.append(candidate)
        added += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = BASE_FIELDS + EXTRA_FIELDS
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Base: {base_path}")
    print(f"Suggestions: {sug_path}")
    print(f"Out: {out_path}")
    print(f"Rows out: {len(out_rows)}")
    print(f"Added from suggestions: {added}")
    print(f"Overwritten existing: {overwritten}")
    print(f"Skipped existing: {skipped_existing}")
    print(f"Skipped low score (< {min_score:.2f}): {skipped_low_score}")
    print(f"Skipped invalid suggestions: {skipped_invalid}")


if __name__ == "__main__":
    main()

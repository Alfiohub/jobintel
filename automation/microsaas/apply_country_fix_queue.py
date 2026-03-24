from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Any


def _s(v: Any) -> str:
    return str(v or "").strip()


def _norm_iso2(v: str) -> str:
    t = _s(v).upper()
    if len(t) == 2 and t.isalpha():
        return t
    return ""


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply country/location manual fixes from country_fix_queue CSV.")
    ap.add_argument("--gold-csv", default="docs/gold_eval_set_v1_en_locv5_autolabeled.csv")
    ap.add_argument("--queue-csv", default="docs/country_fix_queue_locv5.csv")
    ap.add_argument("--output", default="docs/gold_eval_set_v1_en_locv5_autolabeled.csv")
    ap.add_argument("--backup", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--report-json", default="docs/review_analysis_locv5/country_queue_apply.json")
    ap.add_argument("--report-txt", default="docs/review_analysis_locv5/country_queue_apply.txt")
    args = ap.parse_args()

    gold_path = Path(args.gold_csv)
    queue_path = Path(args.queue_csv)
    out_path = Path(args.output)
    report_json = Path(args.report_json)
    report_txt = Path(args.report_txt)

    if not gold_path.exists():
        raise RuntimeError(f"gold csv not found: {gold_path}")
    if not queue_path.exists():
        raise RuntimeError(f"queue csv not found: {queue_path}")

    gold_rows = list(csv.DictReader(gold_path.open("r", encoding="utf-8")))
    queue_rows = list(csv.DictReader(queue_path.open("r", encoding="utf-8")))
    if not gold_rows:
        raise RuntimeError("gold csv is empty")

    by_id: dict[str, dict[str, str]] = { _s(r.get("job_indexed_id")): r for r in gold_rows if _s(r.get("job_indexed_id")) }

    touched_ids: list[str] = []
    updates = 0
    skipped = 0
    invalid = 0
    missing_ids = 0
    details: list[dict[str, str]] = []

    for q in queue_rows:
        jid = _s(q.get("job_indexed_id"))
        status = _s(q.get("qa_status")).lower()
        if not jid or status != "fix":
            skipped += 1
            continue

        row = by_id.get(jid)
        if row is None:
            missing_ids += 1
            continue

        fix_country = _norm_iso2(_s(q.get("qa_fix_country")))
        fix_city = _s(q.get("qa_fix_location_city"))
        fix_lt = _s(q.get("qa_fix_location_type")).lower()
        notes = _s(q.get("qa_notes"))

        changed = False

        if fix_country:
            if row.get("gold_country", "") != fix_country:
                row["gold_country"] = fix_country
                changed = True
        elif _s(q.get("qa_fix_country")):
            # country provided but invalid
            invalid += 1
            if args.strict:
                raise RuntimeError(f"invalid qa_fix_country for job {jid}: {q.get('qa_fix_country')!r}")

        if fix_city:
            if row.get("gold_location_city", "") != fix_city:
                row["gold_location_city"] = fix_city
                changed = True

        if fix_lt and fix_lt not in {"__no_change__", "remote", "hybrid", "onsite", "unspecified"}:
            invalid += 1
            if args.strict:
                raise RuntimeError(f"invalid qa_fix_location_type for job {jid}: {fix_lt!r}")

        if fix_lt in {"remote", "hybrid", "onsite", "unspecified"} and row.get("gold_location_type", "") != fix_lt:
            row["gold_location_type"] = fix_lt
            changed = True

        if changed:
            updates += 1
            touched_ids.append(jid)
            prev = _s(row.get("notes"))
            merged = notes if not prev else (prev if not notes else f"{prev} | country_fix_applied: {notes}")
            if notes and "country_fix_applied" not in merged:
                merged = f"{merged} | country_fix_applied"
            row["notes"] = merged
            details.append(
                {
                    "job_indexed_id": jid,
                    "gold_country": _s(row.get("gold_country")),
                    "gold_location_city": _s(row.get("gold_location_city")),
                    "gold_location_type": _s(row.get("gold_location_type")),
                }
            )

    if args.backup:
        backup_path = out_path.with_suffix(out_path.suffix + ".bak")
        shutil.copy2(gold_path, backup_path)

    fieldnames = list(gold_rows[0].keys())
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(gold_rows)

    report = {
        "gold_csv": str(gold_path),
        "queue_csv": str(queue_path),
        "output_csv": str(out_path),
        "queue_rows": len(queue_rows),
        "updates": updates,
        "touched_job_ids": touched_ids,
        "skipped_non_fix": skipped,
        "invalid_fixes": invalid,
        "missing_job_ids": missing_ids,
        "details": details[:200],
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report_txt.parent.mkdir(parents=True, exist_ok=True)
    report_txt.write_text(
        "\n".join(
            [
                f"queue_rows: {len(queue_rows)}",
                f"updates: {updates}",
                f"skipped_non_fix: {skipped}",
                f"invalid_fixes: {invalid}",
                f"missing_job_ids: {missing_ids}",
                f"touched_job_ids: {len(touched_ids)}",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote: {out_path}")
    print(f"Wrote: {report_json}")
    print(f"Wrote: {report_txt}")
    print(f"Touched job ids: {len(touched_ids)}")


if __name__ == "__main__":
    main()


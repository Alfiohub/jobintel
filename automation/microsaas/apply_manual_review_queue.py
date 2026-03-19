from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def _s(value: Any) -> str:
    return str(value or "").strip()


def _merge_notes(existing: str, extra: str) -> str:
    a = _s(existing)
    b = _s(extra)
    if not a:
        return b
    if not b:
        return a
    if b in a:
        return a
    return f"{a} | {b}"


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open("r", encoding="utf-8")))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply manual review queue decisions to gold eval CSV.")
    ap.add_argument("--gold-csv", required=True, help="Target gold autolabeled CSV")
    ap.add_argument("--queue-csv", required=True, help="Filled manual queue CSV")
    ap.add_argument("--output", required=True, help="Output gold CSV path")
    ap.add_argument("--dry-run", action="store_true", help="Analyze only, do not write output CSV")
    ap.add_argument("--backup", action="store_true", help="If output exists and not dry-run, write .bak backup")
    ap.add_argument("--strict", action="store_true", help="Fail if required columns are missing")
    ap.add_argument("--report-json", default="", help="Optional report JSON path")
    ap.add_argument("--report-txt", default="", help="Optional report TXT path")
    args = ap.parse_args()

    gold_path = Path(args.gold_csv)
    queue_path = Path(args.queue_csv)
    out_path = Path(args.output)

    if not gold_path.exists():
        raise RuntimeError(f"Gold CSV not found: {gold_path}")
    if not queue_path.exists():
        raise RuntimeError(f"Queue CSV not found: {queue_path}")

    gold_rows = _read_csv(gold_path)
    queue_rows = _read_csv(queue_path)
    if not gold_rows:
        raise RuntimeError("Gold CSV has no rows")
    if not queue_rows:
        raise RuntimeError("Queue CSV has no rows")

    gold_fieldnames = list(gold_rows[0].keys())
    queue_required = {
        "job_indexed_id",
        "review_decision",
        "review_notes",
        "pred_normalized_title",
        "gold_normalized_title_after",
    }
    missing_queue = sorted(queue_required - set(queue_rows[0].keys()))
    if missing_queue and args.strict:
        raise RuntimeError(f"Queue CSV missing required columns: {missing_queue}")

    gold_idx: dict[str, dict[str, str]] = {}
    for row in gold_rows:
        job_id = _s(row.get("job_indexed_id"))
        if job_id:
            gold_idx[job_id] = row

    counters: Counter[str] = Counter()
    touched_ids: set[str] = set()

    for q in queue_rows:
        counters["queue_rows"] += 1
        job_id = _s(q.get("job_indexed_id"))
        decision = _s(q.get("review_decision")).lower()
        note = _s(q.get("review_notes"))
        pred_title = _s(q.get("pred_normalized_title"))
        after_title = _s(q.get("gold_normalized_title_after"))

        if not job_id:
            counters["skip_missing_job_id"] += 1
            continue
        row = gold_idx.get(job_id)
        if row is None:
            counters["skip_job_not_found"] += 1
            continue
        if not decision:
            counters["skip_empty_decision"] += 1
            continue

        touched_ids.add(job_id)
        counters[f"decision_{decision}"] += 1

        if decision == "accept":
            if after_title:
                if _s(row.get("gold_normalized_title")) != after_title:
                    row["gold_normalized_title"] = after_title
                    counters["changed_gold_title"] += 1
            row["notes"] = _merge_notes(row.get("notes", ""), f"manual_queue_accept: {note}")
            counters["updated_notes"] += 1
            continue

        if decision == "reject":
            if pred_title:
                if _s(row.get("gold_normalized_title")) != pred_title:
                    row["gold_normalized_title"] = pred_title
                    counters["changed_gold_title"] += 1
            row["review_status"] = "in_review"
            row["needs_review"] = "1"
            row["notes"] = _merge_notes(row.get("notes", ""), f"manual_queue_reject: {note}")
            counters["set_in_review"] += 1
            counters["updated_notes"] += 1
            continue

        if decision == "needs_manual_rule":
            row["review_status"] = "in_review"
            row["needs_review"] = "1"
            row["notes"] = _merge_notes(row.get("notes", ""), f"manual_queue_needs_manual_rule: {note}")
            counters["set_in_review"] += 1
            counters["updated_notes"] += 1
            continue

        counters["skip_unknown_decision"] += 1

    report = {
        "gold_csv_input": str(gold_path),
        "queue_csv_input": str(queue_path),
        "output_csv": str(out_path),
        "dry_run": bool(args.dry_run),
        "touched_job_ids": len(touched_ids),
        "stats": dict(counters),
    }

    if not args.dry_run:
        if args.backup and out_path.exists():
            bak = out_path.with_suffix(out_path.suffix + ".bak")
            bak.write_bytes(out_path.read_bytes())
            report["backup_csv"] = str(bak)
        _write_csv(out_path, gold_rows, gold_fieldnames)
        print(f"Wrote: {out_path}")
    else:
        print("Dry-run mode: no CSV written.")

    if args.report_json:
        rp = Path(args.report_json)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {rp}")

    if args.report_txt:
        rp = Path(args.report_txt)
        rp.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "Manual Review Queue Apply Report",
            f"Gold input: {gold_path}",
            f"Queue input: {queue_path}",
            f"Output: {out_path}",
            f"Dry-run: {int(args.dry_run)}",
            f"Touched job ids: {len(touched_ids)}",
            "",
            "Stats:",
        ]
        for k, v in counters.most_common():
            lines.append(f"- {k}: {v}")
        rp.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote: {rp}")

    print(f"Touched job ids: {len(touched_ids)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.title_normalization import normalize_title
except ModuleNotFoundError:
    from title_normalization import normalize_title


_TOKEN_RE = re.compile(r"^[a-z0-9_]+$")


def _s(value: Any) -> str:
    return str(value or "").strip()


def _is_token_like(value: str) -> bool:
    return bool(_TOKEN_RE.match(value))


def _canonicalize_gold_title(gold_raw: str, pred_norm: str) -> tuple[str, str, str]:
    gold = _s(gold_raw)
    pred = _s(pred_norm).lower()
    if not gold:
        return "", "keep_empty", "empty_gold_title"

    gold_l = gold.lower()
    if _is_token_like(gold_l):
        return gold_l, "keep_token", "already_token"

    cand, _, _ = normalize_title(gold)
    if cand and cand != "other":
        return cand, "set_from_gold_text", "normalized_from_gold_text"

    if pred and pred != "other":
        return pred, "set_from_pred_fallback", "gold_mapped_to_other_pred_used"

    return "other", "set_other", "gold_mapped_to_other_no_pred"


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _write_queue(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "job_indexed_id",
        "url",
        "title_clean",
        "pred_normalized_title",
        "gold_normalized_title_before",
        "gold_normalized_title_after",
        "pred_role_family",
        "gold_role_family",
        "queue_reason",
        "review_decision",
        "review_notes",
    ]
    _write_csv(path, rows, fieldnames)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Deterministic canonicalization of gold_normalized_title + manual review queue generation."
    )
    ap.add_argument("--input", required=True, help="Input autolabeled CSV path")
    ap.add_argument("--output", required=True, help="Output CSV path")
    ap.add_argument("--dry-run", action="store_true", help="Analyze only, do not write CSV changes")
    ap.add_argument("--backup", action="store_true", help="If output exists and not dry-run, save output.bak")
    ap.add_argument("--strict", action="store_true", help="Fail if required columns are missing")
    ap.add_argument("--queue-csv", default="", help="Optional output manual review queue CSV path")
    ap.add_argument("--report-json", default="", help="Optional output report JSON path")
    ap.add_argument("--report-txt", default="", help="Optional output report TXT path")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        raise RuntimeError(f"Input CSV not found: {in_path}")

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    fieldnames = list(rows[0].keys())
    required = {"gold_normalized_title", "pred_normalized_title", "job_indexed_id", "url", "title_clean"}
    missing = sorted(required - set(fieldnames))
    if missing and args.strict:
        raise RuntimeError(f"Missing required columns: {missing}")

    counters: Counter[str] = Counter()
    changed_rows = 0
    out_rows: list[dict[str, str]] = []
    queue_rows: list[dict[str, str]] = []

    for row in rows:
        counters["total_rows"] += 1
        out_row = dict(row)
        gold_before = _s(row.get("gold_normalized_title"))
        pred = _s(row.get("pred_normalized_title"))

        gold_after, action, reason = _canonicalize_gold_title(gold_before, pred)
        counters[action] += 1

        if gold_after != gold_before:
            changed_rows += 1
            counters["changed_rows"] += 1
            out_row["gold_normalized_title"] = gold_after

        # Manual QA queue policy:
        # - cases mapped to "other"
        # - cases where canonicalized value differs from pred non-other
        # - cases where gold_role_family is empty while title now canonical
        pred_l = pred.lower()
        gold_after_l = gold_after.lower()
        gold_role_family = _s(row.get("gold_role_family"))
        queue_reason = ""
        if gold_after_l == "other":
            queue_reason = "title_still_other_after_canonicalization"
        elif pred_l and pred_l != "other" and gold_after_l != pred_l:
            queue_reason = "gold_vs_pred_title_mismatch"
        elif gold_after_l and gold_after_l != "other" and not gold_role_family:
            queue_reason = "missing_gold_role_family_with_canonical_title"

        if queue_reason:
            queue_rows.append(
                {
                    "job_indexed_id": _s(row.get("job_indexed_id")),
                    "url": _s(row.get("url")),
                    "title_clean": _s(row.get("title_clean")),
                    "pred_normalized_title": pred,
                    "gold_normalized_title_before": gold_before,
                    "gold_normalized_title_after": gold_after,
                    "pred_role_family": _s(row.get("pred_role_family")),
                    "gold_role_family": gold_role_family,
                    "queue_reason": queue_reason,
                    "review_decision": "",
                    "review_notes": "",
                }
            )
            counters[f"queue_{queue_reason}"] += 1

        out_rows.append(out_row)

    report = {
        "input_csv": str(in_path),
        "output_csv": str(out_path),
        "dry_run": bool(args.dry_run),
        "changed_rows": changed_rows,
        "queue_rows": len(queue_rows),
        "stats": dict(counters),
    }

    if not args.dry_run:
        if args.backup and out_path.exists():
            bak = out_path.with_suffix(out_path.suffix + ".bak")
            bak.write_bytes(out_path.read_bytes())
            report["backup_csv"] = str(bak)
        _write_csv(out_path, out_rows, fieldnames)
        print(f"Wrote: {out_path}")
    else:
        print("Dry-run mode: no CSV written.")

    if args.queue_csv:
        queue_path = Path(args.queue_csv)
        _write_queue(queue_path, queue_rows)
        report["queue_csv"] = str(queue_path)
        print(f"Wrote: {queue_path}")

    if args.report_json:
        p = Path(args.report_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {p}")

    if args.report_txt:
        p = Path(args.report_txt)
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "Gold Title Canonical Backfill Report",
            f"Input: {in_path}",
            f"Output: {out_path}",
            f"Dry-run: {int(args.dry_run)}",
            f"Changed rows: {changed_rows}",
            f"Queue rows: {len(queue_rows)}",
            "",
            "Stats:",
        ]
        for k, v in counters.most_common():
            lines.append(f"- {k}: {v}")
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote: {p}")

    print(f"Changed rows: {changed_rows}")
    print(f"Queue rows: {len(queue_rows)}")


if __name__ == "__main__":
    main()


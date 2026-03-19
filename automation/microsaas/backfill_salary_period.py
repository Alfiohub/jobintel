from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_PERIODS = {"hourly", "daily", "weekly", "monthly", "yearly", "unspecified"}


def _s(value: Any) -> str:
    return str(value or "").strip()


def _to_int(value: str) -> int | None:
    try:
        return int(float(value))
    except Exception:
        return None


def _infer_period(*, salary_min: str, salary_max: str, salary_currency: str) -> tuple[str | None, str]:
    # Return: (period, reason)
    cur = _s(salary_currency).upper()
    if not cur or len(cur) != 3 or not cur.isalpha():
        return None, "skip_invalid_currency"

    smin_i = _to_int(_s(salary_min))
    smax_i = _to_int(_s(salary_max))
    anchor = smax_i if smax_i is not None else smin_i
    if anchor is None or anchor <= 0:
        return None, "skip_missing_salary_value"

    # Conservative deterministic heuristic:
    #  - ranges with max >= 1000 are annual compensation in this dataset
    #  - lower values are interpreted as hourly compensation
    if anchor >= 1000:
        return "yearly", "inferred_yearly_anchor_ge_1000"
    return "hourly", "inferred_hourly_anchor_lt_1000"


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill gold_salary_period in autolabeled eval CSV (deterministic, no LLM).")
    ap.add_argument("--input", required=True, help="Input autolabeled CSV path")
    ap.add_argument("--output", required=True, help="Output CSV path")
    ap.add_argument("--dry-run", action="store_true", help="Analyze only, do not write CSV changes")
    ap.add_argument("--backup", action="store_true", help="If output exists and not dry-run, save output.bak before overwrite")
    ap.add_argument("--strict", action="store_true", help="Fail if required columns are missing")
    ap.add_argument("--report-json", default="", help="Optional report JSON path")
    ap.add_argument("--report-txt", default="", help="Optional report TXT path")
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    if not in_path.exists():
        raise RuntimeError(f"Input CSV not found: {in_path}")

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    fieldnames = list(rows[0].keys())
    required = {"gold_salary_min", "gold_salary_max", "gold_salary_currency", "gold_salary_period"}
    missing = sorted(required - set(fieldnames))
    if missing and args.strict:
        raise RuntimeError(f"Missing required columns: {missing}")

    counters: Counter[str] = Counter()
    changed_rows = 0
    out_rows: list[dict[str, str]] = []

    for row in rows:
        out_row = dict(row)
        counters["total_rows"] += 1

        cur_period = _s(row.get("gold_salary_period"))
        if cur_period:
            if cur_period.lower() in ALLOWED_PERIODS:
                counters["already_has_period"] += 1
            else:
                counters["already_has_nonstandard_period"] += 1
            out_rows.append(out_row)
            continue

        smin = _s(row.get("gold_salary_min"))
        smax = _s(row.get("gold_salary_max"))
        scur = _s(row.get("gold_salary_currency"))
        if not (smin or smax):
            counters["skip_no_salary_values"] += 1
            out_rows.append(out_row)
            continue
        if not scur:
            counters["skip_no_currency"] += 1
            out_rows.append(out_row)
            continue

        period, reason = _infer_period(salary_min=smin, salary_max=smax, salary_currency=scur)
        if period is None:
            counters[reason] += 1
            out_rows.append(out_row)
            continue

        counters[f"set_{period}"] += 1
        counters["changed_rows"] += 1
        changed_rows += 1
        out_row["gold_salary_period"] = period
        out_rows.append(out_row)

    report = {
        "input_csv": str(in_path),
        "output_csv": str(out_path),
        "dry_run": bool(args.dry_run),
        "changed_rows": changed_rows,
        "stats": dict(counters),
    }

    if not args.dry_run:
        if args.backup and out_path.exists():
            backup_path = out_path.with_suffix(out_path.suffix + ".bak")
            backup_path.write_bytes(out_path.read_bytes())
            report["backup_csv"] = str(backup_path)
        _write_csv(out_path, out_rows, fieldnames)
        print(f"Wrote: {out_path}")
    else:
        print("Dry-run mode: no CSV written.")

    if args.report_json:
        p = Path(args.report_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {p}")

    if args.report_txt:
        p = Path(args.report_txt)
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "Salary Period Backfill Report",
            f"Input: {in_path}",
            f"Output: {out_path}",
            f"Dry-run: {int(args.dry_run)}",
            f"Changed rows: {changed_rows}",
            "",
            "Stats:",
        ]
        for k, v in counters.most_common():
            lines.append(f"- {k}: {v}")
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote: {p}")

    print(f"Changed rows: {changed_rows}")


if __name__ == "__main__":
    main()


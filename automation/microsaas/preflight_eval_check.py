from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def _pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return (float(part) / float(total)) * 100.0


def _db_stats(db_path: Path) -> dict[str, Any]:
    con = sqlite3.connect(str(db_path))
    try:
        total = int(con.execute("SELECT COUNT(*) FROM jobs_indexed").fetchone()[0])
        title_clean = int(
            con.execute("SELECT COUNT(*) FROM jobs_indexed WHERE trim(coalesce(title_clean,''))<>''").fetchone()[0]
        )
        title_raw = int(
            con.execute("SELECT COUNT(*) FROM jobs_indexed WHERE trim(coalesce(title_raw,''))<>''").fetchone()[0]
        )
        desc_clean = int(
            con.execute("SELECT COUNT(*) FROM jobs_clean WHERE trim(coalesce(description_clean,''))<>''").fetchone()[0]
        )
        country = int(con.execute("SELECT COUNT(*) FROM jobs_indexed WHERE trim(coalesce(country,''))<>''").fetchone()[0])
    finally:
        con.close()
    return {
        "total_jobs_indexed": total,
        "title_clean_non_empty": title_clean,
        "title_raw_non_empty": title_raw,
        "description_clean_non_empty": desc_clean,
        "country_non_empty": country,
        "title_clean_pct": _pct(title_clean, total),
        "title_raw_pct": _pct(title_raw, total),
        "description_clean_pct": _pct(desc_clean, total),
        "country_pct": _pct(country, total),
    }


def _csv_stats(csv_path: Path) -> dict[str, Any]:
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    total = len(rows)
    keys = rows[0].keys() if rows else []
    counts: dict[str, int] = {}
    for k in (
        "title_clean",
        "description_clean_excerpt",
        "pred_normalized_title",
        "pred_role_family",
        "pred_location_type",
        "pred_country",
        "gold_normalized_title",
        "label_confidence",
    ):
        if k in keys:
            counts[k] = sum(1 for r in rows if str(r.get(k) or "").strip())
    return {"rows": total, "counts_non_empty": counts}


def _run_checks(
    db_stats: dict[str, Any],
    *,
    min_title_coverage: float,
    min_desc_coverage: float,
    min_country_coverage: float,
    csv_stats: dict[str, Any] | None,
    min_eval_rows: int,
) -> list[CheckResult]:
    checks: list[CheckResult] = []
    total = int(db_stats["total_jobs_indexed"])
    checks.append(
        CheckResult(
            name="db_has_rows",
            passed=total > 0,
            details=f"total_jobs_indexed={total}",
        )
    )
    checks.append(
        CheckResult(
            name="title_clean_coverage",
            passed=float(db_stats["title_clean_pct"]) >= min_title_coverage,
            details=f"title_clean_pct={db_stats['title_clean_pct']:.2f}% threshold={min_title_coverage:.2f}%",
        )
    )
    checks.append(
        CheckResult(
            name="description_clean_coverage",
            passed=float(db_stats["description_clean_pct"]) >= min_desc_coverage,
            details=f"description_clean_pct={db_stats['description_clean_pct']:.2f}% threshold={min_desc_coverage:.2f}%",
        )
    )
    checks.append(
        CheckResult(
            name="country_coverage",
            passed=float(db_stats["country_pct"]) >= min_country_coverage,
            details=f"country_pct={db_stats['country_pct']:.2f}% threshold={min_country_coverage:.2f}%",
        )
    )

    if csv_stats is not None:
        rows = int(csv_stats["rows"])
        checks.append(
            CheckResult(
                name="eval_csv_rows",
                passed=rows >= min_eval_rows,
                details=f"rows={rows} threshold={min_eval_rows}",
            )
        )
        c = csv_stats["counts_non_empty"]
        title_non_empty = int(c.get("title_clean", 0))
        desc_non_empty = int(c.get("description_clean_excerpt", 0))
        checks.append(
            CheckResult(
                name="eval_csv_has_title_clean",
                passed=(rows > 0 and title_non_empty == rows),
                details=f"title_clean_non_empty={title_non_empty}/{rows}",
            )
        )
        checks.append(
            CheckResult(
                name="eval_csv_has_description_excerpt",
                passed=(rows > 0 and desc_non_empty == rows),
                details=f"description_clean_excerpt_non_empty={desc_non_empty}/{rows}",
            )
        )
    return checks


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Preflight checks before running expensive gold-eval autolabel jobs."
    )
    ap.add_argument("--db", required=True, help="SQLite DB path with jobs_indexed/jobs_clean.")
    ap.add_argument("--eval-csv", default="", help="Optional eval CSV path to validate.")
    ap.add_argument("--min-title-coverage", type=float, default=95.0, help="Minimum title_clean coverage in DB (percent).")
    ap.add_argument(
        "--min-description-coverage",
        type=float,
        default=95.0,
        help="Minimum description_clean coverage in DB (percent).",
    )
    ap.add_argument("--min-country-coverage", type=float, default=0.0, help="Minimum country coverage in DB (percent).")
    ap.add_argument("--min-eval-rows", type=int, default=100, help="Minimum rows expected in eval CSV.")
    ap.add_argument("--out-json", default="", help="Optional output JSON path for report.")
    ap.add_argument("--strict", action="store_true", help="Exit with code 1 if any check fails.")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise RuntimeError(f"DB not found: {db_path}")

    csv_stats: dict[str, Any] | None = None
    if args.eval_csv:
        csv_path = Path(args.eval_csv)
        if not csv_path.exists():
            raise RuntimeError(f"Eval CSV not found: {csv_path}")
        csv_stats = _csv_stats(csv_path)

    db_stats = _db_stats(db_path)
    checks = _run_checks(
        db_stats,
        min_title_coverage=float(args.min_title_coverage),
        min_desc_coverage=float(args.min_description_coverage),
        min_country_coverage=float(args.min_country_coverage),
        csv_stats=csv_stats,
        min_eval_rows=max(1, int(args.min_eval_rows)),
    )
    passed = all(c.passed for c in checks)

    report = {
        "db": str(db_path),
        "db_stats": db_stats,
        "eval_csv": args.eval_csv or None,
        "eval_csv_stats": csv_stats,
        "checks": [{"name": c.name, "passed": c.passed, "details": c.details} for c in checks],
        "safe_to_run": passed,
    }

    print(f"DB: {db_path}")
    print(
        "DB coverage:"
        f" title_clean={db_stats['title_clean_pct']:.2f}%"
        f" description_clean={db_stats['description_clean_pct']:.2f}%"
        f" country={db_stats['country_pct']:.2f}%"
    )
    if csv_stats is not None:
        print(f"Eval CSV rows: {csv_stats['rows']}")
    for c in checks:
        icon = "PASS" if c.passed else "FAIL"
        print(f"[{icon}] {c.name}: {c.details}")
    print("SAFE TO RUN" if passed else "NOT SAFE TO RUN")

    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote: {out}")

    if args.strict and not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()


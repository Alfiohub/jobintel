from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


def _stats(db: str) -> dict[str, float | int]:
    con = sqlite3.connect(db)
    cur = con.cursor()
    total = int(cur.execute("select count(*) from jobs_indexed").fetchone()[0])
    other = int(cur.execute("select count(*) from jobs_indexed where lower(coalesce(normalized_title,''))='other'").fetchone()[0])
    con.close()
    rate = (other / total) if total else 0.0
    return {"total_rows": total, "other_rows": other, "other_rate": rate}


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate candidate taxonomy run and decide promotion.")
    ap.add_argument("--baseline-db", required=True)
    ap.add_argument("--candidate-db", required=True)
    ap.add_argument("--min-other-abs-improvement", type=int, default=10)
    ap.add_argument("--max-other-rate-increase", type=float, default=0.0)
    ap.add_argument("--out-json", default="docs/taxonomy_promotion_decision.json")
    ap.add_argument("--out-md", default="docs/taxonomy_promotion_decision.md")
    ap.add_argument("--no-fail", action="store_true", help="Always exit 0 even if failed")
    args = ap.parse_args()

    b = _stats(args.baseline_db)
    c = _stats(args.candidate_db)

    abs_impr = int(b["other_rows"] - c["other_rows"])
    rate_delta = float(c["other_rate"] - b["other_rate"])

    checks = {
        "abs_improvement_ok": abs_impr >= args.min_other_abs_improvement,
        "rate_increase_ok": rate_delta <= args.max_other_rate_increase,
    }
    passed = all(checks.values())

    out = {
        "baseline_db": args.baseline_db,
        "candidate_db": args.candidate_db,
        "baseline": b,
        "candidate": c,
        "delta": {
            "other_abs_improvement": abs_impr,
            "other_rate_delta": rate_delta,
        },
        "thresholds": {
            "min_other_abs_improvement": args.min_other_abs_improvement,
            "max_other_rate_increase": args.max_other_rate_increase,
        },
        "checks": checks,
        "promotion_passed": passed,
    }

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Taxonomy Promotion Decision",
        "",
        f"- baseline_db: `{args.baseline_db}`",
        f"- candidate_db: `{args.candidate_db}`",
        f"- other baseline: {b['other_rows']} / {b['total_rows']} ({b['other_rate']:.4f})",
        f"- other candidate: {c['other_rows']} / {c['total_rows']} ({c['other_rate']:.4f})",
        f"- abs improvement: {abs_impr}",
        f"- rate delta: {rate_delta:.6f}",
        f"- passed: {int(passed)}",
    ]
    Path(args.out_md).write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(out, ensure_ascii=False, indent=2))

    if not passed and not args.no_fail:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

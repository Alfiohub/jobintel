from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


def _s(value: Any) -> str:
    return str(value or "").strip()


def _build_coverage_from_db(conn: sqlite3.Connection, top_n: int) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT j.normalized_title, m.onet_soc_code, m.onet_match_type
        FROM jobs_indexed j
        JOIN jobs_onet_mapping m ON m.job_indexed_id = j.id
        """
    ).fetchall()

    total = len(rows)
    by_type: Counter[str] = Counter()
    no_match_norm: Counter[str] = Counter()
    matched = 0
    no_match = 0

    for row in rows:
        norm = _s(row[0]) or "(empty)"
        soc = _s(row[1])
        mtype = _s(row[2]) or "(empty)"
        by_type[mtype] += 1

        if soc:
            matched += 1
        else:
            no_match += 1
            no_match_norm[norm] += 1

    coverage_pct = (matched / total * 100.0) if total > 0 else 0.0

    return {
        "total_jobs_considered": total,
        "matched_count": matched,
        "no_match_count": no_match,
        "coverage_percent": round(coverage_pct, 2),
        "counts_by_onet_match_type": dict(by_type.most_common()),
        "top_normalized_title_without_match": [
            {"normalized_title": k, "count": v} for k, v in no_match_norm.most_common(max(1, top_n))
        ],
    }


def _write_txt(path: Path, report: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("O*NET Mapping Coverage Report")
    lines.append(f"Total jobs considered: {report['total_jobs_considered']}")
    lines.append(f"Matched count: {report['matched_count']}")
    lines.append(f"No match count: {report['no_match_count']}")
    lines.append(f"Coverage percent: {report['coverage_percent']:.2f}%")
    lines.append("")

    lines.append("Counts by onet_match_type:")
    by_type = report.get("counts_by_onet_match_type") or {}
    if by_type:
        for k, v in by_type.items():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("Top normalized_title without match:")
    top_no = report.get("top_normalized_title_without_match") or []
    if top_no:
        for item in top_no:
            lines.append(f"- {item['normalized_title']}: {item['count']}")
    else:
        lines.append("- (none)")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _num_delta(after: float | int, before: float | int) -> float:
    return float(after) - float(before)


def _compare_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_total = int(before.get("total_jobs_considered", 0) or 0)
    after_total = int(after.get("total_jobs_considered", 0) or 0)

    before_matched = int(before.get("matched_count", 0) or 0)
    after_matched = int(after.get("matched_count", 0) or 0)

    before_no_match = int(before.get("no_match_count", 0) or 0)
    after_no_match = int(after.get("no_match_count", 0) or 0)

    before_cov = float(before.get("coverage_percent", 0.0) or 0.0)
    after_cov = float(after.get("coverage_percent", 0.0) or 0.0)

    before_by_type = before.get("counts_by_onet_match_type") or {}
    after_by_type = after.get("counts_by_onet_match_type") or {}
    all_types = sorted(set(before_by_type) | set(after_by_type))

    by_type_delta = {}
    for t in all_types:
        b = int(before_by_type.get(t, 0) or 0)
        a = int(after_by_type.get(t, 0) or 0)
        by_type_delta[t] = {"before": b, "after": a, "delta": a - b}

    return {
        "summary": {
            "before_total_jobs_considered": before_total,
            "after_total_jobs_considered": after_total,
            "delta_total_jobs_considered": int(_num_delta(after_total, before_total)),
            "before_matched_count": before_matched,
            "after_matched_count": after_matched,
            "delta_matched_count": int(_num_delta(after_matched, before_matched)),
            "before_no_match_count": before_no_match,
            "after_no_match_count": after_no_match,
            "delta_no_match_count": int(_num_delta(after_no_match, before_no_match)),
            "before_coverage_percent": round(before_cov, 2),
            "after_coverage_percent": round(after_cov, 2),
            "delta_coverage_percent": round(_num_delta(after_cov, before_cov), 2),
        },
        "counts_by_onet_match_type_delta": by_type_delta,
    }


def _write_compare_txt(path: Path, compare: dict[str, Any]) -> None:
    s = compare["summary"]
    lines = [
        "O*NET Mapping Coverage Comparison",
        f"Total jobs: {s['before_total_jobs_considered']} -> {s['after_total_jobs_considered']} (delta {s['delta_total_jobs_considered']:+d})",
        f"Matched: {s['before_matched_count']} -> {s['after_matched_count']} (delta {s['delta_matched_count']:+d})",
        f"No match: {s['before_no_match_count']} -> {s['after_no_match_count']} (delta {s['delta_no_match_count']:+d})",
        f"Coverage: {s['before_coverage_percent']:.2f}% -> {s['after_coverage_percent']:.2f}% (delta {s['delta_coverage_percent']:+.2f} pp)",
        "",
        "Counts by onet_match_type (delta):",
    ]

    for t, vals in compare.get("counts_by_onet_match_type_delta", {}).items():
        lines.append(f"- {t}: {vals['before']} -> {vals['after']} (delta {vals['delta']:+d})")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Report O*NET mapping coverage from DB or compare two snapshots")
    sub = ap.add_subparsers(dest="cmd", required=False)

    dbp = sub.add_parser("from-db", help="Generate coverage report from SQLite DB")
    dbp.add_argument("--db", default="data/jobintel_microsaas.sqlite", help="Path to SQLite DB")
    dbp.add_argument("--out-json", default="docs/onet_mapping_coverage.json", help="Output JSON path")
    dbp.add_argument("--out-txt", default="docs/onet_mapping_coverage.txt", help="Output TXT path")
    dbp.add_argument("--top-n", type=int, default=20, help="Top N normalized_title without match")

    cp = sub.add_parser("compare", help="Compare two coverage snapshot JSON files")
    cp.add_argument("--before-json", required=True, help="Before snapshot JSON")
    cp.add_argument("--after-json", required=True, help="After snapshot JSON")
    cp.add_argument("--out-json", default="docs/onet_mapping_coverage_compare.json", help="Output compare JSON")
    cp.add_argument("--out-txt", default="docs/onet_mapping_coverage_compare.txt", help="Output compare TXT")

    args = ap.parse_args()

    cmd = args.cmd or "from-db"

    if cmd == "from-db":
        db_path = Path(args.db)
        if not db_path.exists():
            raise RuntimeError(f"DB not found: {db_path}")

        conn = sqlite3.connect(db_path)
        try:
            report = _build_coverage_from_db(conn, top_n=max(1, args.top_n))
        finally:
            conn.close()

        out_json = Path(args.out_json)
        out_txt = Path(args.out_txt)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_txt.parent.mkdir(parents=True, exist_ok=True)

        out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        _write_txt(out_txt, report)

        print(f"Wrote: {out_json}")
        print(f"Wrote: {out_txt}")
        print(f"Coverage: {report['coverage_percent']:.2f}%")
        return

    before_path = Path(args.before_json)
    after_path = Path(args.after_json)
    if not before_path.exists():
        raise RuntimeError(f"Before JSON not found: {before_path}")
    if not after_path.exists():
        raise RuntimeError(f"After JSON not found: {after_path}")

    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    compare = _compare_reports(before, after)

    out_json = Path(args.out_json)
    out_txt = Path(args.out_txt)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_txt.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps(compare, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_compare_txt(out_txt, compare)

    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_txt}")
    print(f"Coverage delta: {compare['summary']['delta_coverage_percent']:+.2f} pp")


if __name__ == "__main__":
    main()

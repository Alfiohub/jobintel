from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def _s(value: Any) -> str:
    return str(value or "").strip()


def _query_nomatch_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    sql = (
        "SELECT j.id, j.normalized_title, j.title_clean, j.role_family, "
        "m.onet_match_type, m.onet_match_score, m.onet_soc_code "
        "FROM jobs_onet_mapping m "
        "JOIN jobs_indexed j ON j.id = m.job_indexed_id "
        "WHERE m.onet_soc_code IS NULL OR m.onet_match_type IN ('no_match', 'no_match_low_score')"
    )
    return conn.execute(sql).fetchall()


def _build_analysis(rows: list[sqlite3.Row], top_n: int) -> dict[str, Any]:
    by_normalized_title: Counter[str] = Counter()
    by_role_family: Counter[str] = Counter()
    titles_per_normalized: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        nt = _s(row["normalized_title"]) or "(empty)"
        title = _s(row["title_clean"]) or "(empty)"
        rf = _s(row["role_family"]) or "(empty)"

        by_normalized_title[nt] += 1
        by_role_family[rf] += 1
        titles_per_normalized[nt][title] += 1

    top_norm = by_normalized_title.most_common(top_n)

    top_title_clean_by_norm: dict[str, list[dict[str, Any]]] = {}
    for norm, _ in top_norm:
        top_title_clean_by_norm[norm] = [
            {"title_clean": t, "count": c}
            for t, c in titles_per_normalized[norm].most_common(top_n)
        ]

    return {
        "total_no_match_rows": len(rows),
        "counts_per_normalized_title_without_match": [
            {"normalized_title": k, "count": v} for k, v in by_normalized_title.most_common()
        ],
        "top_title_clean_per_normalized_title_without_match": top_title_clean_by_norm,
        "counts_per_role_family_without_match": [
            {"role_family": k, "count": v} for k, v in by_role_family.most_common()
        ],
    }


def _write_txt(path: Path, analysis: dict[str, Any], top_n: int) -> None:
    lines: list[str] = []
    lines.append("O*NET No-Match Analysis")
    lines.append(f"Total no-match rows: {analysis['total_no_match_rows']}")
    lines.append("")

    lines.append("Counts per normalized_title without match:")
    for item in analysis["counts_per_normalized_title_without_match"][:top_n]:
        lines.append(f"- {item['normalized_title']}: {item['count']}")

    lines.append("")
    lines.append("Top title_clean per problematic normalized_title:")
    for normalized_title, top_titles in analysis["top_title_clean_per_normalized_title_without_match"].items():
        lines.append(f"- {normalized_title}")
        for item in top_titles[:top_n]:
            lines.append(f"  - {item['title_clean']}: {item['count']}")

    lines.append("")
    lines.append("Counts per role_family without match:")
    for item in analysis["counts_per_role_family_without_match"][:top_n]:
        lines.append(f"- {item['role_family']}: {item['count']}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze O*NET no-match patterns from jobs_onet_mapping + jobs_indexed")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite", help="Path to SQLite DB")
    ap.add_argument("--outdir", default="docs", help="Output directory")
    ap.add_argument("--top-n", type=int, default=20, help="Top N items for report sections")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise RuntimeError(f"DB not found: {db_path}")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = _query_nomatch_rows(conn)
    finally:
        conn.close()

    analysis = _build_analysis(rows, top_n=max(1, args.top_n))

    json_path = outdir / "onet_nomatch_analysis.json"
    txt_path = outdir / "onet_nomatch_analysis.txt"

    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_txt(txt_path, analysis, top_n=max(1, args.top_n))

    print(f"Wrote: {json_path}")
    print(f"Wrote: {txt_path}")
    print(f"No-match rows analyzed: {analysis['total_no_match_rows']}")


if __name__ == "__main__":
    main()

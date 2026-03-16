from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.onet_mapping import map_onet_title
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from automation.microsaas.onet_mapping import map_onet_title


def _s(value: Any) -> str:
    return str(value or "").strip()


def _fetch_no_match_rows(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    sql = (
        "SELECT j.normalized_title, j.title_clean "
        "FROM jobs_onet_mapping m "
        "JOIN jobs_indexed j ON j.id = m.job_indexed_id "
        "WHERE m.onet_soc_code IS NULL OR m.onet_match_type IN ('no_match', 'no_match_low_score')"
    )
    return conn.execute(sql).fetchall()


def _build_no_match_buckets(rows: list[sqlite3.Row]) -> tuple[Counter[str], dict[str, Counter[str]]]:
    by_norm: Counter[str] = Counter()
    titles_by_norm: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        norm = _s(row["normalized_title"]) or "(empty)"
        title = _s(row["title_clean"]) or "(empty)"
        by_norm[norm] += 1
        titles_by_norm[norm][title] += 1

    return by_norm, titles_by_norm


def _pick_best_suggestion(
    conn: sqlite3.Connection,
    normalized_title: str,
    title_counter: Counter[str],
    max_titles: int,
) -> dict[str, Any]:
    candidates_to_try: list[tuple[str, str]] = []

    if normalized_title and normalized_title != "(empty)":
        candidates_to_try.append((normalized_title, "normalized_title_query"))

    for title_clean, _ in title_counter.most_common(max_titles):
        if title_clean and title_clean != "(empty)":
            candidates_to_try.append((title_clean, "title_clean_sample"))

    best: dict[str, Any] | None = None

    for query, reason in candidates_to_try:
        mapped = map_onet_title(conn, title_clean=query, normalized_title=normalized_title)
        score = float(mapped.get("onet_match_score") or 0.0)
        soc = _s(mapped.get("onet_soc_code"))
        if not soc:
            continue

        row = {
            "normalized_title": normalized_title,
            "suggested_onet_soc_code": soc,
            "suggested_onet_title": _s(mapped.get("onet_title")),
            "suggested_match_score": round(score, 4),
            "suggested_source_table": _s(mapped.get("onet_source_table")),
            "suggestion_reason": f"{reason}:{_s(mapped.get('onet_match_type'))}",
        }

        if best is None or row["suggested_match_score"] > best["suggested_match_score"]:
            best = row

    if best is not None:
        return best

    return {
        "normalized_title": normalized_title,
        "suggested_onet_soc_code": "",
        "suggested_onet_title": "",
        "suggested_match_score": 0.0,
        "suggested_source_table": "",
        "suggestion_reason": "no_candidate_found",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Suggest manual normalized_title -> O*NET crosswalk candidates")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite", help="Path to SQLite DB")
    ap.add_argument("--out", default="docs/title_onet_crosswalk_suggestions.csv", help="Output CSV path")
    ap.add_argument(
        "--top-normalized",
        type=int,
        default=50,
        help="How many top normalized_title no-match buckets to analyze",
    )
    ap.add_argument(
        "--titles-per-normalized",
        type=int,
        default=8,
        help="How many frequent title_clean samples to try per normalized_title",
    )
    args = ap.parse_args()

    db_path = Path(args.db)
    out_path = Path(args.out)

    if not db_path.exists():
        raise RuntimeError(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = _fetch_no_match_rows(conn)
        by_norm, titles_by_norm = _build_no_match_buckets(rows)

        top_norms = [k for k, _ in by_norm.most_common(max(1, args.top_normalized))]
        suggestions: list[dict[str, Any]] = []

        for norm in top_norms:
            suggestion = _pick_best_suggestion(
                conn,
                normalized_title=norm,
                title_counter=titles_by_norm.get(norm, Counter()),
                max_titles=max(1, args.titles_per_normalized),
            )
            suggestions.append(suggestion)

    finally:
        conn.close()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "normalized_title",
        "suggested_onet_soc_code",
        "suggested_onet_title",
        "suggested_match_score",
        "suggested_source_table",
        "suggestion_reason",
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(suggestions)

    print(f"DB: {db_path}")
    print(f"No-match rows scanned: {len(rows)}")
    print(f"Normalized_title analyzed: {len(suggestions)}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.onet_mapping import map_onet_title
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from automation.microsaas.onet_mapping import map_onet_title


def _s(value: Any) -> str:
    return str(value or "").strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs_onet_mapping (
          job_indexed_id INTEGER PRIMARY KEY,
          onet_soc_code TEXT,
          onet_title TEXT,
          onet_match_type TEXT,
          onet_match_score REAL,
          onet_source_table TEXT,
          onet_matched_candidate TEXT,
          mapped_at TEXT NOT NULL,
          FOREIGN KEY (job_indexed_id) REFERENCES jobs_indexed(id) ON DELETE CASCADE
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_onet_mapping_match_type ON jobs_onet_mapping(onet_match_type)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_jobs_onet_mapping_soc_code ON jobs_onet_mapping(onet_soc_code)"
    )


def _iter_jobs(
    conn: sqlite3.Connection,
    *,
    start_id: int,
    limit: int,
    overwrite: bool,
) -> list[sqlite3.Row]:
    where = ["j.id >= ?"]
    params: list[Any] = [max(0, start_id)]

    if not overwrite:
        where.append("m.job_indexed_id IS NULL")

    sql = (
        "SELECT j.id, j.title_clean, j.normalized_title "
        "FROM jobs_indexed j "
        "LEFT JOIN jobs_onet_mapping m ON m.job_indexed_id = j.id "
        f"WHERE {' AND '.join(where)} "
        "ORDER BY j.id ASC"
    )
    if limit > 0:
        sql += " LIMIT ?"
        params.append(limit)

    return conn.execute(sql, tuple(params)).fetchall()


def _apply_min_score_policy(mapped: dict[str, Any], min_score: float) -> dict[str, Any]:
    out = dict(mapped)
    score = float(out.get("onet_match_score") or 0.0)
    if score >= min_score:
        return out

    out["onet_match_type"] = "no_match_low_score"
    out["onet_soc_code"] = None
    out["onet_title"] = None
    out["onet_source_table"] = None
    out["onet_matched_candidate"] = None
    out["onet_match_score"] = score
    return out


def _upsert_mapping(conn: sqlite3.Connection, job_id: int, mapped: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO jobs_onet_mapping(
          job_indexed_id,
          onet_soc_code,
          onet_title,
          onet_match_type,
          onet_match_score,
          onet_source_table,
          onet_matched_candidate,
          mapped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_indexed_id) DO UPDATE SET
          onet_soc_code=excluded.onet_soc_code,
          onet_title=excluded.onet_title,
          onet_match_type=excluded.onet_match_type,
          onet_match_score=excluded.onet_match_score,
          onet_source_table=excluded.onet_source_table,
          onet_matched_candidate=excluded.onet_matched_candidate,
          mapped_at=excluded.mapped_at
        """,
        (
            job_id,
            mapped.get("onet_soc_code"),
            mapped.get("onet_title"),
            mapped.get("onet_match_type"),
            float(mapped.get("onet_match_score") or 0.0),
            mapped.get("onet_source_table"),
            mapped.get("onet_matched_candidate"),
            _utc_now_iso(),
        ),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch map jobs_indexed titles to O*NET and store in jobs_onet_mapping.")
    ap.add_argument("--db", default="data/jobintel_microsaas.sqlite", help="SQLite DB path")
    ap.add_argument("--limit", type=int, default=0, help="Max jobs to process (0 = all from start-id)")
    ap.add_argument("--start-id", type=int, default=0, help="Process jobs_indexed.id >= start-id")
    ap.add_argument("--min-score", type=float, default=0.75, help="Minimum score to keep O*NET code")
    ap.add_argument("--overwrite", action="store_true", help="Recompute rows already present in jobs_onet_mapping")
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        raise RuntimeError(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        _ensure_schema(conn)
        rows = _iter_jobs(
            conn,
            start_id=max(0, args.start_id),
            limit=max(0, args.limit),
            overwrite=bool(args.overwrite),
        )

        jobs_read = len(rows)
        matched = 0
        no_match = 0
        by_type: Counter[str] = Counter()
        no_match_norm_titles: Counter[str] = Counter()

        for row in rows:
            job_id = int(row["id"])
            title_clean = _s(row["title_clean"])
            normalized_title = _s(row["normalized_title"]) or None

            mapped = map_onet_title(conn, title_clean=title_clean, normalized_title=normalized_title)
            mapped = _apply_min_score_policy(mapped, min_score=max(0.0, min(1.0, args.min_score)))

            match_type = _s(mapped.get("onet_match_type")) or "no_match"
            by_type[match_type] += 1

            if mapped.get("onet_soc_code"):
                matched += 1
            else:
                no_match += 1
                no_match_norm_titles[_s(normalized_title) or "(empty)"] += 1

            _upsert_mapping(conn, job_id, mapped)

        conn.commit()

    finally:
        conn.close()

    print(f"DB: {db_path}")
    print(f"Jobs read: {jobs_read}")
    print(f"Matched: {matched}")
    print(f"No match: {no_match}")
    print("Counts by onet_match_type:")
    if by_type:
        for k, v in by_type.most_common():
            print(f"- {k}: {v}")
    else:
        print("- (none)")

    print("Top 20 normalized_title without match:")
    if no_match_norm_titles:
        for k, v in no_match_norm_titles.most_common(20):
            print(f"- {k}: {v}")
    else:
        print("- (none)")


if __name__ == "__main__":
    main()

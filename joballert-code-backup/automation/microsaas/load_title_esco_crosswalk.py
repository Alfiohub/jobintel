from __future__ import annotations

import argparse
import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "normalized_title",
    "esco_id",
    "esco_label",
    "mapping_confidence",
    "mapping_source",
]


def _s(value: Any) -> str:
    return str(value or "").strip()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _to_float(value: Any) -> float | None:
    raw = _s(value)
    if not raw:
        return None
    try:
        return float(raw)
    except Exception:
        return None


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS title_esco_crosswalk (
          normalized_title TEXT PRIMARY KEY,
          esco_id TEXT,
          esco_label TEXT,
          mapping_confidence REAL,
          mapping_source TEXT,
          created_at TEXT,
          updated_at TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_title_esco_crosswalk_esco_id ON title_esco_crosswalk(esco_id)"
    )


def validate_columns(fieldnames: list[str] | None) -> None:
    cols = set(fieldnames or [])
    missing = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing:
        raise RuntimeError(f"CSV missing required columns: {', '.join(missing)}")


def upsert_row(conn: sqlite3.Connection, row: dict[str, str]) -> bool:
    normalized_title = _s(row.get("normalized_title")).lower()
    if not normalized_title:
        return False

    esco_id = _s(row.get("esco_id")) or None
    esco_label = _s(row.get("esco_label")) or None
    mapping_source = _s(row.get("mapping_source")) or None
    mapping_confidence = _to_float(row.get("mapping_confidence"))

    now = _now_iso()

    conn.execute(
        """
        INSERT INTO title_esco_crosswalk(
          normalized_title,
          esco_id,
          esco_label,
          mapping_confidence,
          mapping_source,
          created_at,
          updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(normalized_title) DO UPDATE SET
          esco_id=excluded.esco_id,
          esco_label=excluded.esco_label,
          mapping_confidence=excluded.mapping_confidence,
          mapping_source=excluded.mapping_source,
          updated_at=excluded.updated_at
        """,
        (
            normalized_title,
            esco_id,
            esco_label,
            mapping_confidence,
            mapping_source,
            now,
            now,
        ),
    )
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Load normalized_title -> ESCO crosswalk CSV into SQLite")
    ap.add_argument("--db", default="data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite", help="Path to SQLite DB")
    ap.add_argument("--csv", required=True, help="Path to input CSV")
    args = ap.parse_args()

    db_path = Path(args.db)
    csv_path = Path(args.csv)

    if not csv_path.exists():
        raise RuntimeError(f"CSV not found: {csv_path}")

    conn = sqlite3.connect(db_path)
    try:
        ensure_table(conn)

        inserted_or_updated = 0
        skipped = 0

        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            validate_columns(reader.fieldnames)
            for row in reader:
                ok = upsert_row(conn, row)
                if ok:
                    inserted_or_updated += 1
                else:
                    skipped += 1

        conn.commit()

    finally:
        conn.close()

    print(f"DB: {db_path}")
    print(f"CSV: {csv_path}")
    print(f"Inserted/Updated: {inserted_or_updated}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()

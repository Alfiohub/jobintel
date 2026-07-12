from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def _read_csv(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open("r", encoding="utf-8")))


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


def _upsert(
    conn: sqlite3.Connection,
    *,
    normalized_title: str,
    esco_id: str,
    esco_label: str,
    mapping_confidence: float | None,
    mapping_source: str,
) -> None:
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
            esco_id or None,
            esco_label or None,
            mapping_confidence,
            mapping_source or None,
            now,
            now,
        ),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Apply reviewed ESCO crosswalk decisions into SQLite.")
    ap.add_argument("--db", default="data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite")
    ap.add_argument("--queue-csv", default="docs/esco_crosswalk_review_queue.csv")
    ap.add_argument("--dry-run", action="store_true", help="Analyze only, do not write DB")
    ap.add_argument("--strict", action="store_true", help="Fail on invalid rows")
    ap.add_argument("--default-confidence", type=float, default=0.95)
    ap.add_argument("--mapping-source", default="manual_review")
    ap.add_argument("--report-json", default="docs/review_analysis_locv6r/esco_review_apply.json")
    ap.add_argument("--report-txt", default="docs/review_analysis_locv6r/esco_review_apply.txt")
    args = ap.parse_args()

    queue_path = Path(args.queue_csv)
    if not queue_path.exists():
        raise RuntimeError(f"Queue CSV not found: {queue_path}")

    rows = _read_csv(queue_path)
    if not rows:
        raise RuntimeError("Queue CSV has no rows")

    required = {
        "normalized_title",
        "review_action",
        "review_esco_id",
        "review_esco_label",
        "mapping_confidence",
    }
    missing = sorted(required - set(rows[0].keys()))
    if missing and args.strict:
        raise RuntimeError(f"Queue CSV missing required columns: {missing}")

    counters: Counter[str] = Counter()
    touched: list[str] = []
    details: list[dict[str, str]] = []

    conn = sqlite3.connect(args.db)
    try:
        ensure_table(conn)

        for row in rows:
            counters["queue_rows"] += 1
            nt = _s(row.get("normalized_title")).lower()
            action = _s(row.get("review_action")).lower()

            if not nt:
                counters["skip_missing_normalized_title"] += 1
                continue

            if not action:
                counters["skip_empty_action"] += 1
                continue

            if action in {"skip", "keep", "no_change"}:
                counters["skip_no_change"] += 1
                continue

            if action not in {"approve", "replace", "fix"}:
                counters["skip_unknown_action"] += 1
                if args.strict:
                    raise RuntimeError(f"Unknown review_action for {nt}: {action!r}")
                continue

            esco_id = _s(row.get("review_esco_id"))
            esco_label = _s(row.get("review_esco_label"))

            if not esco_id or not esco_label:
                counters["skip_missing_review_target"] += 1
                if args.strict:
                    raise RuntimeError(f"Missing review_esco_id/review_esco_label for {nt}")
                continue

            conf = _to_float(row.get("mapping_confidence"))
            if conf is None:
                conf = float(args.default_confidence)

            touched.append(nt)
            counters["updates"] += 1
            details.append(
                {
                    "normalized_title": nt,
                    "action": action,
                    "esco_id": esco_id,
                    "esco_label": esco_label,
                    "mapping_confidence": f"{conf:.3f}",
                }
            )

            if not args.dry_run:
                _upsert(
                    conn,
                    normalized_title=nt,
                    esco_id=esco_id,
                    esco_label=esco_label,
                    mapping_confidence=conf,
                    mapping_source=args.mapping_source,
                )

        if not args.dry_run:
            conn.commit()
    finally:
        conn.close()

    report = {
        "db": args.db,
        "queue_csv": str(queue_path),
        "dry_run": bool(args.dry_run),
        "touched_normalized_titles": len(touched),
        "stats": dict(counters),
        "details": details[:300],
    }

    report_json = Path(args.report_json)
    report_txt = Path(args.report_txt)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_txt.parent.mkdir(parents=True, exist_ok=True)

    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "ESCO Crosswalk Review Apply Report",
        f"DB: {args.db}",
        f"Queue: {queue_path}",
        f"Dry-run: {int(args.dry_run)}",
        f"Touched normalized titles: {len(touched)}",
        "",
        "Stats:",
    ]
    for k, v in counters.most_common():
        lines.append(f"- {k}: {v}")
    report_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote: {report_json}")
    print(f"Wrote: {report_txt}")
    print(f"Touched normalized titles: {len(touched)}")


if __name__ == "__main__":
    main()

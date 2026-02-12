from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ..interfaces import Store
from ..model import ScoredJob


SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_jobs (
  fingerprint TEXT PRIMARY KEY,
  first_seen  TEXT NOT NULL,
  last_seen   TEXT NOT NULL,
  score       INTEGER NOT NULL,
  source      TEXT NOT NULL,
  company     TEXT NOT NULL,
  title       TEXT NOT NULL,
  url         TEXT NOT NULL,
  location    TEXT,
  remote      INTEGER,
  published_at TEXT,
  notified    INTEGER NOT NULL DEFAULT 0
);
"""


class SQLiteStore(Store):
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute(SCHEMA)
            self._ensure_columns(con)

    def _ensure_columns(self, con: sqlite3.Connection) -> None:
        existing = {row[1] for row in con.execute("PRAGMA table_info(seen_jobs)")}
        cols = {
            "location": "TEXT",
            "remote": "INTEGER",
            "published_at": "TEXT",
        }
        for name, typ in cols.items():
            if name not in existing:
                con.execute(f"ALTER TABLE seen_jobs ADD COLUMN {name} {typ}")

    def filter_new(self, jobs: Sequence[ScoredJob]) -> list[ScoredJob]:
        out: list[ScoredJob] = []
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as con:
            for j in jobs:
                fp = j.fingerprint
                row = con.execute(
                    "SELECT fingerprint FROM seen_jobs WHERE fingerprint=?",
                    (fp,),
                ).fetchone()

                if row:
                    con.execute(
                        "UPDATE seen_jobs SET last_seen=?, score=? WHERE fingerprint=?",
                        (now, j.score, fp),
                    )
                    continue

                con.execute(
                    "INSERT INTO seen_jobs(fingerprint, first_seen, last_seen, score, source, company, title, url, location, remote, published_at, notified) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,0)",
                    (
                        fp,
                        now,
                        now,
                        int(j.score),
                        j.post.source,
                        j.post.company,
                        j.post.title,
                        j.post.url,
                        j.post.location,
                        1 if j.post.remote else 0 if j.post.remote is False else None,
                        j.post.published_at.isoformat() if j.post.published_at else None,
                    ),
                )
                out.append(j)

        return out

    def mark_notified(self, fingerprints: Sequence[str]) -> None:
        if not fingerprints:
            return
        with sqlite3.connect(self.db_path) as con:
            con.executemany(
                "UPDATE seen_jobs SET notified=1 WHERE fingerprint=?",
                [(fp,) for fp in fingerprints],
            )

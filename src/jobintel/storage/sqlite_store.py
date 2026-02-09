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
  notified    INTEGER NOT NULL DEFAULT 0
);
"""


class SQLiteStore(Store):
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute(SCHEMA)

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
                    "INSERT INTO seen_jobs(fingerprint, first_seen, last_seen, score, source, company, title, url, notified) "
                    "VALUES(?,?,?,?,?,?,?,?,0)",
                    (
                        fp,
                        now,
                        now,
                        int(j.score),
                        j.post.source,
                        j.post.company,
                        j.post.title,
                        j.post.url,
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

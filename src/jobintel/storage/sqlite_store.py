from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from ..interfaces import Store
from ..model import ScoredJob


SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_jobs (
  fingerprint TEXT PRIMARY KEY,
  dedup_key   TEXT,
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
            "dedup_key": "TEXT",
            "location": "TEXT",
            "remote": "INTEGER",
            "published_at": "TEXT",
        }
        for name, typ in cols.items():
            if name not in existing:
                con.execute(f"ALTER TABLE seen_jobs ADD COLUMN {name} {typ}")
        con.execute("CREATE INDEX IF NOT EXISTS idx_seen_jobs_dedup_key ON seen_jobs(dedup_key)")

    @staticmethod
    def _norm_for_dedup(value: str) -> str:
        txt = (value or "").strip().lower()
        txt = re.sub(r"[^a-z0-9]+", " ", txt)
        return re.sub(r"\s+", " ", txt).strip()

    def _dedup_key(self, j: ScoredJob) -> str:
        post = j.post
        raw = "|".join(
            [
                self._norm_for_dedup(post.company_name),
                self._norm_for_dedup(post.title),
                self._norm_for_dedup(post.location_raw or ""),
            ]
        )
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:20]

    def filter_new(self, jobs: Sequence[ScoredJob]) -> list[ScoredJob]:
        out: list[ScoredJob] = []
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as con:
            for j in jobs:
                fp = j.fingerprint
                dedup_key = self._dedup_key(j)
                row = con.execute(
                    "SELECT fingerprint FROM seen_jobs WHERE fingerprint=?",
                    (fp,),
                ).fetchone()
                row_dedup = con.execute(
                    "SELECT fingerprint FROM seen_jobs WHERE dedup_key=?",
                    (dedup_key,),
                ).fetchone()

                if row or row_dedup:
                    existing_fp = fp if row else row_dedup[0]
                    con.execute(
                        "UPDATE seen_jobs SET last_seen=?, score=? WHERE fingerprint=?",
                        (now, j.score, existing_fp),
                    )
                    continue

                con.execute(
                    "INSERT INTO seen_jobs(fingerprint, dedup_key, first_seen, last_seen, score, source, company, title, url, location, remote, published_at, notified) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0)",
                    (
                        fp,
                        dedup_key,
                        now,
                        now,
                        int(j.score),
                        j.post.source,
                        j.post.company_name,
                        j.post.title,
                        j.post.url,
                        j.post.location_raw or "",
                        1 if j.post.remote else 0 if j.post.remote is False else None,
                        j.post.posted_at.isoformat() if j.post.posted_at else None,
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

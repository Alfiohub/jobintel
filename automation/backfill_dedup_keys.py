from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

DB = Path('data/jobintel.sqlite')


def norm(v: str) -> str:
    txt = (v or '').strip().lower()
    txt = re.sub(r'[^a-z0-9]+', ' ', txt)
    return re.sub(r'\s+', ' ', txt).strip()


def dedup_key(company: str, title: str, location: str) -> str:
    raw = '|'.join([norm(company), norm(title), norm(location)])
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()[:20]


def main() -> None:
    con = sqlite3.connect(str(DB))
    con.execute('CREATE INDEX IF NOT EXISTS idx_seen_jobs_dedup_key ON seen_jobs(dedup_key)')
    rows = con.execute(
        "SELECT fingerprint, company, title, COALESCE(location,'') FROM seen_jobs WHERE dedup_key IS NULL OR dedup_key = ''"
    ).fetchall()
    updates = [(dedup_key(c, t, l), fp) for fp, c, t, l in rows]
    if updates:
        con.executemany('UPDATE seen_jobs SET dedup_key=? WHERE fingerprint=?', updates)
        con.commit()
    print(f'backfilled={len(updates)}')


if __name__ == '__main__':
    main()

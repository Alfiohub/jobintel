from __future__ import annotations

from datetime import datetime
from typing import Any
import sqlite3

from fastapi import FastAPI, Query


app = FastAPI(title="jobintel")


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def _ensure_columns(con: sqlite3.Connection) -> None:
    existing = {row[1] for row in con.execute("PRAGMA table_info(seen_jobs)")}
    cols = {
        "location": "TEXT",
        "remote": "INTEGER",
        "published_at": "TEXT",
    }
    for name, typ in cols.items():
        if name not in existing:
            con.execute(f"ALTER TABLE seen_jobs ADD COLUMN {name} {typ}")


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return dt.isoformat()
    except Exception:
        return None


@app.get("/jobs")
def list_jobs(
    db_path: str = Query("data/jobintel.sqlite"),
    min_score: int | None = Query(None, ge=0, le=100),
    company: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if min_score is not None:
        where.append("score >= ?")
        params.append(min_score)
    if company:
        where.append("company = ?")
        params.append(company)
    if source:
        where.append("source = ?")
        params.append(source)
    if remote is not None:
        where.append("remote = ?")
        params.append(1 if remote else 0)
    if location:
        where.append("location LIKE ?")
        params.append(f"%{location}%")

    df = _parse_date(date_from)
    if df:
        where.append("published_at >= ?")
        params.append(df)
    dt = _parse_date(date_to)
    if dt:
        where.append("published_at <= ?")
        params.append(dt)

    sql = "SELECT score, company, title, url, source, location, remote, published_at FROM seen_jobs"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY score DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with _connect(db_path) as con:
        _ensure_columns(con)
        rows = con.execute(sql, params).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        out.append({
            "score": r["score"],
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "source": r["source"],
            "location": r["location"],
            "remote": None if r["remote"] is None else bool(r["remote"]),
            "published_at": r["published_at"],
        })
    return out

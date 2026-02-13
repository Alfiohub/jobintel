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
    q: str | None = None,
    company: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    return _list_jobs_common(
        db_path=db_path,
        q=q,
        company=company,
        source=source,
        remote=remote,
        location=location,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
        include_score=False,
        min_score=None,
    )


@app.get("/jobs/scored")
def list_scored_jobs(
    db_path: str = Query("data/jobintel.sqlite"),
    min_score: int | None = Query(None, ge=0, le=100),
    q: str | None = None,
    company: str | None = None,
    source: str | None = None,
    remote: bool | None = None,
    location: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    return _list_jobs_common(
        db_path=db_path,
        q=q,
        company=company,
        source=source,
        remote=remote,
        location=location,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
        include_score=True,
        min_score=min_score,
    )


def _list_jobs_common(
    *,
    db_path: str,
    q: str | None,
    company: str | None,
    source: str | None,
    remote: bool | None,
    location: str | None,
    date_from: str | None,
    date_to: str | None,
    limit: int,
    offset: int,
    include_score: bool,
    min_score: int | None,
) -> list[dict[str, Any]]:
    where = []
    params: list[Any] = []

    if min_score is not None:
        where.append("score >= ?")
        params.append(min_score)
    if q:
        where.append("(title LIKE ? OR company LIKE ? OR location LIKE ? OR url LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like, like, like])
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

    if include_score:
        sql = "SELECT score, company, title, url, source, location, remote, published_at FROM seen_jobs"
    else:
        sql = "SELECT company, title, url, source, location, remote, published_at FROM seen_jobs"

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY first_seen DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with _connect(db_path) as con:
        _ensure_columns(con)
        rows = con.execute(sql, params).fetchall()

    out: list[dict[str, Any]] = []
    for r in rows:
        item = {
            "company": r["company"],
            "title": r["title"],
            "url": r["url"],
            "source": r["source"],
            "location": r["location"],
            "remote": None if r["remote"] is None else bool(r["remote"]),
            "published_at": r["published_at"],
        }
        if include_score:
            item["score"] = r["score"]
        out.append(item)
    return out


@app.get("/filters")
def list_filters(
    db_path: str = Query("data/jobintel.sqlite"),
    top_companies: int = Query(50, ge=1, le=200),
    top_locations: int = Query(50, ge=1, le=200),
) -> dict[str, Any]:
    with _connect(db_path) as con:
        _ensure_columns(con)
        total_jobs = con.execute("SELECT COUNT(*) AS c FROM seen_jobs").fetchone()["c"]
        sources = [row["source"] for row in con.execute("SELECT DISTINCT source FROM seen_jobs ORDER BY source")]
        companies = [
            {"company": row["company"], "count": row["count"]}
            for row in con.execute(
                "SELECT company, COUNT(*) AS count FROM seen_jobs GROUP BY company ORDER BY count DESC, company ASC LIMIT ?",
                (top_companies,),
            )
        ]
        locations = [
            {"location": row["location"], "count": row["count"]}
            for row in con.execute(
                "SELECT location, COUNT(*) AS count FROM seen_jobs "
                "WHERE location IS NOT NULL AND location <> '' "
                "GROUP BY location ORDER BY count DESC, location ASC LIMIT ?",
                (top_locations,),
            )
        ]
        remote_counts = {
            str(row["remote"]): row["count"]
            for row in con.execute("SELECT remote, COUNT(*) AS count FROM seen_jobs GROUP BY remote")
        }

    return {
        "total_jobs": total_jobs,
        "sources": sources,
        "top_companies": companies,
        "top_locations": locations,
        "remote_counts": remote_counts,
    }

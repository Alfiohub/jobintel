from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Iterable


DEFAULT_JOB_STATE_DB_PATH = "data/jobs/job_state.db"
DEFAULT_USER_ID = "local-user"
DEFAULT_USER_EMAIL = "local@example.com"
JOB_STATE_VALUES = {"new", "seen", "saved", "dismissed"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_user(user_id: str | None, user_email: str | None = None) -> tuple[str, str]:
    uid = (user_id or "").strip() or DEFAULT_USER_ID
    email = (user_email or "").strip() or f"{uid}@local"
    return uid, email


def _connect(db_path: str | Path) -> sqlite3.Connection:
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS job_state (
            user_id TEXT NOT NULL,
            job_url TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('new','seen','saved','dismissed')),
            updated_at TEXT NOT NULL,
            PRIMARY KEY(user_id, job_url)
        );
        """
    )

    # Migration from old single-user schema (job_url PK without user_id).
    cols = {str(r[1]) for r in conn.execute("PRAGMA table_info(job_state)").fetchall()}
    if "user_id" not in cols:
        conn.execute("ALTER TABLE job_state RENAME TO job_state_old;")
        conn.execute(
            """
            CREATE TABLE job_state (
                user_id TEXT NOT NULL,
                job_url TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('new','seen','saved','dismissed')),
                updated_at TEXT NOT NULL,
                PRIMARY KEY(user_id, job_url)
            );
            """
        )
        conn.execute(
            """
            INSERT INTO job_state(user_id, job_url, state, updated_at)
            SELECT ?, job_url, state, updated_at FROM job_state_old
            """,
            (DEFAULT_USER_ID,),
        )
        conn.execute("DROP TABLE job_state_old;")

    conn.execute("CREATE INDEX IF NOT EXISTS idx_job_state_state ON job_state(state);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_job_state_user ON job_state(user_id);")
    conn.commit()


def _ensure_user(conn: sqlite3.Connection, *, user_id: str, user_email: str) -> None:
    now = _now_iso()
    conn.execute(
        """
        INSERT OR IGNORE INTO users (user_id, email, created_at, is_active)
        VALUES (?, ?, ?, 1)
        """,
        (user_id, user_email, now),
    )


def _validate_state(state: str) -> str:
    s = state.strip().lower()
    if s not in JOB_STATE_VALUES:
        raise ValueError(f"invalid job state: {state}")
    return s


def set_job_state(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    job_url: str,
    state: str,
    user_id: str = DEFAULT_USER_ID,
    user_email: str | None = None,
) -> dict[str, str]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, email = _normalize_user(user_id, user_email)
    normalized_state = _validate_state(state)
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        _ensure_user(conn, user_id=uid, user_email=email)
        conn.execute(
            """
            INSERT INTO job_state(user_id, job_url, state, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, job_url) DO UPDATE SET
              state=excluded.state,
              updated_at=excluded.updated_at;
            """,
            (uid, job_url.strip(), normalized_state, now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT job_url, state, updated_at FROM job_state WHERE user_id = ? AND job_url = ?",
            (uid, job_url.strip()),
        ).fetchone()
        return {"job_url": row["job_url"], "state": row["state"], "updated_at": row["updated_at"]}
    finally:
        conn.close()


def get_job_state(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    job_url: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute(
            "SELECT job_url, state, updated_at FROM job_state WHERE user_id = ? AND job_url = ?",
            (uid, job_url.strip()),
        ).fetchone()
        if row is None:
            return {"job_url": job_url.strip(), "state": "new", "updated_at": ""}
        return {"job_url": row["job_url"], "state": row["state"], "updated_at": row["updated_at"]}
    finally:
        conn.close()


def get_many_job_states(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    job_urls: Iterable[str],
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str]:
    cleaned = [u.strip() for u in job_urls if u and u.strip()]
    if not cleaned:
        return {}
    uid, _ = _normalize_user(user_id)
    placeholders = ",".join(["?"] * len(cleaned))
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        rows = conn.execute(
            f"SELECT job_url, state FROM job_state WHERE user_id = ? AND job_url IN ({placeholders})",
            [uid, *cleaned],
        ).fetchall()
        out = {str(r["job_url"]): str(r["state"]) for r in rows}
        for u in cleaned:
            out.setdefault(u, "new")
        return out
    finally:
        conn.close()


def clear_job_state(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    job_url: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str | bool]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute("DELETE FROM job_state WHERE user_id = ? AND job_url = ?", (uid, job_url.strip()))
        conn.commit()
        return {"job_url": job_url.strip(), "deleted": bool(cur.rowcount)}
    finally:
        conn.close()


def count_user_job_state_entries(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    user_id: str = DEFAULT_USER_ID,
) -> int:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute(
            "SELECT COUNT(1) AS c FROM job_state WHERE user_id = ?",
            (uid,),
        ).fetchone()
        return int(row["c"] or 0) if row is not None else 0
    finally:
        conn.close()


def count_user_job_states(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, int]:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT state, COUNT(1) AS c
            FROM job_state
            WHERE user_id = ?
            GROUP BY state
            """,
            (uid,),
        ).fetchall()
        out = {"new": 0, "seen": 0, "saved": 0, "dismissed": 0}
        for row in rows:
            state = str(row["state"] or "")
            if state in out:
                out[state] = int(row["c"] or 0)
        return out
    finally:
        conn.close()


def list_job_urls_by_state(
    *,
    db_path: str | Path = DEFAULT_JOB_STATE_DB_PATH,
    state: str,
    user_id: str = DEFAULT_USER_ID,
    limit: int | None = None,
) -> list[str]:
    normalized_state = _validate_state(state)
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        sql = "SELECT job_url FROM job_state WHERE user_id = ? AND state = ? ORDER BY updated_at DESC"
        params: list[object] = [uid, normalized_state]
        if limit is not None and limit > 0:
            sql += " LIMIT ?"
            params.append(int(limit))
        rows = conn.execute(sql, params).fetchall()
        return [str(r["job_url"]) for r in rows if str(r["job_url"] or "").strip()]
    finally:
        conn.close()

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4

from jobintel_next.pipelines.retrieval import QueryParams
from jobintel_next.serving import list_jobs, run_pack


DEFAULT_SAVED_DB_PATH = "data/jobs/saved_searches.db"
DEFAULT_USER_ID = "local-user"
DEFAULT_USER_EMAIL = "local@example.com"
SUPPORTED_FREQUENCIES = {"manual", "daily", "twice_daily"}
SUPPORTED_LIFECYCLES = {"active", "disabled", "archived"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: str | Path) -> sqlite3.Connection:
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def _parse_iso_datetime(value: str | None) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_user(user_id: str | None, user_email: str | None = None) -> tuple[str, str]:
    uid = (user_id or "").strip() or DEFAULT_USER_ID
    email = (user_email or "").strip() or f"{uid}@local"
    return uid, email


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
        CREATE TABLE IF NOT EXISTS saved_searches (
            search_id TEXT PRIMARY KEY,
            user_id TEXT,
            name TEXT NOT NULL,
            query_type TEXT NOT NULL CHECK(query_type IN ('filters', 'pack')),
            filters_json TEXT,
            pack_name TEXT,
            frequency TEXT NOT NULL DEFAULT 'daily',
            lifecycle TEXT NOT NULL DEFAULT 'active',
            is_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_run_at TEXT,
            last_seen_job_url TEXT
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_searches_enabled ON saved_searches(is_enabled);")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_search_seen (
            user_id TEXT,
            search_id TEXT NOT NULL,
            job_url TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            PRIMARY KEY(search_id, job_url),
            FOREIGN KEY(search_id) REFERENCES saved_searches(search_id) ON DELETE CASCADE
        );
        """
    )
    search_cols = {str(r[1]) for r in conn.execute("PRAGMA table_info(saved_searches)").fetchall()}
    if "user_id" not in search_cols:
        conn.execute("ALTER TABLE saved_searches ADD COLUMN user_id TEXT;")
    if "frequency" not in search_cols:
        conn.execute("ALTER TABLE saved_searches ADD COLUMN frequency TEXT NOT NULL DEFAULT 'daily';")
    if "lifecycle" not in search_cols:
        conn.execute("ALTER TABLE saved_searches ADD COLUMN lifecycle TEXT NOT NULL DEFAULT 'active';")
    conn.execute(
        "UPDATE saved_searches SET frequency = 'daily' WHERE frequency IS NULL OR TRIM(frequency) = ''"
    )
    conn.execute(
        "UPDATE saved_searches SET frequency = 'daily' WHERE frequency NOT IN ('manual', 'daily', 'twice_daily')"
    )
    conn.execute("UPDATE saved_searches SET lifecycle = 'active' WHERE lifecycle IS NULL OR TRIM(lifecycle) = ''")
    conn.execute("UPDATE saved_searches SET lifecycle = 'disabled' WHERE lifecycle = 'active' AND is_enabled = 0")
    conn.execute("UPDATE saved_searches SET lifecycle = 'active' WHERE lifecycle = 'disabled' AND is_enabled = 1")
    conn.execute("UPDATE saved_searches SET lifecycle = 'active' WHERE lifecycle NOT IN ('active', 'disabled', 'archived')")
    seen_cols = {str(r[1]) for r in conn.execute("PRAGMA table_info(saved_search_seen)").fetchall()}
    if "user_id" not in seen_cols:
        conn.execute("ALTER TABLE saved_search_seen ADD COLUMN user_id TEXT;")
    conn.execute("UPDATE saved_searches SET user_id = ? WHERE user_id IS NULL OR TRIM(user_id) = ''", (DEFAULT_USER_ID,))
    conn.execute("UPDATE saved_search_seen SET user_id = ? WHERE user_id IS NULL OR TRIM(user_id) = ''", (DEFAULT_USER_ID,))
    conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_searches_user ON saved_searches(user_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_search_seen_user ON saved_search_seen(user_id);")
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


def _parse_bool_int(v: Any) -> bool:
    return bool(int(v)) if v is not None else False


def _row_to_saved_search(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "search_id": row["search_id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "query_type": row["query_type"],
        "filters_json": row["filters_json"],
        "pack_name": row["pack_name"],
        "frequency": row["frequency"],
        "lifecycle": str(row["lifecycle"] or "active"),
        "is_enabled": _parse_bool_int(row["is_enabled"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_run_at": row["last_run_at"],
        "last_seen_job_url": row["last_seen_job_url"],
    }


def _queryparams_from_filters_dict(filters: dict[str, Any]) -> QueryParams:
    return QueryParams(
        normalized_title=filters.get("normalized_title"),
        role_family=filters.get("role_family"),
        language_bucket=filters.get("language_bucket"),
        location_type=filters.get("location_type"),
        employment_type=filters.get("employment_type"),
        has_salary=filters.get("has_salary"),
        has_skills=filters.get("has_skills"),
        title_is_other=filters.get("title_is_other"),
        skills_contains=filters.get("skills_contains"),
        salary_currency=filters.get("salary_currency"),
        sort_by=filters.get("sort_by", "published_at_desc"),
        limit=None,
    )


def _run_search_rows(
    *,
    saved_search: dict[str, Any],
    indexed_input_path: str | Path,
    indexed_sqlite_path: str | Path | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    if saved_search["query_type"] == "pack":
        if not saved_search.get("pack_name"):
            raise ValueError("saved search pack missing pack_name")
        return run_pack(
            input_path=indexed_input_path,
            sqlite_path=indexed_sqlite_path,
            pack_name=saved_search["pack_name"],
            limit=limit,
            offset=offset,
        )

    filters_raw = saved_search.get("filters_json")
    filters_obj: dict[str, Any]
    if filters_raw:
        parsed = json.loads(filters_raw)
        filters_obj = parsed if isinstance(parsed, dict) else {}
    else:
        filters_obj = {}

    query = _queryparams_from_filters_dict(filters_obj)
    return list_jobs(
        input_path=indexed_input_path,
        sqlite_path=indexed_sqlite_path,
        query=query,
        limit=limit,
        offset=offset,
    )


def create_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    name: str,
    query_type: str,
    filters_json: str | None = None,
    pack_name: str | None = None,
    frequency: str = "daily",
    is_enabled: bool = True,
    lifecycle: str | None = None,
    user_id: str = DEFAULT_USER_ID,
    user_email: str | None = None,
) -> dict[str, Any]:
    qt = query_type.strip().lower()
    if qt not in {"filters", "pack"}:
        raise ValueError("query_type must be 'filters' or 'pack'")
    if qt == "filters":
        if not filters_json:
            raise ValueError("filters_json is required for query_type=filters")
        parsed = json.loads(filters_json)
        if not isinstance(parsed, dict):
            raise ValueError("filters_json must encode a JSON object")
    if qt == "pack" and not pack_name:
        raise ValueError("pack_name is required for query_type=pack")
    freq = frequency.strip().lower()
    if freq not in SUPPORTED_FREQUENCIES:
        raise ValueError("frequency must be one of: manual, daily, twice_daily")
    lifecycle_norm = (lifecycle or "").strip().lower() or ("active" if is_enabled else "disabled")
    if lifecycle_norm not in SUPPORTED_LIFECYCLES:
        raise ValueError("lifecycle must be one of: active, disabled, archived")
    enabled_effective = bool(is_enabled) and lifecycle_norm == "active"

    sid = str(uuid4())
    now = _now_iso()
    uid, email = _normalize_user(user_id, user_email)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        _ensure_user(conn, user_id=uid, user_email=email)
        conn.execute(
            """
            INSERT INTO saved_searches (
                search_id, user_id, name, query_type, filters_json, pack_name,
                frequency, lifecycle, is_enabled, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                uid,
                name,
                qt,
                filters_json,
                pack_name,
                freq,
                lifecycle_norm,
                1 if enabled_effective else 0,
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (sid, uid)).fetchone()
        return _row_to_saved_search(row)
    finally:
        conn.close()


def list_saved_searches(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    user_id: str = DEFAULT_USER_ID,
    lifecycle: str = "all",
) -> list[dict[str, Any]]:
    uid, _ = _normalize_user(user_id)
    lifecycle_norm = lifecycle.strip().lower() or "all"
    if lifecycle_norm not in {"all", *SUPPORTED_LIFECYCLES}:
        raise ValueError("lifecycle filter must be one of: all, active, disabled, archived")
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        if lifecycle_norm == "all":
            rows = conn.execute(
                "SELECT * FROM saved_searches WHERE user_id = ? ORDER BY created_at DESC, search_id DESC",
                (uid,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM saved_searches
                WHERE user_id = ? AND lifecycle = ?
                ORDER BY created_at DESC, search_id DESC
                """,
                (uid, lifecycle_norm),
            ).fetchall()
        return [_row_to_saved_search(r) for r in rows]
    finally:
        conn.close()


def get_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        if row is None:
            raise ValueError(f"saved search not found: {search_id}")
        return _row_to_saved_search(row)
    finally:
        conn.close()


def _set_enabled(*, db_path: str | Path, search_id: str, enabled: bool, user_id: str) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    now = _now_iso()
    lifecycle = "active" if enabled else "disabled"
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute(
            """
            UPDATE saved_searches
            SET is_enabled = ?, lifecycle = ?, updated_at = ?
            WHERE search_id = ? AND user_id = ?
            """,
            (1 if enabled else 0, lifecycle, now, search_id, uid),
        )
        if cur.rowcount == 0:
            raise ValueError(f"saved search not found: {search_id}")
        conn.commit()
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        return _row_to_saved_search(row)
    finally:
        conn.close()


def enable_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    return _set_enabled(db_path=db_path, search_id=search_id, enabled=True, user_id=user_id)


def disable_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    return _set_enabled(db_path=db_path, search_id=search_id, enabled=False, user_id=user_id)


def update_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    name: str,
    query_type: str,
    filters_json: str | None = None,
    pack_name: str | None = None,
    frequency: str = "daily",
    is_enabled: bool = True,
    lifecycle: str | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    qt = query_type.strip().lower()
    if qt not in {"filters", "pack"}:
        raise ValueError("query_type must be 'filters' or 'pack'")
    normalized_filters: str | None = None
    normalized_pack: str | None = None
    if qt == "filters":
        if not filters_json:
            raise ValueError("filters_json is required for query_type=filters")
        parsed = json.loads(filters_json)
        if not isinstance(parsed, dict):
            raise ValueError("filters_json must encode a JSON object")
        normalized_filters = filters_json
    else:
        if not pack_name:
            raise ValueError("pack_name is required for query_type=pack")
        normalized_pack = pack_name
    freq = frequency.strip().lower()
    if freq not in SUPPORTED_FREQUENCIES:
        raise ValueError("frequency must be one of: manual, daily, twice_daily")
    lifecycle_norm = (lifecycle or "").strip().lower() or ("active" if is_enabled else "disabled")
    if lifecycle_norm not in SUPPORTED_LIFECYCLES:
        raise ValueError("lifecycle must be one of: active, disabled, archived")
    enabled_effective = bool(is_enabled) and lifecycle_norm == "active"

    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute(
            """
            UPDATE saved_searches
            SET name = ?, query_type = ?, filters_json = ?, pack_name = ?, frequency = ?, lifecycle = ?, is_enabled = ?, updated_at = ?
            WHERE search_id = ? AND user_id = ?
            """,
            (
                name,
                qt,
                normalized_filters,
                normalized_pack,
                freq,
                lifecycle_norm,
                1 if enabled_effective else 0,
                now,
                search_id,
                uid,
            ),
        )
        if cur.rowcount == 0:
            raise ValueError(f"saved search not found: {search_id}")
        conn.commit()
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        return _row_to_saved_search(row)
    finally:
        conn.close()


def _set_lifecycle(*, db_path: str | Path, search_id: str, lifecycle: str, user_id: str) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    lifecycle_norm = lifecycle.strip().lower()
    if lifecycle_norm not in SUPPORTED_LIFECYCLES:
        raise ValueError("lifecycle must be one of: active, disabled, archived")
    now = _now_iso()
    enabled = 1 if lifecycle_norm == "active" else 0
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute(
            """
            UPDATE saved_searches
            SET lifecycle = ?, is_enabled = ?, updated_at = ?
            WHERE search_id = ? AND user_id = ?
            """,
            (lifecycle_norm, enabled, now, search_id, uid),
        )
        if cur.rowcount == 0:
            raise ValueError(f"saved search not found: {search_id}")
        conn.commit()
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        return _row_to_saved_search(row)
    finally:
        conn.close()


def archive_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    return _set_lifecycle(db_path=db_path, search_id=search_id, lifecycle="archived", user_id=user_id)


def restore_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    return _set_lifecycle(db_path=db_path, search_id=search_id, lifecycle="disabled", user_id=user_id)


def delete_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        if row is None:
            raise ValueError(f"saved search not found: {search_id}")
        deleted = _row_to_saved_search(row)
        conn.execute("DELETE FROM saved_search_seen WHERE search_id = ? AND user_id = ?", (search_id, uid))
        conn.execute("DELETE FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid))
        conn.commit()
        return {"deleted": True, "saved_search": deleted}
    finally:
        conn.close()


def run_saved_search(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    indexed_input_path: str | Path = "data/jobs/jobs_indexed_en.jsonl",
    indexed_sqlite_path: str | Path | None = None,
    limit: int = 100,
    offset: int = 0,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        if row is None:
            raise ValueError(f"saved search not found: {search_id}")
        saved = _row_to_saved_search(row)
        results = _run_search_rows(
            saved_search=saved,
            indexed_input_path=indexed_input_path,
            indexed_sqlite_path=indexed_sqlite_path,
            limit=limit,
            offset=offset,
        )
        last_url = None
        if results.get("results"):
            first = results["results"][0]
            last_url = str(first.get("url") or "") or None
        conn.execute(
            "UPDATE saved_searches SET last_run_at = ?, last_seen_job_url = ?, updated_at = ? WHERE search_id = ? AND user_id = ?",
            (now, last_url, now, search_id, uid),
        )
        conn.commit()
        saved_after = conn.execute(
            "SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?",
            (search_id, uid),
        ).fetchone()
        return {
            "saved_search": _row_to_saved_search(saved_after),
            "run_result": results,
        }
    finally:
        conn.close()


def check_new_matches(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    indexed_input_path: str | Path = "data/jobs/jobs_indexed_en.jsonl",
    indexed_sqlite_path: str | Path | None = None,
    scan_limit: int = 5000,
    return_limit: int = 100,
    offset: int = 0,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        if row is None:
            raise ValueError(f"saved search not found: {search_id}")
        saved = _row_to_saved_search(row)
        current = _run_search_rows(
            saved_search=saved,
            indexed_input_path=indexed_input_path,
            indexed_sqlite_path=indexed_sqlite_path,
            limit=scan_limit,
            offset=0,
        )
        urls = [str(r.get("url") or "") for r in current["results"] if str(r.get("url") or "")]
        seen_rows = conn.execute(
            "SELECT job_url FROM saved_search_seen WHERE search_id = ? AND user_id = ?",
            (search_id, uid),
        ).fetchall()
        seen_urls = {str(r["job_url"]) for r in seen_rows}
        new_urls = {u for u in urls if u not in seen_urls}
        new_rows_all = [r for r in current["results"] if str(r.get("url") or "") in new_urls]

        conn.executemany(
            "INSERT OR IGNORE INTO saved_search_seen (user_id, search_id, job_url, first_seen_at) VALUES (?, ?, ?, ?)",
            [(uid, search_id, u, now) for u in urls],
        )
        last_url = urls[0] if urls else None
        conn.execute(
            "UPDATE saved_searches SET last_run_at = ?, last_seen_job_url = ?, updated_at = ? WHERE search_id = ? AND user_id = ?",
            (now, last_url, now, search_id, uid),
        )
        conn.commit()
        saved_after = conn.execute(
            "SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?",
            (search_id, uid),
        ).fetchone()

        new_rows_paged = new_rows_all[offset : offset + return_limit]
        current_rows_paged = current["results"][offset : offset + return_limit]
        return {
            "saved_search": _row_to_saved_search(saved_after),
            "current_count": len(current["results"]),
            "new_count": len(new_rows_all),
            "current_results": current_rows_paged,
            "new_results": new_rows_paged,
            "scan_limit": scan_limit,
            "return_limit": return_limit,
            "offset": offset,
        }
    finally:
        conn.close()


def get_saved_search_results(
    *,
    db_path: str | Path = DEFAULT_SAVED_DB_PATH,
    search_id: str,
    indexed_input_path: str | Path = "data/jobs/jobs_indexed_en.jsonl",
    indexed_sqlite_path: str | Path | None = None,
    limit: int = 100,
    offset: int = 0,
    new_only: bool = False,
    scan_limit: int = 5000,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT * FROM saved_searches WHERE search_id = ? AND user_id = ?", (search_id, uid)).fetchone()
        if row is None:
            raise ValueError(f"saved search not found: {search_id}")
        saved = _row_to_saved_search(row)

        if not new_only:
            rep = _run_search_rows(
                saved_search=saved,
                indexed_input_path=indexed_input_path,
                indexed_sqlite_path=indexed_sqlite_path,
                limit=limit,
                offset=offset,
            )
            return {
                "saved_search": saved,
                "mode": "current",
                "current_count": int(rep.get("total_count") or len(rep.get("results", []))),
                "new_count": None,
                "limit": limit,
                "offset": offset,
                "results": rep.get("results", []),
            }

        current = _run_search_rows(
            saved_search=saved,
            indexed_input_path=indexed_input_path,
            indexed_sqlite_path=indexed_sqlite_path,
            limit=scan_limit,
            offset=0,
        )
        urls = [str(r.get("url") or "") for r in current["results"] if str(r.get("url") or "")]
        seen_rows = conn.execute(
            "SELECT job_url FROM saved_search_seen WHERE search_id = ? AND user_id = ?",
            (search_id, uid),
        ).fetchall()
        seen_urls = {str(r["job_url"]) for r in seen_rows}
        new_rows_all = [r for r in current["results"] if str(r.get("url") or "") not in seen_urls]
        paged = new_rows_all[offset : offset + limit]
        return {
            "saved_search": saved,
            "mode": "new_only",
            "current_count": len(current["results"]),
            "new_count": len(new_rows_all),
            "limit": limit,
            "offset": offset,
            "results": paged,
        }
    finally:
        conn.close()


def is_saved_search_due(
    saved_search: dict[str, Any],
    *,
    now: datetime | None = None,
) -> bool:
    if str(saved_search.get("lifecycle") or "active").strip().lower() != "active":
        return False
    if not bool(saved_search.get("is_enabled")):
        return False
    freq = str(saved_search.get("frequency") or "daily").strip().lower()
    if freq == "manual":
        return False
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    last_run_at = _parse_iso_datetime(saved_search.get("last_run_at"))
    if last_run_at is None:
        return True
    delta_seconds = (now_utc - last_run_at).total_seconds()
    if freq == "twice_daily":
        return delta_seconds >= 12 * 3600
    if freq == "daily":
        return delta_seconds >= 24 * 3600
    return False

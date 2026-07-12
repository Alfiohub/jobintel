from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Iterable
from uuid import uuid4


DEFAULT_APPLICATION_DB_PATH = "data/jobs/job_state.db"
DEFAULT_USER_ID = "local-user"
DEFAULT_USER_EMAIL = "local@example.com"
APPLICATION_STATES = {"saved", "applied", "interview", "rejected"}
APPLICATION_TEMPLATE_KINDS = {"resume", "cover_letter"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
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
        CREATE TABLE IF NOT EXISTS application_state (
            user_id TEXT NOT NULL,
            job_url TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('saved','applied','interview','rejected')),
            updated_at TEXT NOT NULL,
            PRIMARY KEY(user_id, job_url)
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS application_details (
            user_id TEXT NOT NULL,
            job_url TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            applied_at TEXT,
            interview_at TEXT,
            follow_up_at TEXT,
            follow_up_note TEXT NOT NULL DEFAULT '',
            application_channel TEXT NOT NULL DEFAULT '',
            contact_name TEXT NOT NULL DEFAULT '',
            contact_email TEXT NOT NULL DEFAULT '',
            compensation_note TEXT NOT NULL DEFAULT '',
            external_application_url TEXT NOT NULL DEFAULT '',
            resume_label TEXT NOT NULL DEFAULT '',
            cover_letter_label TEXT NOT NULL DEFAULT '',
            submission_note TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY(user_id, job_url)
        );
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS application_templates (
            template_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN ('resume','cover_letter')),
            label TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    details_cols = {str(r[1]) for r in conn.execute("PRAGMA table_info(application_details)").fetchall()}
    if "follow_up_at" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN follow_up_at TEXT;")
    if "follow_up_note" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN follow_up_note TEXT NOT NULL DEFAULT '';")
    if "application_channel" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN application_channel TEXT NOT NULL DEFAULT '';")
    if "contact_name" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN contact_name TEXT NOT NULL DEFAULT '';")
    if "contact_email" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN contact_email TEXT NOT NULL DEFAULT '';")
    if "compensation_note" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN compensation_note TEXT NOT NULL DEFAULT '';")
    if "external_application_url" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN external_application_url TEXT NOT NULL DEFAULT '';")
    if "resume_label" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN resume_label TEXT NOT NULL DEFAULT '';")
    if "cover_letter_label" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN cover_letter_label TEXT NOT NULL DEFAULT '';")
    if "submission_note" not in details_cols:
        conn.execute("ALTER TABLE application_details ADD COLUMN submission_note TEXT NOT NULL DEFAULT '';")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_application_state_user ON application_state(user_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_application_state_state ON application_state(state);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_application_details_user ON application_details(user_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_application_templates_user ON application_templates(user_id);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_application_templates_kind ON application_templates(kind);")
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
    if s not in APPLICATION_STATES:
        raise ValueError("invalid application state")
    return s


def _validate_template_kind(kind: str) -> str:
    k = kind.strip().lower()
    if k not in APPLICATION_TEMPLATE_KINDS:
        raise ValueError("invalid template kind")
    return k


def set_application_state(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_url: str,
    state: str,
    user_id: str = DEFAULT_USER_ID,
    user_email: str | None = None,
) -> dict[str, str]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, email = _normalize_user(user_id, user_email)
    st = _validate_state(state)
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        _ensure_user(conn, user_id=uid, user_email=email)
        conn.execute(
            """
            INSERT INTO application_state(user_id, job_url, state, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, job_url) DO UPDATE SET
              state=excluded.state,
              updated_at=excluded.updated_at
            """,
            (uid, job_url.strip(), st, now),
        )
        if st in {"applied", "interview"}:
            col = "applied_at" if st == "applied" else "interview_at"
            conn.execute(
                f"""
                INSERT INTO application_details(user_id, job_url, notes, {col}, updated_at)
                VALUES (?, ?, '', ?, ?)
                ON CONFLICT(user_id, job_url) DO UPDATE SET
                  {col}=COALESCE(application_details.{col}, excluded.{col}),
                  updated_at=excluded.updated_at
                """,
                (uid, job_url.strip(), now, now),
            )
        conn.commit()
        row = conn.execute(
            "SELECT job_url, state, updated_at FROM application_state WHERE user_id = ? AND job_url = ?",
            (uid, job_url.strip()),
        ).fetchone()
        return {"job_url": row["job_url"], "state": row["state"], "updated_at": row["updated_at"]}
    finally:
        conn.close()


def get_application_state(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
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
            "SELECT job_url, state, updated_at FROM application_state WHERE user_id = ? AND job_url = ?",
            (uid, job_url.strip()),
        ).fetchone()
        if row is None:
            return {"job_url": job_url.strip(), "state": "saved", "updated_at": ""}
        return {"job_url": row["job_url"], "state": row["state"], "updated_at": row["updated_at"]}
    finally:
        conn.close()


def get_many_application_states(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
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
            f"SELECT job_url, state FROM application_state WHERE user_id = ? AND job_url IN ({placeholders})",
            [uid, *cleaned],
        ).fetchall()
        out = {str(r["job_url"]): str(r["state"]) for r in rows}
        for u in cleaned:
            out.setdefault(u, "saved")
        return out
    finally:
        conn.close()


def clear_application_state(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_url: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str | bool]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute("DELETE FROM application_state WHERE user_id = ? AND job_url = ?", (uid, job_url.strip()))
        conn.commit()
        return {"job_url": job_url.strip(), "deleted": bool(cur.rowcount)}
    finally:
        conn.close()


def count_application_states(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_urls: Iterable[str],
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, int]:
    states = get_many_application_states(db_path=db_path, job_urls=job_urls, user_id=user_id)
    counts = {"saved": 0, "applied": 0, "interview": 0, "rejected": 0}
    for st in states.values():
        if st in counts:
            counts[st] += 1
    return counts


def build_closed_loop_metrics(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_urls: Iterable[str],
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, int | float]:
    counts = count_application_states(db_path=db_path, job_urls=job_urls, user_id=user_id)
    saved_count = int(counts.get("saved") or 0)
    applied_count = int(counts.get("applied") or 0)
    interview_count = int(counts.get("interview") or 0)
    rejected_count = int(counts.get("rejected") or 0)
    total_count = saved_count + applied_count + interview_count + rejected_count
    open_pipeline_count = saved_count + applied_count + interview_count
    return {
        "total_count": total_count,
        "open_pipeline_count": open_pipeline_count,
        "saved_count": saved_count,
        "applied_count": applied_count,
        "interview_count": interview_count,
        "rejected_count": rejected_count,
        "saved_to_applied_rate": (applied_count / total_count) if total_count > 0 else 0.0,
        "applied_to_interview_rate": (interview_count / applied_count) if applied_count > 0 else 0.0,
        "interview_to_rejected_rate": (rejected_count / interview_count) if interview_count > 0 else 0.0,
    }


def get_application_details(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
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
            """
            SELECT job_url, notes, applied_at, interview_at, follow_up_at, follow_up_note,
                   application_channel, contact_name, contact_email, compensation_note, external_application_url,
                   resume_label, cover_letter_label, submission_note,
                   updated_at
            FROM application_details
            WHERE user_id = ? AND job_url = ?
            """,
            (uid, job_url.strip()),
        ).fetchone()
        if row is None:
            return {
                "job_url": job_url.strip(),
                "notes": "",
                "applied_at": "",
                "interview_at": "",
                "follow_up_at": "",
                "follow_up_note": "",
                "application_channel": "",
                "contact_name": "",
                "contact_email": "",
                "compensation_note": "",
                "external_application_url": "",
                "resume_label": "",
                "cover_letter_label": "",
                "submission_note": "",
                "updated_at": "",
            }
        return {
            "job_url": str(row["job_url"]),
            "notes": str(row["notes"] or ""),
            "applied_at": str(row["applied_at"] or ""),
            "interview_at": str(row["interview_at"] or ""),
            "follow_up_at": str(row["follow_up_at"] or ""),
            "follow_up_note": str(row["follow_up_note"] or ""),
            "application_channel": str(row["application_channel"] or ""),
            "contact_name": str(row["contact_name"] or ""),
            "contact_email": str(row["contact_email"] or ""),
            "compensation_note": str(row["compensation_note"] or ""),
            "external_application_url": str(row["external_application_url"] or ""),
            "resume_label": str(row["resume_label"] or ""),
            "cover_letter_label": str(row["cover_letter_label"] or ""),
            "submission_note": str(row["submission_note"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }
    finally:
        conn.close()


def get_many_application_details(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_urls: Iterable[str],
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, dict[str, str]]:
    cleaned = [u.strip() for u in job_urls if u and u.strip()]
    if not cleaned:
        return {}
    uid, _ = _normalize_user(user_id)
    placeholders = ",".join(["?"] * len(cleaned))
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        rows = conn.execute(
            f"""
            SELECT job_url, notes, applied_at, interview_at, follow_up_at, follow_up_note,
                   application_channel, contact_name, contact_email, compensation_note, external_application_url,
                   resume_label, cover_letter_label, submission_note,
                   updated_at
            FROM application_details
            WHERE user_id = ? AND job_url IN ({placeholders})
            """,
            [uid, *cleaned],
        ).fetchall()
        out = {
            str(r["job_url"]): {
                "job_url": str(r["job_url"]),
                "notes": str(r["notes"] or ""),
                "applied_at": str(r["applied_at"] or ""),
                "interview_at": str(r["interview_at"] or ""),
                "follow_up_at": str(r["follow_up_at"] or ""),
                "follow_up_note": str(r["follow_up_note"] or ""),
                "application_channel": str(r["application_channel"] or ""),
                "contact_name": str(r["contact_name"] or ""),
                "contact_email": str(r["contact_email"] or ""),
                "compensation_note": str(r["compensation_note"] or ""),
                "external_application_url": str(r["external_application_url"] or ""),
                "resume_label": str(r["resume_label"] or ""),
                "cover_letter_label": str(r["cover_letter_label"] or ""),
                "submission_note": str(r["submission_note"] or ""),
                "updated_at": str(r["updated_at"] or ""),
            }
            for r in rows
        }
        for u in cleaned:
            out.setdefault(
                u,
                {
                    "job_url": u,
                    "notes": "",
                    "applied_at": "",
                    "interview_at": "",
                    "follow_up_at": "",
                    "follow_up_note": "",
                    "application_channel": "",
                    "contact_name": "",
                    "contact_email": "",
                    "compensation_note": "",
                    "external_application_url": "",
                    "resume_label": "",
                    "cover_letter_label": "",
                    "submission_note": "",
                    "updated_at": "",
                },
            )
        return out
    finally:
        conn.close()


def update_application_details(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_url: str,
    notes: str = "",
    applied_at: str | None = None,
    interview_at: str | None = None,
    follow_up_at: str | None = None,
    follow_up_note: str = "",
    application_channel: str = "",
    contact_name: str = "",
    contact_email: str = "",
    compensation_note: str = "",
    external_application_url: str = "",
    resume_label: str = "",
    cover_letter_label: str = "",
    submission_note: str = "",
    user_id: str = DEFAULT_USER_ID,
    user_email: str | None = None,
) -> dict[str, str]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, email = _normalize_user(user_id, user_email)
    now = _now_iso()
    notes_clean = notes.strip()
    applied_clean = (applied_at or "").strip() or None
    interview_clean = (interview_at or "").strip() or None
    follow_up_clean = (follow_up_at or "").strip() or None
    follow_up_note_clean = follow_up_note.strip()
    application_channel_clean = application_channel.strip().lower()
    contact_name_clean = contact_name.strip()
    contact_email_clean = contact_email.strip()
    compensation_note_clean = compensation_note.strip()
    external_application_url_clean = external_application_url.strip()
    resume_label_clean = resume_label.strip()
    cover_letter_label_clean = cover_letter_label.strip()
    submission_note_clean = submission_note.strip()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        _ensure_user(conn, user_id=uid, user_email=email)
        conn.execute(
            """
            INSERT INTO application_details(
              user_id, job_url, notes, applied_at, interview_at, follow_up_at, follow_up_note,
              application_channel, contact_name, contact_email, compensation_note, external_application_url,
              resume_label, cover_letter_label, submission_note,
              updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, job_url) DO UPDATE SET
              notes=excluded.notes,
              applied_at=excluded.applied_at,
              interview_at=excluded.interview_at,
              follow_up_at=excluded.follow_up_at,
              follow_up_note=excluded.follow_up_note,
              application_channel=excluded.application_channel,
              contact_name=excluded.contact_name,
              contact_email=excluded.contact_email,
              compensation_note=excluded.compensation_note,
              external_application_url=excluded.external_application_url,
              resume_label=excluded.resume_label,
              cover_letter_label=excluded.cover_letter_label,
              submission_note=excluded.submission_note,
              updated_at=excluded.updated_at
            """,
            (
                uid,
                job_url.strip(),
                notes_clean,
                applied_clean,
                interview_clean,
                follow_up_clean,
                follow_up_note_clean,
                application_channel_clean,
                contact_name_clean,
                contact_email_clean,
                compensation_note_clean,
                external_application_url_clean,
                resume_label_clean,
                cover_letter_label_clean,
                submission_note_clean,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_application_details(db_path=db_path, job_url=job_url.strip(), user_id=uid)


def clear_application_details(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    job_url: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str | bool]:
    if not job_url or not job_url.strip():
        raise ValueError("job_url is required")
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute(
            "DELETE FROM application_details WHERE user_id = ? AND job_url = ?",
            (uid, job_url.strip()),
        )
        conn.commit()
        return {"job_url": job_url.strip(), "deleted": bool(cur.rowcount)}
    finally:
        conn.close()


def list_follow_up_items(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    user_id: str = DEFAULT_USER_ID,
    now: datetime | None = None,
    limit: int = 100,
) -> list[dict[str, str]]:
    uid, _ = _normalize_user(user_id)
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        rows = conn.execute(
            """
            SELECT job_url, follow_up_at, follow_up_note
            FROM application_details
            WHERE user_id = ? AND follow_up_at IS NOT NULL AND TRIM(follow_up_at) != ''
            ORDER BY follow_up_at ASC
            LIMIT ?
            """,
            (uid, max(1, int(limit))),
        ).fetchall()
        ref = now or datetime.now(timezone.utc)
        out: list[dict[str, str]] = []
        for row in rows:
            follow = str(row["follow_up_at"] or "")
            dt = _parse_iso(follow)
            status = "scheduled"
            if dt is not None:
                if dt <= ref:
                    status = "overdue"
                elif dt <= (ref + timedelta(days=2)):
                    status = "due"
            out.append(
                {
                    "job_url": str(row["job_url"] or ""),
                    "follow_up_at": follow,
                    "follow_up_note": str(row["follow_up_note"] or ""),
                    "follow_up_status": status,
                }
            )
        return out
    finally:
        conn.close()


def create_application_template(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    kind: str,
    label: str,
    description: str = "",
    is_active: bool = True,
    user_id: str = DEFAULT_USER_ID,
    user_email: str | None = None,
) -> dict[str, str | bool]:
    uid, email = _normalize_user(user_id, user_email)
    k = _validate_template_kind(kind)
    label_clean = label.strip()
    if not label_clean:
        raise ValueError("label is required")
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        _ensure_user(conn, user_id=uid, user_email=email)
        template_id = str(uuid4())
        conn.execute(
            """
            INSERT INTO application_templates(
              template_id, user_id, kind, label, description, is_active, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (template_id, uid, k, label_clean, description.strip(), 1 if is_active else 0, now, now),
        )
        conn.commit()
        return {
            "template_id": template_id,
            "user_id": uid,
            "kind": k,
            "label": label_clean,
            "description": description.strip(),
            "is_active": bool(is_active),
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def list_application_templates(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    user_id: str = DEFAULT_USER_ID,
    kind: str | None = None,
    include_inactive: bool = True,
) -> list[dict[str, str | bool]]:
    uid, _ = _normalize_user(user_id)
    kind_clean: str | None = None
    if kind is not None and str(kind).strip():
        kind_clean = _validate_template_kind(str(kind))
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        clauses = ["user_id = ?"]
        params: list[object] = [uid]
        if kind_clean:
            clauses.append("kind = ?")
            params.append(kind_clean)
        if not include_inactive:
            clauses.append("is_active = 1")
        where = " AND ".join(clauses)
        rows = conn.execute(
            f"""
            SELECT template_id, user_id, kind, label, description, is_active, created_at, updated_at
            FROM application_templates
            WHERE {where}
            ORDER BY kind ASC, is_active DESC, label ASC, created_at DESC
            """,
            params,
        ).fetchall()
        return [
            {
                "template_id": str(r["template_id"] or ""),
                "user_id": str(r["user_id"] or ""),
                "kind": str(r["kind"] or ""),
                "label": str(r["label"] or ""),
                "description": str(r["description"] or ""),
                "is_active": bool(r["is_active"]),
                "created_at": str(r["created_at"] or ""),
                "updated_at": str(r["updated_at"] or ""),
            }
            for r in rows
        ]
    finally:
        conn.close()


def set_application_template_active(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    template_id: str,
    is_active: bool,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str | bool]:
    uid, _ = _normalize_user(user_id)
    tid = template_id.strip()
    if not tid:
        raise ValueError("template_id is required")
    now = _now_iso()
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute(
            """
            UPDATE application_templates
            SET is_active = ?, updated_at = ?
            WHERE template_id = ? AND user_id = ?
            """,
            (1 if is_active else 0, now, tid, uid),
        )
        conn.commit()
        if cur.rowcount <= 0:
            raise ValueError("template not found")
        row = conn.execute(
            """
            SELECT template_id, user_id, kind, label, description, is_active, created_at, updated_at
            FROM application_templates
            WHERE template_id = ? AND user_id = ?
            """,
            (tid, uid),
        ).fetchone()
        if row is None:
            raise ValueError("template not found")
        return {
            "template_id": str(row["template_id"] or ""),
            "user_id": str(row["user_id"] or ""),
            "kind": str(row["kind"] or ""),
            "label": str(row["label"] or ""),
            "description": str(row["description"] or ""),
            "is_active": bool(row["is_active"]),
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }
    finally:
        conn.close()


def delete_application_template(
    *,
    db_path: str | Path = DEFAULT_APPLICATION_DB_PATH,
    template_id: str,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, str | bool]:
    uid, _ = _normalize_user(user_id)
    tid = template_id.strip()
    if not tid:
        raise ValueError("template_id is required")
    conn = _connect(db_path)
    try:
        _ensure_schema(conn)
        cur = conn.execute("DELETE FROM application_templates WHERE template_id = ? AND user_id = ?", (tid, uid))
        conn.commit()
        return {"template_id": tid, "deleted": bool(cur.rowcount)}
    finally:
        conn.close()

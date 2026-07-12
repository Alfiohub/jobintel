from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
from pathlib import Path
import secrets
import sqlite3
from typing import Any
from uuid import uuid5, NAMESPACE_DNS


DEFAULT_AUTH_DB_PATH = "data/jobs/saved_searches.db"
PBKDF2_ITERATIONS = 120_000
MIN_PASSWORD_LENGTH = 8


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: str | Path) -> sqlite3.Connection:
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str, *, salt: str | None = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        alg, iter_s, salt, digest = encoded.split("$", 3)
        if alg != "pbkdf2_sha256":
            return False
        iterations = int(iter_s)
    except Exception:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations).hex()
    return hmac.compare_digest(check, digest)


def _validate_new_password(password: str) -> None:
    if not password:
        raise ValueError("new password is required")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"new password must be at least {MIN_PASSWORD_LENGTH} characters")


def ensure_auth_schema(*, db_path: str | Path = DEFAULT_AUTH_DB_PATH) -> None:
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                created_at TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );
            """
        )
        cols = {str(r[1]) for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "password_hash" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT;")
        if "default_alert_email" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN default_alert_email TEXT;")
        if "include_dismissed_default" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN include_dismissed_default INTEGER NOT NULL DEFAULT 1;")
        if "show_saved_search_quality_attention" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN show_saved_search_quality_attention INTEGER NOT NULL DEFAULT 1;")
        if "show_due_saved_search_attention" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN show_due_saved_search_attention INTEGER NOT NULL DEFAULT 1;")
        if "show_follow_up_attention" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN show_follow_up_attention INTEGER NOT NULL DEFAULT 1;")
        if "show_digest_error_attention" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN show_digest_error_attention INTEGER NOT NULL DEFAULT 1;")
        if "digest_include_attention" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN digest_include_attention INTEGER NOT NULL DEFAULT 1;")
        if "target_titles" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN target_titles TEXT NOT NULL DEFAULT '';")
        if "target_role_families" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN target_role_families TEXT NOT NULL DEFAULT '';")
        if "preferred_location_types" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN preferred_location_types TEXT NOT NULL DEFAULT '';")
        if "salary_target_note" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN salary_target_note TEXT NOT NULL DEFAULT '';")
        if "keywords_note" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN keywords_note TEXT NOT NULL DEFAULT '';")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        conn.commit()
    finally:
        conn.close()


def create_local_user(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    email: str,
    password: str,
    user_id: str | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    em = email.strip().lower()
    if not em:
        raise ValueError("email is required")
    _validate_new_password(password)
    uid = (user_id or str(uuid5(NAMESPACE_DNS, em))).strip()
    now = _now_iso()
    pwd = _hash_password(password)

    conn = _connect(db_path)
    try:
        ensure_auth_schema(db_path=db_path)
        existing_by_uid = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)).fetchone()
        existing_by_email = conn.execute("SELECT user_id FROM users WHERE email = ?", (em,)).fetchone()
        if existing_by_uid is not None:
            conn.execute(
                """
                UPDATE users
                SET email = ?, password_hash = ?, is_active = ?
                WHERE user_id = ?;
                """,
                (em, pwd, 1 if is_active else 0, uid),
            )
        elif existing_by_email is not None:
            conn.execute(
                """
                UPDATE users
                SET user_id = ?, password_hash = ?, is_active = ?
                WHERE email = ?;
                """,
                (uid, pwd, 1 if is_active else 0, em),
            )
        else:
            conn.execute(
                """
                INSERT INTO users(user_id, email, password_hash, created_at, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uid, em, pwd, now, 1 if is_active else 0),
            )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (em,)).fetchone()
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "created_at": row["created_at"],
            "is_active": bool(row["is_active"]),
        }
    finally:
        conn.close()


def authenticate_local_user(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    email: str,
    password: str,
) -> dict[str, Any] | None:
    em = email.strip().lower()
    if not em or not password:
        return None
    conn = _connect(db_path)
    try:
        ensure_auth_schema(db_path=db_path)
        row = conn.execute("SELECT * FROM users WHERE email = ?", (em,)).fetchone()
        if row is None:
            return None
        if not bool(row["is_active"]):
            return None
        password_hash = str(row["password_hash"] or "")
        if not password_hash or not _verify_password(password, password_hash):
            return None
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "created_at": row["created_at"],
            "is_active": bool(row["is_active"]),
            "default_alert_email": row["default_alert_email"],
            "include_dismissed_default": bool(row["include_dismissed_default"]),
            "show_saved_search_quality_attention": bool(
                1 if row["show_saved_search_quality_attention"] is None else row["show_saved_search_quality_attention"]
            ),
            "show_due_saved_search_attention": bool(
                1 if row["show_due_saved_search_attention"] is None else row["show_due_saved_search_attention"]
            ),
            "show_follow_up_attention": bool(1 if row["show_follow_up_attention"] is None else row["show_follow_up_attention"]),
            "show_digest_error_attention": bool(
                1 if row["show_digest_error_attention"] is None else row["show_digest_error_attention"]
            ),
            "digest_include_attention": bool(1 if row["digest_include_attention"] is None else row["digest_include_attention"]),
            "target_titles": str(row["target_titles"] or ""),
            "target_role_families": str(row["target_role_families"] or ""),
            "preferred_location_types": str(row["preferred_location_types"] or ""),
            "salary_target_note": str(row["salary_target_note"] or ""),
            "keywords_note": str(row["keywords_note"] or ""),
        }
    finally:
        conn.close()


def bootstrap_local_user(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    email: str,
    password: str,
    user_id: str | None = None,
) -> dict[str, Any]:
    # Idempotent local bootstrap for dev/demo.
    return create_local_user(db_path=db_path, email=email, password=password, user_id=user_id, is_active=True)


def get_user_settings(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    user_id: str,
) -> dict[str, Any]:
    uid = user_id.strip()
    if not uid:
        raise ValueError("user_id is required")
    conn = _connect(db_path)
    try:
        ensure_auth_schema(db_path=db_path)
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (uid,)).fetchone()
        if row is None:
            raise ValueError(f"user not found: {uid}")
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "default_alert_email": row["default_alert_email"],
            "include_dismissed_default": bool(row["include_dismissed_default"]),
            "show_saved_search_quality_attention": bool(
                1 if row["show_saved_search_quality_attention"] is None else row["show_saved_search_quality_attention"]
            ),
            "show_due_saved_search_attention": bool(
                1 if row["show_due_saved_search_attention"] is None else row["show_due_saved_search_attention"]
            ),
            "show_follow_up_attention": bool(1 if row["show_follow_up_attention"] is None else row["show_follow_up_attention"]),
            "show_digest_error_attention": bool(
                1 if row["show_digest_error_attention"] is None else row["show_digest_error_attention"]
            ),
            "digest_include_attention": bool(1 if row["digest_include_attention"] is None else row["digest_include_attention"]),
            "target_titles": str(row["target_titles"] or ""),
            "target_role_families": str(row["target_role_families"] or ""),
            "preferred_location_types": str(row["preferred_location_types"] or ""),
            "salary_target_note": str(row["salary_target_note"] or ""),
            "keywords_note": str(row["keywords_note"] or ""),
            "created_at": row["created_at"],
            "is_active": bool(row["is_active"]),
        }
    finally:
        conn.close()


def update_user_settings(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    user_id: str,
    email: str,
    default_alert_email: str | None = None,
    include_dismissed_default: bool = True,
    show_saved_search_quality_attention: bool = True,
    show_due_saved_search_attention: bool = True,
    show_follow_up_attention: bool = True,
    show_digest_error_attention: bool = True,
    digest_include_attention: bool = True,
    target_titles: str = "",
    target_role_families: str = "",
    preferred_location_types: str = "",
    salary_target_note: str = "",
    keywords_note: str = "",
) -> dict[str, Any]:
    uid = user_id.strip()
    em = email.strip().lower()
    if not uid:
        raise ValueError("user_id is required")
    if not em:
        raise ValueError("email is required")
    alert_email = (default_alert_email or "").strip().lower() or None
    conn = _connect(db_path)
    try:
        ensure_auth_schema(db_path=db_path)
        row = conn.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)).fetchone()
        if row is None:
            raise ValueError(f"user not found: {uid}")
        conflict = conn.execute("SELECT user_id FROM users WHERE email = ? AND user_id <> ?", (em, uid)).fetchone()
        if conflict is not None:
            raise ValueError(f"email already used by another user: {em}")
        conn.execute(
            """
            UPDATE users
            SET email = ?,
                default_alert_email = ?,
                include_dismissed_default = ?,
                show_saved_search_quality_attention = ?,
                show_due_saved_search_attention = ?,
                show_follow_up_attention = ?,
                show_digest_error_attention = ?,
                digest_include_attention = ?,
                target_titles = ?,
                target_role_families = ?,
                preferred_location_types = ?,
                salary_target_note = ?,
                keywords_note = ?
            WHERE user_id = ?
            """,
            (
                em,
                alert_email,
                1 if include_dismissed_default else 0,
                1 if show_saved_search_quality_attention else 0,
                1 if show_due_saved_search_attention else 0,
                1 if show_follow_up_attention else 0,
                1 if show_digest_error_attention else 0,
                1 if digest_include_attention else 0,
                target_titles.strip(),
                target_role_families.strip(),
                preferred_location_types.strip().lower(),
                salary_target_note.strip(),
                keywords_note.strip(),
                uid,
            ),
        )
        conn.commit()
        return get_user_settings(db_path=db_path, user_id=uid)
    finally:
        conn.close()


def change_local_password(
    *,
    db_path: str | Path = DEFAULT_AUTH_DB_PATH,
    user_id: str,
    current_password: str,
    new_password: str,
) -> dict[str, Any]:
    uid = user_id.strip()
    if not uid:
        raise ValueError("user_id is required")
    if not current_password:
        raise ValueError("current password is required")
    _validate_new_password(new_password)
    conn = _connect(db_path)
    try:
        ensure_auth_schema(db_path=db_path)
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (uid,)).fetchone()
        if row is None:
            raise ValueError(f"user not found: {uid}")
        if not bool(row["is_active"]):
            raise ValueError("user is inactive")
        encoded = str(row["password_hash"] or "")
        if not encoded or not _verify_password(current_password, encoded):
            raise ValueError("current password is incorrect")
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE user_id = ?",
            (_hash_password(new_password), uid),
        )
        conn.commit()
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "password_changed": True,
        }
    finally:
        conn.close()

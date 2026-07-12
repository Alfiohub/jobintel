from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

from fastapi import HTTPException, Request


DEFAULT_DATASET_PATH = "data/jobs/jobs_indexed_en.jsonl"
DEFAULT_SAVED_DB_PATH = "data/jobs/saved_searches.db"
DEFAULT_ALERT_RUNS_DIR = "data/alerts/runs"
DEFAULT_JOB_STATE_DB_PATH = "data/jobs/job_state.db"
DATASET_PATH_ENV = "JOBINTEL_INDEXED_INPUT"
SQLITE_PATH_ENV = "JOBINTEL_SQLITE_PATH"
SAVED_DB_PATH_ENV = "JOBINTEL_SAVED_DB_PATH"
ALERT_RUNS_DIR_ENV = "JOBINTEL_ALERT_RUNS_DIR"
JOB_STATE_DB_PATH_ENV = "JOBINTEL_JOB_STATE_DB_PATH"
DEFAULT_USER_ID_ENV = "JOBINTEL_DEFAULT_USER_ID"
DEFAULT_USER_EMAIL_ENV = "JOBINTEL_DEFAULT_USER_EMAIL"
SESSION_SECRET_ENV = "JOBINTEL_SESSION_SECRET"
SESSION_SECRET_REQUIRED_ENV = "JOBINTEL_REQUIRE_SESSION_SECRET"
SESSION_MAX_AGE_ENV = "JOBINTEL_SESSION_MAX_AGE"
SESSION_COOKIE_NAME_ENV = "JOBINTEL_SESSION_COOKIE_NAME"
SESSION_HTTPS_ONLY_ENV = "JOBINTEL_SESSION_HTTPS_ONLY"
SESSION_SAME_SITE_ENV = "JOBINTEL_SESSION_SAME_SITE"
BOOTSTRAP_EMAIL_ENV = "JOBINTEL_BOOTSTRAP_EMAIL"
BOOTSTRAP_PASSWORD_ENV = "JOBINTEL_BOOTSTRAP_PASSWORD"


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    email: str


@dataclass(frozen=True)
class SessionConfig:
    secret_key: str
    max_age: int
    session_cookie: str
    same_site: str
    https_only: bool


def resolve_dataset_path(override: str | Path | None = None) -> str:
    if override is not None:
        return str(override)
    return os.getenv(DATASET_PATH_ENV, DEFAULT_DATASET_PATH)


def resolve_sqlite_path(override: str | Path | None = None) -> str | None:
    if override is not None:
        return str(override)
    env_val = os.getenv(SQLITE_PATH_ENV)
    return env_val if env_val else None


def resolve_saved_db_path(override: str | Path | None = None) -> str:
    if override is not None:
        return str(override)
    return os.getenv(SAVED_DB_PATH_ENV, DEFAULT_SAVED_DB_PATH)


def resolve_alert_runs_dir(override: str | Path | None = None) -> str:
    if override is not None:
        return str(override)
    return os.getenv(ALERT_RUNS_DIR_ENV, DEFAULT_ALERT_RUNS_DIR)


def resolve_job_state_db_path(override: str | Path | None = None) -> str:
    if override is not None:
        return str(override)
    return os.getenv(JOB_STATE_DB_PATH_ENV, DEFAULT_JOB_STATE_DB_PATH)


def resolve_default_user(
    *,
    user_id_override: str | None = None,
    email_override: str | None = None,
) -> CurrentUser:
    user_id = (user_id_override or os.getenv(DEFAULT_USER_ID_ENV, "local-user")).strip() or "local-user"
    email = (email_override or os.getenv(DEFAULT_USER_EMAIL_ENV, f"{user_id}@local")).strip() or f"{user_id}@local"
    return CurrentUser(user_id=user_id, email=email)


def resolve_session_secret(override: str | None = None) -> str:
    default_secret = "jobintel-dev-session-secret-change-me"
    secret = (override or os.getenv(SESSION_SECRET_ENV, default_secret)).strip() or default_secret
    require_secret = _trueish(os.getenv(SESSION_SECRET_REQUIRED_ENV, "false"))
    if require_secret and secret == default_secret:
        raise RuntimeError(
            f"{SESSION_SECRET_ENV} must be set to a non-default value when "
            f"{SESSION_SECRET_REQUIRED_ENV}=true"
        )
    return secret


def _trueish(v: str | None) -> bool:
    return (v or "").strip().lower() in {"1", "true", "yes", "on"}


def resolve_session_config(*, secret_override: str | None = None) -> SessionConfig:
    secret_key = resolve_session_secret(secret_override)
    try:
        max_age = int((os.getenv(SESSION_MAX_AGE_ENV, "43200")).strip())  # 12h default
    except ValueError:
        max_age = 43200
    if max_age <= 0:
        max_age = 43200
    session_cookie = (os.getenv(SESSION_COOKIE_NAME_ENV, "jobintel_session").strip() or "jobintel_session")
    same_site = (os.getenv(SESSION_SAME_SITE_ENV, "lax").strip().lower() or "lax")
    if same_site not in {"lax", "strict", "none"}:
        same_site = "lax"
    https_only = _trueish(os.getenv(SESSION_HTTPS_ONLY_ENV, "false"))
    return SessionConfig(
        secret_key=secret_key,
        max_age=max_age,
        session_cookie=session_cookie,
        same_site=same_site,
        https_only=https_only,
    )


def resolve_bootstrap_login(
    *,
    email_override: str | None = None,
    password_override: str | None = None,
) -> tuple[str, str]:
    email = (email_override or os.getenv(BOOTSTRAP_EMAIL_ENV, "admin@example.com")).strip() or "admin@example.com"
    password = (password_override or os.getenv(BOOTSTRAP_PASSWORD_ENV, "admin123")).strip() or "admin123"
    return email, password


def ensure_dataset_exists(path: str | Path) -> None:
    p = Path(path)
    if not p.exists():
        raise RuntimeError(
            f"indexed dataset not found: {p}. Set {DATASET_PATH_ENV} or pass create_app(input_path=...)."
        )
    if not p.is_file():
        raise RuntimeError(f"indexed dataset path is not a file: {p}")


def ensure_sqlite_exists(path: str | Path | None) -> None:
    if path is None:
        return
    p = Path(path)
    if not p.exists():
        raise RuntimeError(
            f"sqlite storage not found: {p}. Set {SQLITE_PATH_ENV} or pass create_app(sqlite_path=...)."
        )
    if not p.is_file():
        raise RuntimeError(f"sqlite path is not a file: {p}")


def get_dataset_path(request: Request) -> str:
    path = getattr(request.app.state, "indexed_input_path", None)
    if not isinstance(path, str) or not path:
        raise HTTPException(status_code=500, detail="dataset path not configured")
    return path


def get_sqlite_path(request: Request) -> str | None:
    path = getattr(request.app.state, "sqlite_path", None)
    if path is None:
        return None
    if not isinstance(path, str):
        raise HTTPException(status_code=500, detail="sqlite path not configured")
    return path


def get_saved_db_path(request: Request) -> str:
    path = getattr(request.app.state, "saved_db_path", None)
    if not isinstance(path, str) or not path:
        raise HTTPException(status_code=500, detail="saved db path not configured")
    return path


def get_alert_runs_dir(request: Request) -> str:
    path = getattr(request.app.state, "alert_runs_dir", None)
    if not isinstance(path, str) or not path:
        raise HTTPException(status_code=500, detail="alert runs dir not configured")
    return path


def get_job_state_db_path(request: Request) -> str:
    path = getattr(request.app.state, "job_state_db_path", None)
    if not isinstance(path, str) or not path:
        raise HTTPException(status_code=500, detail="job state db path not configured")
    return path


def get_current_user(request: Request) -> CurrentUser:
    default_user = getattr(request.app.state, "default_user", None)
    if not isinstance(default_user, CurrentUser):
        raise HTTPException(status_code=500, detail="default user not configured")
    session = request.scope.get("session")
    if isinstance(session, dict):
        session_uid = str(session.get("user_id") or "").strip()
        session_email = str(session.get("user_email") or "").strip()
        if session_uid:
            return CurrentUser(user_id=session_uid, email=session_email or f"{session_uid}@local")
    header_user_id = (request.headers.get("X-JobIntel-User-Id") or "").strip()
    header_email = (request.headers.get("X-JobIntel-User-Email") or "").strip()
    if not header_user_id:
        return default_user
    email = header_email or f"{header_user_id}@local"
    return CurrentUser(user_id=header_user_id, email=email)

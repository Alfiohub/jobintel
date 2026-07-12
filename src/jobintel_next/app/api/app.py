from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from jobintel_next.product.auth import bootstrap_local_user, ensure_auth_schema
from ..admin_ui import router as admin_ui_router
from .dependencies import (
    ensure_dataset_exists,
    ensure_sqlite_exists,
    resolve_alert_runs_dir,
    resolve_dataset_path,
    resolve_default_user,
    resolve_job_state_db_path,
    resolve_session_config,
    resolve_bootstrap_login,
    resolve_saved_db_path,
    resolve_sqlite_path,
)
from .router import router


def create_app(
    *,
    input_path: str | Path | None = None,
    sqlite_path: str | Path | None = None,
    saved_db_path: str | Path | None = None,
    alert_runs_dir: str | Path | None = None,
    job_state_db_path: str | Path | None = None,
    default_user_id: str | None = None,
    default_user_email: str | None = None,
    session_secret: str | None = None,
    bootstrap_email: str | None = None,
    bootstrap_password: str | None = None,
) -> FastAPI:
    indexed_input = resolve_dataset_path(input_path)
    sqlite_storage = resolve_sqlite_path(sqlite_path)
    saved_db = resolve_saved_db_path(saved_db_path)
    runs_dir = resolve_alert_runs_dir(alert_runs_dir)
    job_state_db = resolve_job_state_db_path(job_state_db_path)
    default_user = resolve_default_user(user_id_override=default_user_id, email_override=default_user_email)
    session_cfg = resolve_session_config(secret_override=session_secret)
    resolved_bootstrap_email, resolved_bootstrap_password = resolve_bootstrap_login(
        email_override=bootstrap_email,
        password_override=bootstrap_password,
    )
    # Ensure login works even when startup lifespan isn't entered (e.g. some tests).
    ensure_auth_schema(db_path=saved_db)
    bootstrap_local_user(
        db_path=saved_db,
        email=resolved_bootstrap_email,
        password=resolved_bootstrap_password,
        user_id=default_user.user_id,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        ensure_dataset_exists(indexed_input)
        ensure_sqlite_exists(sqlite_storage)
        ensure_auth_schema(db_path=saved_db)
        bootstrap_local_user(
            db_path=saved_db,
            email=resolved_bootstrap_email,
            password=resolved_bootstrap_password,
            user_id=default_user.user_id,
        )
        app.state.indexed_input_path = indexed_input
        app.state.sqlite_path = sqlite_storage
        app.state.saved_db_path = saved_db
        app.state.alert_runs_dir = runs_dir
        app.state.job_state_db_path = job_state_db
        app.state.default_user = default_user
        yield

    app = FastAPI(
        title="jobintel-next API",
        version="0.1.0",
        description="HTTP API v1 on top of local serving layer and query packs.",
        lifespan=lifespan,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_cfg.secret_key,
        max_age=session_cfg.max_age,
        session_cookie=session_cfg.session_cookie,
        same_site=session_cfg.same_site,
        https_only=session_cfg.https_only,
    )

    @app.middleware("http")
    async def protect_admin_routes(request, call_next):
        path = request.url.path
        if path.startswith("/admin"):
            # This middleware may execute before SessionMiddleware decodes the session
            # in some stacks; cookie presence is enough for redirect gate.
            cookie_name = str(getattr(request.app.state, "session_cookie_name", session_cfg.session_cookie))
            if not str(request.cookies.get(cookie_name) or "").strip():
                next_path = path + (f"?{request.url.query}" if request.url.query else "")
                return RedirectResponse(url=f"/login?next={quote(next_path, safe='')}", status_code=303)
        return await call_next(request)

    app.state.indexed_input_path = indexed_input
    app.state.sqlite_path = sqlite_storage
    app.state.saved_db_path = saved_db
    app.state.alert_runs_dir = runs_dir
    app.state.job_state_db_path = job_state_db
    app.state.default_user = default_user
    app.state.session_cookie_name = session_cfg.session_cookie
    app.state.bootstrap_user_email = resolved_bootstrap_email
    app.include_router(router)
    app.include_router(admin_ui_router)
    return app


app = create_app()

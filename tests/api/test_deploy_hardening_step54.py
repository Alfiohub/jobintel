from __future__ import annotations

from pathlib import Path

import pytest

from jobintel_next.app.api.dependencies import resolve_session_secret
from jobintel_next.app.api import create_app


def _write_jsonl(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"url":"https://e/1","title_raw":"SE"}\n', encoding='utf-8')


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def test_session_secret_required_raises_on_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JOBINTEL_SESSION_SECRET", raising=False)
    monkeypatch.setenv("JOBINTEL_REQUIRE_SESSION_SECRET", "true")
    with pytest.raises(RuntimeError):
        resolve_session_secret()


def test_session_secret_required_accepts_custom_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JOBINTEL_REQUIRE_SESSION_SECRET", "true")
    monkeypatch.setenv("JOBINTEL_SESSION_SECRET", "super-secret-value")
    assert resolve_session_secret() == "super-secret-value"


def test_create_app_with_prod_like_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    indexed = tmp_path / "demo" / "jobs_indexed_demo.jsonl"
    sqlite = tmp_path / "demo" / "jobs_indexed_demo.db"
    saved = tmp_path / "jobs" / "saved_searches.db"
    runs = tmp_path / "alerts" / "runs"
    _write_jsonl(indexed)
    _touch(sqlite)

    monkeypatch.setenv("JOBINTEL_REQUIRE_SESSION_SECRET", "true")
    monkeypatch.setenv("JOBINTEL_SESSION_SECRET", "another-super-secret")

    app = create_app(
        input_path=indexed,
        sqlite_path=sqlite,
        saved_db_path=saved,
        alert_runs_dir=runs,
    )
    assert app.state.indexed_input_path == str(indexed)
    assert app.state.sqlite_path == str(sqlite)
    assert app.state.saved_db_path == str(saved)
    assert app.state.alert_runs_dir == str(runs)

from __future__ import annotations

import json
from pathlib import Path
import time

from fastapi.testclient import TestClient

from jobintel_next.app.api import create_app
from jobintel_next.product.saved_searches import create_saved_search


def _write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _rows() -> list[dict]:
    return [
        {
            "url": "https://e/1",
            "title_raw": "Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "language_bucket": "en",
            "published_at": "2026-03-10T00:00:00+00:00",
        }
    ]


def test_per_user_alert_runs_isolated_history_and_detail(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())

    create_saved_search(
        db_path=saved_db,
        name="u1-search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        user_id="user-1",
        user_email="user1@example.com",
    )
    create_saved_search(
        db_path=saved_db,
        name="u2-search",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
        user_id="user-2",
        user_email="user2@example.com",
    )

    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db, alert_runs_dir=runs_dir))

    h1 = {"X-JobIntel-User-Id": "user-1", "X-JobIntel-User-Email": "user1@example.com"}
    h2 = {"X-JobIntel-User-Id": "user-2", "X-JobIntel-User-Email": "user2@example.com"}

    r1 = client.post("/alerts/run-all", headers=h1)
    time.sleep(1.1)
    r2 = client.post("/alerts/run-all", headers=h2)
    assert r1.status_code == 200
    assert r2.status_code == 200

    p1 = r1.json()
    p2 = r2.json()

    assert p1["run_id"] != p2["run_id"] or p1["json_report_path"] != p2["json_report_path"]
    assert f"/user-1/{p1['run_id']}.json" in p1["json_report_path"]
    assert f"/user-2/{p2['run_id']}.json" in p2["json_report_path"]
    assert Path(p1["json_report_path"]).exists()
    assert Path(p2["json_report_path"]).exists()

    l1 = client.get("/alerts/runs", headers=h1)
    l2 = client.get("/alerts/runs", headers=h2)
    assert l1.status_code == 200
    assert l2.status_code == 200

    runs1 = l1.json()["runs"]
    runs2 = l2.json()["runs"]
    assert len(runs1) == 1
    assert len(runs2) == 1
    assert runs1[0]["run_id"] == p1["run_id"]
    assert runs2[0]["run_id"] == p2["run_id"]

    d1_ok = client.get(f"/alerts/runs/{p1['run_id']}", headers=h1)
    assert d1_ok.status_code == 200
    d1_forbidden = client.get(f"/alerts/runs/{p1['run_id']}", headers=h2)
    assert d1_forbidden.status_code == 404

    s1 = client.get("/alerts/summary", headers=h1)
    s2 = client.get("/alerts/summary", headers=h2)
    assert s1.status_code == 200
    assert s2.status_code == 200
    assert s1.json()["runs_count"] == 1
    assert s2.json()["runs_count"] == 1
    assert s1.json()["latest_run_id"] == p1["run_id"]
    assert s2.json()["latest_run_id"] == p2["run_id"]

from __future__ import annotations

import json
from pathlib import Path

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
            "has_skills": True,
            "skills": ["python"],
        },
        {
            "url": "https://e/2",
            "title_raw": "Account Executive",
            "normalized_title": "account_executive",
            "role_family": "sales",
            "language_bucket": "en",
            "published_at": "2026-03-11T00:00:00+00:00",
        },
    ]


def test_alert_runs_run_all_and_history_endpoints(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())
    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )

    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db, alert_runs_dir=runs_dir))

    r_run = client.post("/alerts/run-all", params={"scan_limit": 1000, "limit": 100, "sample_size": 3})
    assert r_run.status_code == 200
    run_payload = r_run.json()
    run_id = run_payload["run_id"]
    assert run_payload["searches_enabled"] == 1
    assert Path(run_payload["json_report_path"]).exists()

    r_list = client.get("/alerts/runs")
    assert r_list.status_code == 200
    runs = r_list.json()["runs"]
    assert len(runs) >= 1
    assert any(x["run_id"] == run_id for x in runs)

    r_detail = client.get(f"/alerts/runs/{run_id}")
    assert r_detail.status_code == 200
    detail = r_detail.json()
    assert detail["run_id"] == run_id
    assert "results" in detail


def test_alert_run_detail_not_found_404(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"
    _write(indexed, _rows())
    client = TestClient(create_app(input_path=indexed, saved_db_path=saved_db, alert_runs_dir=runs_dir))

    r = client.get("/alerts/runs/not_a_real_run")
    assert r.status_code == 404
    assert "alert run not found" in r.json()["detail"]


def test_alert_runs_second_run_has_no_new_matches_if_dataset_unchanged(tmp_path: Path) -> None:
    indexed = tmp_path / "idx.jsonl"
    saved_db = tmp_path / "saved.db"
    runs_dir = tmp_path / "alerts" / "runs"

    _write(indexed, _rows())

    create_saved_search(
        db_path=saved_db,
        name="software eng",
        query_type="filters",
        filters_json='{"normalized_title":"software_engineer"}',
    )

    client = TestClient(
        create_app(
            input_path=indexed,
            saved_db_path=saved_db,
            alert_runs_dir=runs_dir,
        )
    )

    # First run: initial match should be considered new.
    r1 = client.post("/alerts/run-all", params={"scan_limit": 1000, "limit": 100, "sample_size": 3})
    assert r1.status_code == 200
    p1 = r1.json()
    assert p1["processed_ok"] == 1
    assert p1["processed_error"] == 0

    d1 = client.get(f"/alerts/runs/{p1['run_id']}")
    assert d1.status_code == 200
    detail1 = d1.json()
    assert len(detail1["results"]) == 1
    assert detail1["results"][0]["name"] == "software eng"
    assert detail1["results"][0]["new_matches_count"] >= 1

    # Second run on unchanged dataset: no new matches expected.
    r2 = client.post("/alerts/run-all", params={"scan_limit": 1000, "limit": 100, "sample_size": 3})
    assert r2.status_code == 200
    p2 = r2.json()
    assert p2["processed_ok"] == 1
    assert p2["processed_error"] == 0

    d2 = client.get(f"/alerts/runs/{p2['run_id']}")
    assert d2.status_code == 200
    detail2 = d2.json()
    assert len(detail2["results"]) == 1
    assert detail2["results"][0]["name"] == "software eng"
    assert detail2["results"][0]["new_matches_count"] == 0

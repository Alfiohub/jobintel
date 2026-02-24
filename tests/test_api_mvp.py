from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from jobintel.api import app


def _seed_db(db_path: Path) -> None:
    con = sqlite3.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE seen_jobs (
          fingerprint TEXT PRIMARY KEY,
          company TEXT,
          title TEXT,
          url TEXT,
          source TEXT,
          score INTEGER,
          first_seen TEXT,
          location TEXT,
          remote INTEGER,
          published_at TEXT
        )
        """
    )
    con.execute(
        """
        CREATE TABLE jobs_enriched (
          fingerprint TEXT PRIMARY KEY,
          role_family TEXT,
          seniority TEXT,
          location_type TEXT,
          country TEXT,
          skills_json TEXT NOT NULL,
          normalized_title TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """
    )
    con.execute(
        """
        INSERT INTO seen_jobs(fingerprint, company, title, url, source, score, first_seen, location, remote, published_at)
        VALUES ('fp1', 'acme', 'Data Engineer', 'https://example.com/1', 'greenhouse', 0, '2026-02-17T00:00:00', 'Remote US', 1, '2026-02-17T00:00:00')
        """
    )
    con.execute(
        """
        INSERT INTO jobs_enriched(fingerprint, role_family, seniority, location_type, country, skills_json, normalized_title, updated_at)
        VALUES ('fp1', 'data', 'senior', 'remote', 'US', '["data","python"]', 'data engineer', '2026-02-17T00:00:00')
        """
    )
    con.commit()
    con.close()


def test_saved_filters_and_recommendations(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite"
    _seed_db(db_path)
    client = TestClient(app)

    r = client.post(
        "/saved-filters",
        params={"db_path": str(db_path)},
        json={
            "user_id": "demo",
            "name": "Data Remote US",
            "criteria": {"role_family": ["data"], "location_type": ["remote"], "country": ["us"]},
            "is_active": True,
        },
    )
    assert r.status_code == 200
    fid = r.json()["id"]

    rec = client.get(f"/recommendations/{fid}", params={"db_path": str(db_path), "max_scan": 1000, "limit": 5})
    assert rec.status_code == 200
    data = rec.json()
    assert len(data) == 1
    assert data[0]["company"] == "acme"


def test_actions_endpoint(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite"
    _seed_db(db_path)
    client = TestClient(app)

    resp = client.post(
        "/jobs/fp1/actions",
        params={"db_path": str(db_path)},
        json={"user_id": "demo", "action": "save", "metadata": {"source": "test"}},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "created"

    hist = client.get("/jobs/fp1/actions", params={"db_path": str(db_path), "user_id": "demo"})
    assert hist.status_code == 200
    assert len(hist.json()) == 1
    assert hist.json()[0]["action"] == "save"


def test_notification_target_crud(tmp_path: Path) -> None:
    db_path = tmp_path / "test.sqlite"
    _seed_db(db_path)
    client = TestClient(app)

    create = client.post(
        "/saved-filters",
        params={"db_path": str(db_path)},
        json={"user_id": "demo", "name": "Any", "criteria": {}, "is_active": True},
    )
    fid = create.json()["id"]

    upsert = client.post(
        f"/notifications/targets/{fid}",
        params={"db_path": str(db_path)},
        json={"webhook_url": "https://example.invalid/hook", "is_active": True},
    )
    assert upsert.status_code == 200

    listed = client.get(f"/notifications/targets/{fid}", params={"db_path": str(db_path)})
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(
        f"/notifications/targets/{fid}",
        params={"db_path": str(db_path), "webhook_url": "https://example.invalid/hook"},
    )
    assert deleted.status_code == 200

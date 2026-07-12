from __future__ import annotations

from jobintel.collectors.greenhouse import GreenhouseBoard, GreenhouseCollector


def test_greenhouse_map_extracts_html_content_and_language() -> None:
    collector = GreenhouseCollector([GreenhouseBoard(token="acme", company_name="Acme")])
    payload = {
        "id": 123,
        "title": "Data Engineer",
        "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/123",
        "location": {"name": "Remote"},
        "updated_at": "2026-02-20T10:00:00-05:00",
        "language": "en",
        "content": "<div><p>The role requires Python and SQL.</p><ul><li>Remote friendly</li></ul></div>",
    }

    post = collector._map(GreenhouseBoard(token="acme", company_name="Acme"), payload)

    assert post is not None
    assert post.description_text == "The role requires Python and SQL. Remote friendly"
    assert post.language == "en"
    assert post.workplace_type == "remote"


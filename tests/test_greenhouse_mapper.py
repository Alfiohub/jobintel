from jobintel_next.adapters.greenhouse.mapper import map_greenhouse_job_to_canonical


def test_map_greenhouse_job_to_canonical() -> None:
    payload = {
        "id": 123,
        "title": "Data Engineer",
        "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/123",
        "company_name": "ACME Corp",
        "first_published": "2026-01-22T10:31:21-05:00",
        "updated_at": "2026-03-25T01:00:22-04:00",
        "language": "en",
        "location": {"name": "Remote"},
        "content": "<p>hello</p>",
        "departments": [{"id": 1, "name": "Engineering"}],
        "offices": [{"id": 2, "location": "Remote"}],
    }

    out = map_greenhouse_job_to_canonical(board="acme", payload=payload)

    assert out is not None
    assert out.source == "greenhouse"
    assert out.source_org == "acme"
    assert out.external_id == "123"
    assert out.title == "Data Engineer"
    assert out.url == "https://job-boards.greenhouse.io/acme/jobs/123"
    assert out.company_name == "ACME Corp"
    assert out.location_raw == "Remote"
    assert out.published_at is not None
    assert out.updated_at is not None
    assert out.published_at != out.updated_at
    assert out.language_hint == "en"
    assert out.description_raw == "<p>hello</p>"
    assert out.departments_raw == [{"id": 1, "name": "Engineering"}]
    assert out.offices_raw == [{"id": 2, "location": "Remote"}]
    assert out.raw_payload["id"] == 123

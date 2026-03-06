from __future__ import annotations

from automation.legacy_ner.weak_label_greenhouse_phase2 import build_output_row, generate_entities, keep_row, row_description


def test_generate_entities_extracts_priority_labels() -> None:
    row = {
        "id": "raw-1",
        "source": "greenhouse",
        "url": "https://example.com/jobs/1",
        "company_name": "acme",
        "title": "Senior Data Engineer",
        "description_text": (
            "This is a full-time remote role. You will build ETL pipelines with Python, SQL, "
            "Airflow, dbt, and AWS. Salary range: $120,000 - $150,000 per year."
        ),
        "location_raw": "New York, NY",
        "language": "en",
    }

    entities = generate_entities(row, max_skills=8)
    labels = {entity["label"] for entity in entities}

    assert "ROLE" in labels
    assert "SENIORITY" in labels
    assert "SKILL" in labels
    assert "WORKPLACE_TYPE" in labels
    assert "EMPLOYMENT_TYPE" in labels
    assert "SALARY" in labels
    assert "LOCATION" in labels


def test_keep_row_requires_multiple_priority_labels() -> None:
    row = {
        "description_text": "Remote role with Python and SQL " * 20,
    }
    entities = [
        {"label": "LOCATION", "source_field": "location_raw", "start": 0, "end": 10},
        {"label": "ROLE", "source_field": "title", "start": 0, "end": 12},
        {"label": "SKILL", "source_field": "description_text", "start": 17, "end": 23},
    ]

    assert keep_row(row, entities, min_entities=3, min_priority_labels=2, min_description_chars=50) is True
    assert keep_row(row, entities[:2], min_entities=2, min_priority_labels=2, min_description_chars=50) is False


def test_build_output_row_reuses_existing_id() -> None:
    row = {
        "id": "raw-1",
        "source": "greenhouse",
        "url": "https://example.com/jobs/1",
        "company_name": "acme",
        "title": "Data Engineer",
        "description_text": "Python SQL" * 40,
        "location_raw": "Berlin",
        "language": "en",
    }

    out = build_output_row(row, [], {"https://example.com/jobs/1": "existing-123"})

    assert out["id"] == "existing-123"
    assert out["annotation_status"] == "preannotated"
    assert out["language"] == "en"


def test_row_description_falls_back_to_raw_payload_html() -> None:
    row = {
        "description_text": None,
        "raw_payload": {
            "content": "<div><p>Python and SQL</p><p>Remote role</p></div>",
        },
    }

    assert row_description(row) == "Python and SQL Remote role"

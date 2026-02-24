from __future__ import annotations

import pytest

from jobintel.canonical import CanonicalJob, validate_canonical


def test_canonical_required_fields() -> None:
    job = CanonicalJob.from_source(
        source="greenhouse",
        url="https://example.com/job/1",
        title="Data Engineer",
        company_name="Acme",
    )
    validate_canonical(job)
    assert job.id
    assert job.company_name == "Acme"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source": "", "url": "https://example.com/1", "title": "x", "company_name": "y"},
        {"source": "gh", "url": "", "title": "x", "company_name": "y"},
        {"source": "gh", "url": "https://example.com/1", "title": "", "company_name": "y"},
        {"source": "gh", "url": "https://example.com/1", "title": "x", "company_name": ""},
    ],
)
def test_canonical_missing_required_raises(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        CanonicalJob.from_source(**kwargs)

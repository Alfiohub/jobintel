from __future__ import annotations

import json

from jobintel_next.domain.models import (
    CanonicalRawJob,
    CleanedJob,
    ExtractedAttributes,
    IndexedJob,
    LanguageDecision,
    SourceRawJob,
    TitleClassification,
    model_from_dict,
    model_to_jsonl_line,
)


def test_construct_models_minimal() -> None:
    raw = SourceRawJob(source="greenhouse", source_org="found", fetched_at="2026-03-27T12:00:00Z", payload={"id": 1})
    canon = CanonicalRawJob(
        source="greenhouse",
        source_org="found",
        url="https://job-boards.greenhouse.io/found/jobs/1",
        title="Data Engineer",
        company_name="found",
        raw_payload={"id": 1},
    )
    lang = LanguageDecision(url=canon.url, bucket="en", reason="hint_en")
    clean = CleanedJob(url=canon.url, title_clean="Data Engineer", description_clean="desc", location_clean="Remote")
    ext = ExtractedAttributes(url=canon.url, skills=["python"])
    tc = TitleClassification(
        url=canon.url,
        normalized_title="data_engineer",
        role_family="data_engineering",
        classification_status="matched",
        match_method="rule_pattern",
        confidence=0.85,
    )
    idx = IndexedJob(
        source=canon.source,
        source_org=canon.source_org,
        url=canon.url,
        company_name=canon.company_name,
        title_raw=canon.title,
        title_clean=clean.title_clean,
        normalized_title=tc.normalized_title,
        role_family=tc.role_family,
        classification_status=tc.classification_status,
        match_method=tc.match_method,
        confidence=tc.confidence,
        skills=ext.skills,
    )

    assert raw.source == "greenhouse"
    assert canon.url.startswith("https://")
    assert lang.bucket == "en"
    assert clean.title_clean == "Data Engineer"
    assert ext.skills == ["python"]
    assert tc.normalized_title == "data_engineer"
    assert idx.role_family == "data_engineering"


def test_serialization_helpers() -> None:
    canon = CanonicalRawJob(
        source="greenhouse",
        source_org="found",
        url="https://job-boards.greenhouse.io/found/jobs/2",
        title="Analyst",
        company_name="found",
        raw_payload={"id": 2},
        external_id="2",
    )
    line = model_to_jsonl_line(canon)
    payload = json.loads(line)
    assert payload["source"] == "greenhouse"
    assert payload["external_id"] == "2"

    rebuilt = model_from_dict(CanonicalRawJob, payload)
    assert rebuilt.url == canon.url
    assert rebuilt.title == canon.title


def test_key_fields_present_in_indexed_job_dict() -> None:
    idx = IndexedJob(
        source="greenhouse",
        source_org="found",
        url="https://job-boards.greenhouse.io/found/jobs/3",
        company_name="found",
        title_raw="Data Engineer",
        title_clean="Data Engineer",
        normalized_title="data_engineer",
        role_family="data_engineering",
        classification_status="matched",
        match_method="rule_pattern",
        confidence=0.9,
    )
    d = idx.to_dict()
    for key in [
        "source",
        "url",
        "title_raw",
        "normalized_title",
        "role_family",
        "classification_status",
        "has_salary",
        "has_skills",
        "has_location",
        "title_is_other",
    ]:
        assert key in d

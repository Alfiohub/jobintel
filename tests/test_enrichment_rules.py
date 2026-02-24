from __future__ import annotations

from jobintel.canonical import CanonicalJob
from jobintel.enrichment import EnrichmentRules


def test_enrichment_infers_fields_and_quality() -> None:
    post = CanonicalJob.from_source(
        source="smartrecruiters",
        url="https://example.com/job/2",
        title="Senior Data Engineer",
        company_name="Contoso",
        description_text="Remote role. Python, SQL, Airflow. Full-time.",
        location_raw="Remote, Italy",
    )
    enricher = EnrichmentRules(enabled=True, min_quality_score=0.0)
    enriched = enricher.enrich_one(post)

    assert enriched.workplace_type == "remote"
    assert enriched.seniority == "senior"
    assert enriched.employment_type == "full_time"
    assert enriched.function_family == "data"
    assert "python" in enriched.tags
    assert (enriched.quality_score or 0) > 0


def test_enrichment_quality_gate_filters_low_quality() -> None:
    low = CanonicalJob.from_source(
        source="lever",
        url="https://example.com/job/low",
        title="X",
        company_name="Y",
        description_text="",
    )
    high = CanonicalJob.from_source(
        source="lever",
        url="https://example.com/job/high",
        title="Senior Software Engineer",
        company_name="Y",
        description_text="Remote full-time role with Python and SQL. " * 4,
        location_raw="Remote",
    )

    enricher = EnrichmentRules(enabled=True, min_quality_score=0.4)
    out, stats = enricher.enrich_many([low, high])

    assert len(out) == 1
    assert out[0].url.endswith("/high")
    assert stats.input_count == 2
    assert stats.output_count == 1
    assert stats.low_quality_dropped == 1

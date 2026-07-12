from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.domain.models import CanonicalRawJob
from jobintel_next.pipelines.cleaning import CleaningStage
from jobintel_next.pipelines.cleaning.run import run_cleaning_stage


def test_html_escaped_description_is_cleaned() -> None:
    job = CanonicalRawJob(
        source="greenhouse",
        source_org="acme",
        url="https://example.com/1",
        title="Data Engineer",
        company_name="Acme",
        raw_payload={},
        description_raw="&lt;p&gt;We build data pipelines &amp; analytics.&lt;/p&gt;",
    )
    cleaned = CleaningStage().run_one(job)
    assert cleaned.description_clean == "We build data pipelines & analytics."


def test_title_whitespace_and_separator_normalization() -> None:
    job = CanonicalRawJob(
        source="greenhouse",
        source_org="acme",
        url="https://example.com/2",
        title="  Senior   Backend Engineer  / Remote ",
        company_name="Acme",
        raw_payload={},
    )
    cleaned = CleaningStage().run_one(job)
    assert cleaned.title_clean == "Senior Backend Engineer - Remote"


def test_section_extraction_requirements_and_responsibilities() -> None:
    job = CanonicalRawJob(
        source="greenhouse",
        source_org="acme",
        url="https://example.com/3",
        title="Product Manager",
        company_name="Acme",
        raw_payload={},
        description_raw=(
            "<h2>What you'll do</h2><ul><li>Own roadmap</li><li>Lead delivery</li></ul>"
            "<h2>Requirements</h2><ul><li>5+ years experience</li><li>Strong communication</li></ul>"
        ),
    )
    cleaned = CleaningStage().run_one(job)
    assert "Own roadmap" in cleaned.responsibilities_clean
    assert "5+ years experience" in cleaned.requirements_clean


def test_content_hash_is_stable() -> None:
    job = CanonicalRawJob(
        source="greenhouse",
        source_org="acme",
        url="https://example.com/4",
        title="Software Engineer",
        company_name="Acme",
        raw_payload={},
        description_raw="<p>You will build APIs.</p>",
        location_raw=" Remote ",
    )
    stage = CleaningStage()
    a = stage.run_one(job)
    b = stage.run_one(job)
    assert a.content_hash == b.content_hash


def test_run_cleaning_stage_outputs_report_and_file(tmp_path: Path) -> None:
    in_path = tmp_path / "jobs_en.jsonl"
    rows = [
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/5",
            "title": " Engineer / Data ",
            "company_name": "Acme",
            "description_raw": "<p>Build platform.</p>",
            "language_bucket": "en",
            "raw_payload": {"id": 5},
        }
    ]
    with in_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    out_path = tmp_path / "jobs_cleaned_en.jsonl"
    report_dir = tmp_path / "docs"
    report = run_cleaning_stage(input_path=in_path, output_path=out_path, report_dir=report_dir)
    assert report["rows_total"] == 1
    assert out_path.exists()
    assert (report_dir / "cleaning_stage_step8.json").exists()
    assert (report_dir / "cleaning_stage_step8.md").exists()


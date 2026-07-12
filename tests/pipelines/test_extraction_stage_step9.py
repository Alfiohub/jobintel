from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.domain.models import CleanedJob
from jobintel_next.pipelines.extraction.run import run_extraction_stage
from jobintel_next.pipelines.extraction.stage import ExtractionStage


def test_seniority_extraction() -> None:
    job = CleanedJob(
        url="https://example.com/1",
        title_clean="Senior Backend Engineer",
        description_clean="Build services.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.seniority == "senior"


def test_employment_type_extraction() -> None:
    job = CleanedJob(
        url="https://example.com/2",
        title_clean="Data Analyst",
        description_clean="This is a full-time role with benefits.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.employment_type == "full_time"


def test_location_type_extraction() -> None:
    job = CleanedJob(
        url="https://example.com/3",
        title_clean="Engineer",
        description_clean="Work with the team.",
        location_clean="Hybrid - Berlin",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.location_type == "hybrid"


def test_salary_extraction_base() -> None:
    job = CleanedJob(
        url="https://example.com/4",
        title_clean="Engineer",
        description_clean="Compensation: $120,000 - $150,000 base salary.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min == 120000
    assert extracted.salary_max == 150000
    assert extracted.salary_currency == "USD"
    assert extracted.salary_period is None


def test_salary_extraction_hourly() -> None:
    job = CleanedJob(
        url="https://example.com/4b",
        title_clean="Provider",
        description_clean="Compensation is $140-$180 per hour.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min == 140
    assert extracted.salary_max == 180
    assert extracted.salary_currency == "USD"
    assert extracted.salary_period == "hour"


def test_salary_extraction_annual() -> None:
    job = CleanedJob(
        url="https://example.com/4c",
        title_clean="Analyst",
        description_clean="Annual salary: $120,000 - $150,000.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min == 120000
    assert extracted.salary_max == 150000
    assert extracted.salary_currency == "USD"
    assert extracted.salary_period == "year"


def test_salary_extraction_monthly() -> None:
    job = CleanedJob(
        url="https://example.com/4d",
        title_clean="Coordinator",
        description_clean="Compensation from €3,000 monthly.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min == 3000
    assert extracted.salary_max is None
    assert extracted.salary_currency == "EUR"
    assert extracted.salary_period == "month"


def test_skills_extraction_base() -> None:
    job = CleanedJob(
        url="https://example.com/5",
        title_clean="Data Engineer",
        description_clean="Required: Python, SQL, dbt, and AWS.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert "python" in extracted.skills
    assert "sql" in extracted.skills
    assert "dbt" in extracted.skills
    assert "aws" in extracted.skills


def test_skills_weak_mention_not_extracted() -> None:
    job = CleanedJob(
        url="https://example.com/5b",
        title_clean="Data Writer",
        description_clean="We sponsor the Python community and publish event recaps.",
        location_clean="Remote",
    )
    extracted = ExtractionStage().run_one(job)
    assert "python" not in extracted.skills


def test_no_signal_returns_none_or_empty() -> None:
    job = CleanedJob(
        url="https://example.com/6",
        title_clean="Role",
        description_clean="Something generic.",
        location_clean="",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.seniority is None
    assert extracted.employment_type is None
    assert extracted.location_type is None
    assert extracted.salary_min is None
    assert extracted.salary_max is None
    assert extracted.salary_currency is None
    assert extracted.salary_period is None
    assert extracted.skills == []


def test_salary_range_with_currency_and_period() -> None:
    job = CleanedJob(
        url="https://example.com/6b",
        title_clean="Driver",
        description_clean="Pay range: £600 - £800 per week depending on shift.",
        location_clean="Onsite",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min == 600
    assert extracted.salary_max == 800
    assert extracted.salary_currency == "GBP"
    assert extracted.salary_period == "week"


def test_case_without_salary_keeps_none() -> None:
    job = CleanedJob(
        url="https://example.com/6c",
        title_clean="Designer",
        description_clean="Benefits include insurance and bonus.",
        location_clean="Hybrid",
    )
    extracted = ExtractionStage().run_one(job)
    assert extracted.salary_min is None
    assert extracted.salary_max is None
    assert extracted.salary_currency is None
    assert extracted.salary_period is None


def test_run_extraction_stage_outputs_report_and_file(tmp_path: Path) -> None:
    in_path = tmp_path / "jobs_cleaned_en.jsonl"
    rows = [
        {
            "url": "https://example.com/7",
            "title_clean": "Junior Data Analyst",
            "description_clean": "Part-time role. Salary $60,000 - $80,000. Need SQL and Excel.",
            "location_clean": "Remote",
            "requirements_clean": "",
            "responsibilities_clean": "",
            "content_hash": "abc",
        }
    ]
    with in_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    out_path = tmp_path / "jobs_extracted_en.jsonl"
    report_dir = tmp_path / "docs"
    report = run_extraction_stage(input_path=in_path, output_path=out_path, report_dir=report_dir)
    assert report["rows_total"] == 1
    assert out_path.exists()
    assert (report_dir / "extraction_stage_step9.json").exists()
    assert (report_dir / "extraction_stage_step9.md").exists()

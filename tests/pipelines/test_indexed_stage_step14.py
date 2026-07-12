from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.indexed.run import run_indexed_stage


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_run_indexed_stage_composes_records_and_flags(tmp_path: Path) -> None:
    canonical_path = tmp_path / "canonical.jsonl"
    language_path = tmp_path / "language.jsonl"
    cleaned_path = tmp_path / "cleaned.jsonl"
    extracted_path = tmp_path / "extracted.jsonl"
    titled_path = tmp_path / "titled.jsonl"
    out_path = tmp_path / "jobs_indexed_en.jsonl"
    report_dir = tmp_path / "docs"

    _write_jsonl(
        canonical_path,
        [
            {
                "source": "greenhouse",
                "source_org": "acme",
                "url": "https://example.com/1",
                "title": "Senior Data Engineer",
                "company_name": "Acme",
                "location_raw": "Remote",
                "published_at": "2026-03-01T10:00:00Z",
                "raw_payload": {"id": 1},
            },
            {
                "source": "greenhouse",
                "source_org": "acme",
                "url": "https://example.com/2",
                "title": "Unclear Role",
                "company_name": "Acme",
                "raw_payload": {"id": 2},
            },
        ],
    )
    _write_jsonl(
        language_path,
        [
            {
                "url": "https://example.com/1",
                "language_bucket": "en",
                "language_reason": "hint_detector_agree",
                "language_code": "en",
                "language_confidence": 0.98,
            },
            {
                "url": "https://example.com/2",
                "language_bucket": "unknown",
                "language_reason": "low_signal_mixed_or_ambiguous",
            },
        ],
    )
    _write_jsonl(
        cleaned_path,
        [
            {
                "url": "https://example.com/1",
                "title_clean": "Senior Data Engineer",
                "description_clean": "Build pipelines in Python and SQL.",
                "location_clean": "Remote",
            },
            {
                "url": "https://example.com/2",
                "title_clean": "Unclear Role",
                "description_clean": "General support",
                "location_clean": "",
            },
        ],
    )
    _write_jsonl(
        extracted_path,
        [
            {
                "url": "https://example.com/1",
                "seniority": "senior",
                "employment_type": "full_time",
                "location_type": "remote",
                "salary_min": 120000,
                "salary_max": 150000,
                "salary_currency": "USD",
                "salary_period": "year",
                "skills": ["python", "sql"],
                "tags": {"has_salary": True},
            },
            {
                "url": "https://example.com/2",
                "skills": [],
                "tags": {},
            },
        ],
    )
    _write_jsonl(
        titled_path,
        [
            {
                "url": "https://example.com/1",
                "normalized_title": "data_engineer",
                "role_family": "data_engineering",
                "classification_status": "matched",
                "match_method": "rule_pattern",
                "confidence": 0.85,
            },
            {
                "url": "https://example.com/2",
                "normalized_title": "other",
                "role_family": "other",
                "classification_status": "other",
                "match_method": "fallback",
                "confidence": 0.1,
            },
        ],
    )

    report = run_indexed_stage(
        input_canonical_path=canonical_path,
        input_language_path=language_path,
        input_cleaned_path=cleaned_path,
        input_extracted_path=extracted_path,
        input_titled_path=titled_path,
        output_path=out_path,
        report_dir=report_dir,
        sample_size=2,
    )

    assert report["rows_total"] == 2
    assert report["missing_components"] == 0
    assert (report_dir / "indexed_job_stage_step14.json").exists()
    assert (report_dir / "indexed_job_stage_step14.md").exists()

    rows = [json.loads(x) for x in out_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(rows) == 2

    row1 = next(r for r in rows if r["url"] == "https://example.com/1")
    assert row1["language_bucket"] == "en"
    assert row1["has_salary"] is True
    assert row1["has_skills"] is True
    assert row1["has_location"] is True
    assert row1["title_is_other"] is False

    row2 = next(r for r in rows if r["url"] == "https://example.com/2")
    assert row2["title_is_other"] is True
    assert row2["has_skills"] is False


def test_run_indexed_stage_treats_non_role_as_excluded_from_normal_results(tmp_path: Path) -> None:
    canonical_path = tmp_path / "canonical.jsonl"
    language_path = tmp_path / "language.jsonl"
    cleaned_path = tmp_path / "cleaned.jsonl"
    extracted_path = tmp_path / "extracted.jsonl"
    titled_path = tmp_path / "titled.jsonl"
    out_path = tmp_path / "jobs_indexed_en.jsonl"

    _write_jsonl(
        canonical_path,
        [
            {
                "source": "greenhouse",
                "source_org": "acme",
                "url": "https://example.com/non-role",
                "title": "General Application",
                "company_name": "Acme",
                "raw_payload": {"id": 1},
            }
        ],
    )
    _write_jsonl(
        language_path,
        [
            {
                "url": "https://example.com/non-role",
                "language_bucket": "en",
                "language_reason": "hint_detector_agree",
            }
        ],
    )
    _write_jsonl(
        cleaned_path,
        [
            {
                "url": "https://example.com/non-role",
                "title_clean": "General Application",
                "description_clean": "",
                "location_clean": "",
            }
        ],
    )
    _write_jsonl(
        extracted_path,
        [
            {
                "url": "https://example.com/non-role",
                "skills": [],
                "tags": {},
            }
        ],
    )
    _write_jsonl(
        titled_path,
        [
            {
                "url": "https://example.com/non-role",
                "normalized_title": "non_role_recruiting_entry",
                "role_family": "non_role",
                "classification_status": "non_role",
                "match_method": "rule_exact",
                "confidence": 0.98,
                "notes": ["non_role_recruiting_entry"],
            }
        ],
    )

    run_indexed_stage(
        input_canonical_path=canonical_path,
        input_language_path=language_path,
        input_cleaned_path=cleaned_path,
        input_extracted_path=extracted_path,
        input_titled_path=titled_path,
        output_path=out_path,
    )
    rows = [json.loads(x) for x in out_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert rows[0]["normalized_title"] == "non_role_recruiting_entry"
    assert rows[0]["role_family"] == "non_role"
    assert rows[0]["classification_status"] == "non_role"
    assert rows[0]["title_is_other"] is True

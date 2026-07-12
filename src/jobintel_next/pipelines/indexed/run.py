from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

from jobintel_next.domain.models import IndexedJob

from .io import (
    row_to_canonical,
    row_to_cleaned,
    row_to_extracted,
    row_to_language_decision,
    row_to_title_classification,
)


def _load_by_url(path: Path, parser) -> tuple[dict[str, Any], int]:
    items: dict[str, Any] = {}
    invalid = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            row = json.loads(s)
            if not isinstance(row, dict):
                invalid += 1
                continue
            model = parser(row)
            if model is None:
                invalid += 1
                continue
            items[model.url] = model
    return items, invalid


def run_indexed_stage(
    *,
    input_canonical_path: str | Path,
    input_language_path: str | Path,
    input_cleaned_path: str | Path,
    input_extracted_path: str | Path,
    input_titled_path: str | Path,
    output_path: str | Path,
    report_dir: str | Path = "docs",
    limit: int | None = None,
    sample_size: int = 10,
) -> dict[str, Any]:
    canonical_path = Path(input_canonical_path)
    language_path = Path(input_language_path)
    cleaned_path = Path(input_cleaned_path)
    extracted_path = Path(input_extracted_path)
    titled_path = Path(input_titled_path)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    report_path_dir = Path(report_dir)
    report_path_dir.mkdir(parents=True, exist_ok=True)

    canonical_by_url, invalid_canonical = _load_by_url(canonical_path, row_to_canonical)
    language_by_url, invalid_language = _load_by_url(language_path, row_to_language_decision)
    cleaned_by_url, invalid_cleaned = _load_by_url(cleaned_path, row_to_cleaned)
    extracted_by_url, invalid_extracted = _load_by_url(extracted_path, row_to_extracted)
    titled_by_url, invalid_titled = _load_by_url(titled_path, row_to_title_classification)

    rows_total = 0
    missing_components = 0
    samples: list[dict[str, Any]] = []

    fill_counter = Counter()
    language_bucket_counter = Counter()

    with out_path.open("w", encoding="utf-8") as out:
        for url, canonical in canonical_by_url.items():
            language = language_by_url.get(url)
            cleaned = cleaned_by_url.get(url)
            extracted = extracted_by_url.get(url)
            title = titled_by_url.get(url)

            if not (language and cleaned and extracted and title):
                missing_components += 1
                continue

            has_salary = any(
                [
                    extracted.salary_min is not None,
                    extracted.salary_max is not None,
                    bool(extracted.salary_currency),
                ]
            )
            has_skills = bool(extracted.skills)
            has_location = any(
                [
                    bool(extracted.city),
                    bool(extracted.region),
                    bool(extracted.country),
                    bool(cleaned.location_clean),
                    bool(canonical.location_raw),
                ]
            )
            title_is_other = title.normalized_title in {"other", "non_role_recruiting_entry"}

            indexed = IndexedJob(
                source=canonical.source,
                source_org=canonical.source_org,
                url=canonical.url,
                company_name=canonical.company_name,
                title_raw=canonical.title,
                title_clean=cleaned.title_clean,
                normalized_title=title.normalized_title,
                role_family=title.role_family,
                classification_status=title.classification_status,
                match_method=title.match_method,
                confidence=title.confidence,
                language_bucket=language.bucket,
                language_reason=language.reason,
                language_code=language.language_code,
                language_confidence=language.confidence,
                published_at=canonical.published_at,
                updated_at=canonical.updated_at,
                seniority=extracted.seniority,
                employment_type=extracted.employment_type,
                location_type=extracted.location_type,
                city=extracted.city,
                region=extracted.region,
                country=extracted.country,
                salary_min=extracted.salary_min,
                salary_max=extracted.salary_max,
                salary_currency=extracted.salary_currency,
                salary_period=extracted.salary_period,
                skills=extracted.skills,
                has_salary=has_salary,
                has_skills=has_skills,
                has_location=has_location,
                title_is_other=title_is_other,
                tags=extracted.tags,
            )
            out.write(json.dumps(indexed.to_dict(), ensure_ascii=False) + "\n")
            rows_total += 1

            if indexed.language_bucket:
                language_bucket_counter[indexed.language_bucket] += 1
            if indexed.title_clean:
                fill_counter["title_clean"] += 1
            if indexed.normalized_title:
                fill_counter["normalized_title"] += 1
            if indexed.role_family:
                fill_counter["role_family"] += 1
            if indexed.seniority:
                fill_counter["seniority"] += 1
            if indexed.employment_type:
                fill_counter["employment_type"] += 1
            if indexed.location_type:
                fill_counter["location_type"] += 1
            if indexed.city:
                fill_counter["city"] += 1
            if indexed.region:
                fill_counter["region"] += 1
            if indexed.country:
                fill_counter["country"] += 1
            if indexed.salary_min is not None:
                fill_counter["salary_min"] += 1
            if indexed.salary_max is not None:
                fill_counter["salary_max"] += 1
            if indexed.salary_currency:
                fill_counter["salary_currency"] += 1
            if indexed.salary_period:
                fill_counter["salary_period"] += 1
            if indexed.skills:
                fill_counter["skills"] += 1
            if indexed.has_salary:
                fill_counter["has_salary"] += 1
            if indexed.has_skills:
                fill_counter["has_skills"] += 1
            if indexed.has_location:
                fill_counter["has_location"] += 1
            if indexed.title_is_other:
                fill_counter["title_is_other"] += 1

            if len(samples) < sample_size:
                samples.append(
                    {
                        "url": indexed.url,
                        "title_raw": indexed.title_raw,
                        "normalized_title": indexed.normalized_title,
                        "role_family": indexed.role_family,
                        "language_bucket": indexed.language_bucket,
                        "has_salary": indexed.has_salary,
                        "has_skills": indexed.has_skills,
                        "has_location": indexed.has_location,
                        "title_is_other": indexed.title_is_other,
                    }
                )

            if limit is not None and rows_total >= limit:
                break

    def _rate(value: int) -> float:
        return round((value * 100.0 / rows_total), 2) if rows_total else 0.0

    field_fill_rates = {
        k: {"count": v, "pct": _rate(v)}
        for k, v in sorted(fill_counter.items(), key=lambda x: x[0])
    }

    report = {
        "input_paths": {
            "canonical": str(canonical_path),
            "language": str(language_path),
            "cleaned": str(cleaned_path),
            "extracted": str(extracted_path),
            "titled": str(titled_path),
        },
        "output_path": str(out_path),
        "rows_total": rows_total,
        "invalid_rows_by_input": {
            "canonical": invalid_canonical,
            "language": invalid_language,
            "cleaned": invalid_cleaned,
            "extracted": invalid_extracted,
            "titled": invalid_titled,
        },
        "missing_components": missing_components,
        "language_bucket_counts": dict(language_bucket_counter),
        "field_fill_rates": field_fill_rates,
        "completeness_flags": {
            "has_salary": field_fill_rates.get("has_salary", {"count": 0, "pct": 0.0}),
            "has_skills": field_fill_rates.get("has_skills", {"count": 0, "pct": 0.0}),
            "has_location": field_fill_rates.get("has_location", {"count": 0, "pct": 0.0}),
            "title_is_other": field_fill_rates.get("title_is_other", {"count": 0, "pct": 0.0}),
        },
        "sample_indexed_rows": samples,
        "known_limits": [
            "No ranking or semantic retrieval in this step.",
            "Composition requires URL-level alignment across upstream artifacts.",
            "Quality flags are lightweight and deterministic by design.",
        ],
    }

    report_json = report_path_dir / "indexed_job_stage_step14.json"
    report_md = report_path_dir / "indexed_job_stage_step14.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Indexed Job Stage Step 14",
        "",
        "## Input Files",
        f"- canonical: `{canonical_path}`",
        f"- language: `{language_path}`",
        f"- cleaned: `{cleaned_path}`",
        f"- extracted: `{extracted_path}`",
        f"- titled: `{titled_path}`",
        f"- output: `{out_path}`",
        "",
        "## Counts",
        f"- rows_total: {rows_total}",
        f"- missing_components: {missing_components}",
        "",
        "## Field Fill Rates",
    ]
    for key, value in field_fill_rates.items():
        md_lines.append(f"- {key}: {value['count']} ({value['pct']}%)")
    md_lines += [
        "",
        "## Completeness Flags",
        f"- has_salary: {report['completeness_flags']['has_salary']['count']} ({report['completeness_flags']['has_salary']['pct']}%)",
        f"- has_skills: {report['completeness_flags']['has_skills']['count']} ({report['completeness_flags']['has_skills']['pct']}%)",
        f"- has_location: {report['completeness_flags']['has_location']['count']} ({report['completeness_flags']['has_location']['pct']}%)",
        f"- title_is_other: {report['completeness_flags']['title_is_other']['count']} ({report['completeness_flags']['title_is_other']['pct']}%)",
        "",
        "## Sample Indexed Rows",
    ]
    for sample in samples:
        md_lines.append(
            f"- {sample['url']} | title={sample['title_raw']} | normalized={sample['normalized_title']} | "
            f"language={sample['language_bucket']} | has_salary={sample['has_salary']} | "
            f"has_skills={sample['has_skills']} | has_location={sample['has_location']} | "
            f"title_is_other={sample['title_is_other']}"
        )

    md_lines += [
        "",
        "## Known Limits",
    ]
    for item in report["known_limits"]:
        md_lines.append(f"- {item}")

    report_md.write_text("\n".join(md_lines), encoding="utf-8")
    return report

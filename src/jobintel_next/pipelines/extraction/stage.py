from __future__ import annotations

from jobintel_next.domain.models import CleanedJob, ExtractedAttributes

from .rules import (
    extract_employment_type,
    extract_location_type,
    extract_salary,
    extract_seniority,
    extract_skills,
)


class ExtractionStage:
    """Extraction stage: CleanedJob -> ExtractedAttributes."""

    def run_one(self, job: CleanedJob) -> ExtractedAttributes:
        seniority, seniority_source = extract_seniority(job.title_clean, job.description_clean)
        employment_type, employment_source = extract_employment_type(job.title_clean, job.description_clean)
        location_type, location_source = extract_location_type(
            job.location_clean,
            job.title_clean,
            job.description_clean,
        )
        salary_min, salary_max, salary_currency, salary_period = extract_salary(job.description_clean)
        skills = extract_skills(
            job.title_clean,
            job.description_clean,
            job.requirements_clean,
            job.responsibilities_clean,
        )

        tags: dict[str, str | int | bool] = {
            "has_salary": bool(salary_min is not None or salary_max is not None),
            "skills_count": len(skills),
        }
        if seniority_source:
            tags["seniority_source"] = seniority_source
        if employment_source:
            tags["employment_source"] = employment_source
        if location_source:
            tags["location_type_source"] = location_source

        return ExtractedAttributes(
            url=job.url,
            seniority=seniority,
            employment_type=employment_type,
            location_type=location_type,
            city=None,
            region=None,
            country=None,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=salary_currency,
            salary_period=salary_period,
            skills=skills,
            tags=tags,
        )

    def run_many(self, jobs: list[CleanedJob]) -> list[ExtractedAttributes]:
        return [self.run_one(j) for j in jobs]

from __future__ import annotations

import hashlib

from jobintel_next.domain.models import CanonicalRawJob, CleanedJob

from .text_utils import (
    clean_description_text,
    clean_location_text,
    clean_title_text,
    extract_simple_sections,
)


def _stable_content_hash(
    *,
    title_clean: str,
    description_clean: str,
    location_clean: str,
    requirements_clean: str,
    responsibilities_clean: str,
) -> str:
    payload = "||".join(
        [
            title_clean,
            description_clean,
            location_clean,
            requirements_clean,
            responsibilities_clean,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CleaningStage:
    """Cleaning stage: CanonicalRawJob -> CleanedJob."""

    def run_one(self, job: CanonicalRawJob) -> CleanedJob:
        title_clean = clean_title_text(job.title)
        description_clean = clean_description_text(job.description_raw)
        location_clean = clean_location_text(job.location_raw)
        requirements_clean, responsibilities_clean = extract_simple_sections(
            job.description_raw,
            description_clean,
        )
        content_hash = _stable_content_hash(
            title_clean=title_clean,
            description_clean=description_clean,
            location_clean=location_clean,
            requirements_clean=requirements_clean,
            responsibilities_clean=responsibilities_clean,
        )
        return CleanedJob(
            url=job.url,
            title_clean=title_clean,
            description_clean=description_clean,
            location_clean=location_clean,
            requirements_clean=requirements_clean,
            responsibilities_clean=responsibilities_clean,
            content_hash=content_hash,
        )

    def run_many(self, jobs: list[CanonicalRawJob]) -> list[CleanedJob]:
        return [self.run_one(j) for j in jobs]


from __future__ import annotations

from jobintel_next.domain.models import CanonicalRawJob, LanguageDecision

from .policy import decide_language


class LanguageStage:
    """Language stage: CanonicalRawJob -> LanguageDecision."""

    def run_one(self, job: CanonicalRawJob) -> LanguageDecision:
        return decide_language(job)

    def run_many(self, jobs: list[CanonicalRawJob]) -> list[LanguageDecision]:
        return [self.run_one(j) for j in jobs]

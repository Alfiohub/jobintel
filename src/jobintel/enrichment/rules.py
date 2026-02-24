from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Sequence

from ..model import JobPost
from ..matching import normalize_text


@dataclass(frozen=True, slots=True)
class EnrichmentStats:
    input_count: int
    output_count: int
    low_quality_dropped: int


@dataclass(frozen=True, slots=True)
class EnrichmentRules:
    enabled: bool = True
    min_quality_score: float = 0.25

    SKILLS: tuple[str, ...] = (
        "python",
        "sql",
        "postgres",
        "postgresql",
        "spark",
        "dbt",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "airflow",
        "snowflake",
        "databricks",
        "power bi",
        "tableau",
    )

    def enrich_many(self, posts: Sequence[JobPost]) -> tuple[list[JobPost], EnrichmentStats]:
        if not self.enabled:
            return list(posts), EnrichmentStats(len(posts), len(posts), 0)

        out: list[JobPost] = []
        dropped = 0
        for p in posts:
            ep = self.enrich_one(p)
            q = ep.quality_score if ep.quality_score is not None else 0.0
            if q < self.min_quality_score:
                dropped += 1
                continue
            out.append(ep)
        return out, EnrichmentStats(len(posts), len(out), dropped)

    def enrich_one(self, post: JobPost) -> JobPost:
        text = normalize_text("\n".join([post.title, post.description_text or "", post.location_raw or "", " ".join(post.tags)]))

        workplace_type = post.workplace_type or self._infer_workplace_type(text)
        seniority = post.seniority or self._infer_seniority(text)
        employment_type = post.employment_type or self._infer_employment_type(text)
        function_family = post.function_family or self._infer_function_family(text)

        skill_tags = self._extract_skills(text)
        merged_tags = tuple(dict.fromkeys(tuple(post.tags) + skill_tags))
        quality = self._quality_score(post, text, workplace_type, merged_tags)

        return replace(
            post,
            workplace_type=workplace_type,
            seniority=seniority,
            employment_type=employment_type,
            function_family=function_family,
            tags=merged_tags,
            quality_score=quality,
        )

    def _extract_skills(self, text: str) -> tuple[str, ...]:
        found: list[str] = []
        for skill in self.SKILLS:
            if skill in text:
                found.append(skill)
        return tuple(found)

    @staticmethod
    def _infer_workplace_type(text: str) -> str | None:
        if any(k in text for k in ("remote", "work from home", "distributed", "anywhere")):
            return "remote"
        if "hybrid" in text:
            return "hybrid"
        if any(k in text for k in ("on-site", "onsite", "on site")):
            return "onsite"
        return None

    @staticmethod
    def _infer_seniority(text: str) -> str | None:
        if any(k in text for k in ("junior", "entry level", "graduate", "intern")):
            return "junior"
        if any(k in text for k in ("staff", "principal", "director", "vp", "vice president", "head of", "lead")):
            return "senior"
        if "senior" in text or "sr." in text or " sr " in text:
            return "senior"
        return None

    @staticmethod
    def _infer_employment_type(text: str) -> str | None:
        if "full-time" in text or "full time" in text:
            return "full_time"
        if "part-time" in text or "part time" in text:
            return "part_time"
        if "contract" in text or "freelance" in text:
            return "contract"
        return None

    @staticmethod
    def _infer_function_family(text: str) -> str | None:
        if any(k in text for k in ("data engineer", "data scientist", "analytics", "bi ")):
            return "data"
        if any(k in text for k in ("software engineer", "backend", "frontend", "full stack", "devops")):
            return "engineering"
        if any(k in text for k in ("product manager", "product designer", "product marketing")):
            return "product"
        if any(k in text for k in ("account executive", "sales", "business development")):
            return "sales"
        return None

    @staticmethod
    def _quality_score(post: JobPost, text: str, workplace_type: str | None, tags: tuple[str, ...]) -> float:
        score = 0.0
        if post.title:
            score += 0.2
        if post.company_name:
            score += 0.2
        if post.url:
            score += 0.2
        if (post.description_text or "") and len(post.description_text or "") >= 80:
            score += 0.15
        if post.location_raw:
            score += 0.1
        if workplace_type is not None:
            score += 0.05
        if tags:
            score += 0.05
        if post.posted_at is not None:
            score += 0.05
        # Penalize obviously noisy records
        if len(text) < 20:
            score -= 0.2
        if len((post.title or "").strip()) < 4:
            score -= 0.25
        if not (post.description_text or "").strip():
            score -= 0.2
        if not (post.location_raw or "").strip():
            score -= 0.1
        return max(0.0, min(1.0, score))

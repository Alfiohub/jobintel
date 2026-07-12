from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


LanguageBucket = Literal["en", "non_en", "unknown"]
ClassificationStatus = Literal["matched", "fallback", "other", "non_role"]
MatchMethod = Literal["rule_exact", "rule_pattern", "fallback", "manual_override"]


@dataclass(frozen=True)
class SourceRawJob:
    source: str
    source_org: str
    fetched_at: str
    payload: dict[str, Any]
    source_record_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalRawJob:
    source: str
    source_org: str
    url: str
    title: str
    company_name: str
    raw_payload: dict[str, Any]
    external_id: str | None = None
    location_raw: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    language_hint: str | None = None
    description_raw: str | None = None
    departments_raw: list[Any] | None = None
    offices_raw: list[Any] | None = None

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("CanonicalRawJob.source is required")
        if not self.source_org.strip():
            raise ValueError("CanonicalRawJob.source_org is required")
        if not self.url.strip():
            raise ValueError("CanonicalRawJob.url is required")
        if not self.title.strip():
            raise ValueError("CanonicalRawJob.title is required")
        if not self.company_name.strip():
            raise ValueError("CanonicalRawJob.company_name is required")
        if not isinstance(self.raw_payload, dict):
            raise ValueError("CanonicalRawJob.raw_payload must be a dict")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LanguageDecision:
    url: str
    bucket: LanguageBucket
    reason: str
    language_code: str | None = None
    confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CleanedJob:
    url: str
    title_clean: str
    description_clean: str
    location_clean: str
    requirements_clean: str = ""
    responsibilities_clean: str = ""
    content_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExtractedAttributes:
    url: str
    seniority: str | None = None
    employment_type: str | None = None
    location_type: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    skills: list[str] = field(default_factory=list)
    tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TitleClassification:
    url: str
    normalized_title: str
    role_family: str
    classification_status: ClassificationStatus
    match_method: MatchMethod
    confidence: float
    matched_rule_id: str | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IndexedJob:
    source: str
    source_org: str
    url: str
    company_name: str
    title_raw: str
    title_clean: str
    normalized_title: str
    role_family: str
    classification_status: ClassificationStatus
    match_method: MatchMethod
    confidence: float
    language_bucket: LanguageBucket | None = None
    language_reason: str | None = None
    language_code: str | None = None
    language_confidence: float | None = None
    published_at: str | None = None
    updated_at: str | None = None
    seniority: str | None = None
    employment_type: str | None = None
    location_type: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    skills: list[str] = field(default_factory=list)
    has_salary: bool = False
    has_skills: bool = False
    has_location: bool = False
    title_is_other: bool = False
    tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

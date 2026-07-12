from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _clean_str(v: Any) -> str:
    return str(v or "").strip()


def _canon_id(source: str, external_id: str | None, url: str) -> str:
    base = f"{source.strip().lower()}|{(external_id or '').strip().lower()}|{url.strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:20]


@dataclass(frozen=True, slots=True)
class CanonicalJob:
    id: str
    source: str
    url: str
    title: str
    company_name: str

    source_org: Optional[str] = None
    external_id: Optional[str] = None

    description_text: Optional[str] = None
    location_raw: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    workplace_type: Optional[str] = None  # remote | hybrid | onsite

    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    function_family: Optional[str] = None

    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None

    posted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ingested_at: datetime = field(default_factory=_now_utc)

    language: Optional[str] = None
    tags: tuple[str, ...] = ()
    raw_payload: Mapping[str, Any] = field(default_factory=dict)
    quality_score: Optional[float] = None

    @classmethod
    def from_source(
        cls,
        *,
        source: str,
        url: str,
        title: str,
        company_name: str,
        source_org: str | None = None,
        external_id: str | None = None,
        description_text: str | None = None,
        location_raw: str | None = None,
        country_code: str | None = None,
        region: str | None = None,
        city: str | None = None,
        workplace_type: str | None = None,
        employment_type: str | None = None,
        seniority: str | None = None,
        function_family: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        salary_currency: str | None = None,
        salary_period: str | None = None,
        posted_at: datetime | None = None,
        updated_at: datetime | None = None,
        ingested_at: datetime | None = None,
        language: str | None = None,
        tags: tuple[str, ...] = (),
        raw_payload: Mapping[str, Any] | None = None,
        quality_score: float | None = None,
    ) -> "CanonicalJob":
        s = _clean_str(source)
        u = _clean_str(url)
        t = _clean_str(title)
        c = _clean_str(company_name)

        if not s:
            raise ValueError("canonical job missing source")
        if not u:
            raise ValueError("canonical job missing url")
        if not t:
            raise ValueError("canonical job missing title")
        if not c:
            raise ValueError("canonical job missing company_name")

        wid = _canon_id(s, external_id, u)
        wt = _clean_str(workplace_type).lower() if workplace_type else None
        if wt not in {None, "remote", "hybrid", "onsite"}:
            wt = None

        return cls(
            id=wid,
            source=s,
            url=u,
            title=t,
            company_name=c,
            source_org=_clean_str(source_org) or None,
            external_id=_clean_str(external_id) or None,
            description_text=_clean_str(description_text) or None,
            location_raw=_clean_str(location_raw) or None,
            country_code=_clean_str(country_code).upper() or None,
            region=_clean_str(region) or None,
            city=_clean_str(city) or None,
            workplace_type=wt,
            employment_type=_clean_str(employment_type) or None,
            seniority=_clean_str(seniority) or None,
            function_family=_clean_str(function_family) or None,
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=_clean_str(salary_currency).upper() or None,
            salary_period=_clean_str(salary_period) or None,
            posted_at=posted_at,
            updated_at=updated_at,
            ingested_at=ingested_at or _now_utc(),
            language=_clean_str(language) or None,
            tags=tuple(x for x in tags if isinstance(x, str) and x.strip()),
            raw_payload=raw_payload or {},
            quality_score=quality_score,
        )

    # Backward compatibility for existing pipeline/scoring/store
    @property
    def company(self) -> str:
        return self.company_name

    @property
    def location(self) -> str:
        return self.location_raw or ""

    @property
    def description(self) -> str:
        return self.description_text or ""

    @property
    def raw(self) -> Mapping[str, Any]:
        return self.raw_payload

    @property
    def remote(self) -> Optional[bool]:
        if self.workplace_type == "remote":
            return True
        if self.workplace_type in {"hybrid", "onsite"}:
            return False
        return None

    @property
    def published_at(self) -> Optional[datetime]:
        return self.posted_at or self.updated_at

    @property
    def contract_type(self) -> Optional[str]:
        return self.employment_type

    @property
    def salary_text(self) -> Optional[str]:
        parts: list[str] = []
        if self.salary_min is not None or self.salary_max is not None:
            parts.append(f"{self.salary_min or ''}-{self.salary_max or ''}".strip("-"))
        if self.salary_currency:
            parts.append(self.salary_currency)
        if self.salary_period:
            parts.append(self.salary_period)
        txt = " ".join([p for p in parts if p])
        return txt or None


def validate_canonical(job: CanonicalJob) -> None:
    if not job.id:
        raise ValueError("canonical id is required")
    if not job.source:
        raise ValueError("canonical source is required")
    if not job.url:
        raise ValueError("canonical url is required")
    if not job.title:
        raise ValueError("canonical title is required")
    if not job.company_name:
        raise ValueError("canonical company_name is required")

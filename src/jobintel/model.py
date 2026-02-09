from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


@dataclass(frozen=True, slots=True)
class JobPost:
    title: str
    company: str
    location: str
    url: str
    source: str

    remote: Optional[bool] = None
    published_at: Optional[datetime] = None

    description: str = ""

    seniority: Optional[str] = None
    contract_type: Optional[str] = None
    salary_text: Optional[str] = None

    tags: tuple[str, ...] = ()

    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ScoredJob:
    post: JobPost
    score: int
    reasons: tuple[str, ...]
    fingerprint: str

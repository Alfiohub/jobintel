from __future__ import annotations

from dataclasses import dataclass

from .canonical import CanonicalJob


JobPost = CanonicalJob


@dataclass(frozen=True, slots=True)
class ScoredJob:
    post: JobPost
    score: int
    reasons: tuple[str, ...]
    fingerprint: str

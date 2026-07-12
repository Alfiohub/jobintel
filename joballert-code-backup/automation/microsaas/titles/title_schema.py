from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class TitleInput(BaseModel):
    title_raw: str = Field(min_length=1)


ClassificationStatus = Literal["matched", "fallback", "other"]
MatchMethod = Literal["rule_exact", "rule_pattern", "fallback", "manual_override"]


class TitleNormalizationResult(BaseModel):
    title_raw: str
    title_clean: str
    normalized_title: str
    role_family: str
    classification_status: ClassificationStatus
    match_method: MatchMethod
    confidence: float
    matched_rule_id: Optional[str] = None
    notes: List[str] = Field(default_factory=list)

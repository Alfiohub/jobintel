from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextRuleDecision:
    normalized_title: str
    role_family: str
    matched_rule_id: str
    confidence: float
    evidence_hits: list[str]
    exclusion_hits: list[str]


PARTNER_TITLE_PATTERNS = [
    "partner growth manager",
    "partner development manager",
    "senior partner development manager",
    "core partner development manager",
    "strategic si partner development manager",
    "senior technology partner development manager",
    "strategic partner director",
    "regional partner director",
    "partner director",
]

PARTNER_COMMERCIAL_SIGNALS = [
    "pipeline",
    "bookings",
    "revenue",
    "business growth",
    "go to market",
    "go-to-market",
    "portfolio growth",
    "merchant acquisition",
    "new business opportunities",
    "co-sell",
    "joint business plan",
    "partner relationships",
    "strategic partnerships",
    "expand business value",
    "growth outcomes",
]

PARTNER_DEPARTMENT_SIGNALS = [
    "sales",
    "partner growth",
    "partner development",
    "alliances",
    "alliances department",
    "partnerships",
]

PARTNER_BLOCKED_SIGNALS = [
    "client strategy",
    "client strategist",
    "client partnership",
    "provider",
    "patient",
    "clinical",
    "education",
    "district",
]


def _hits(text: str, keywords: list[str]) -> list[str]:
    lower = (text or "").lower()
    return [kw for kw in keywords if kw in lower]


def _department_text(row: dict[str, Any]) -> str:
    departments = row.get("departments_raw") or []
    return " ".join(str(item.get("name") or "") for item in departments)


def decide_context_rule(row: dict[str, Any]) -> ContextRuleDecision | None:
    title = str(row.get("title_clean") or "").lower()
    if not any(pattern in title for pattern in PARTNER_TITLE_PATTERNS):
        return None

    dept_text = _department_text(row)
    description = str(row.get("description_clean") or "")
    responsibilities = str(row.get("responsibilities_clean") or "")
    requirements = str(row.get("requirements_clean") or "")
    context_text = " ".join(part for part in [description, responsibilities, requirements] if part)
    focus_text = " ".join(part for part in [title, dept_text, responsibilities, description] if part)

    commercial_hits = _hits(context_text, PARTNER_COMMERCIAL_SIGNALS)
    dept_hits = _hits(dept_text, PARTNER_DEPARTMENT_SIGNALS)
    blocked_hits = _hits(focus_text, PARTNER_BLOCKED_SIGNALS)

    if blocked_hits:
        return None
    if not dept_hits:
        return None
    if len(commercial_hits) < 2:
        return None

    evidence_hits: list[str] = []
    for hit in dept_hits + commercial_hits:
        if hit not in evidence_hits:
            evidence_hits.append(hit)

    return ContextRuleDecision(
        normalized_title="account_manager",
        role_family="sales",
        matched_rule_id="ctx_partner_lane_v1",
        confidence=0.84 if len(commercial_hits) >= 3 else 0.8,
        evidence_hits=evidence_hits,
        exclusion_hits=blocked_hits,
    )

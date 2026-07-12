from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContextRuleDecision:
    title_clean: str
    normalized_title: str
    role_family: str
    matched_rule_id: str
    confidence: float
    evidence_hits: list[str]
    exclusion_hits: list[str]


ONBOARDING_POSITIVE = [
    "customer",
    "client",
    "merchant",
    "implementation",
    "onboarding",
]
ONBOARDING_PRODUCT_SUPPORT = [
    "platform",
    "product",
    "software",
    "saas",
    "adoption",
    "customer success",
    "getting started",
    "implementation process",
]
ONBOARDING_DEPARTMENT_SUPPORT = [
    "sales",
    "revops",
    "customer success",
    "client service",
    "getting started",
    "practice growth",
]
ONBOARDING_HARD_EXCLUSION = [
    "new hire",
    "hris",
    "employee lifecycle",
    "talent acquisition",
    "payroll",
]
ONBOARDING_SOFT_EXCLUSION = [
    "kyc",
    "aml",
    "verification",
    "due diligence",
    "underwriting",
    "compliance",
    "employee",
]

PRODUCER_POSITIVE = [
    "content",
    "news",
    "broadcast",
    "creative",
    "video",
    "campaign",
]
PRODUCER_EXCLUSION = [
    "game",
    "jira",
    "scrum",
    "engineers",
]


def _hits(text: str, keywords: list[str]) -> list[str]:
    lower = (text or "").lower()
    return [kw for kw in keywords if kw in lower]


def _department_text(row: dict[str, Any]) -> str:
    departments = row.get("departments_raw") or []
    return " ".join(str(item.get("name") or "") for item in departments)


def _weighted_onboarding_signal(row: dict[str, Any]) -> tuple[list[str], list[str], int]:
    description = str(row.get("description_clean") or "")
    responsibilities = str(row.get("responsibilities_clean") or "")
    requirements = str(row.get("requirements_clean") or "")
    department = _department_text(row)

    hits: list[str] = []
    score = 0

    def add_hits(text: str, keywords: list[str], weight: int) -> None:
        nonlocal score
        for hit in _hits(text, keywords):
            if hit not in hits:
                hits.append(hit)
            score += weight

    add_hits(description, ONBOARDING_POSITIVE, 1)
    add_hits(responsibilities, ONBOARDING_POSITIVE, 2)
    add_hits(requirements, ONBOARDING_POSITIVE, 1)
    add_hits(description, ONBOARDING_PRODUCT_SUPPORT, 1)
    add_hits(responsibilities, ONBOARDING_PRODUCT_SUPPORT, 2)
    add_hits(requirements, ONBOARDING_PRODUCT_SUPPORT, 1)
    add_hits(department, ONBOARDING_DEPARTMENT_SUPPORT, 2)

    negatives: list[str] = []
    for field_text in [description, responsibilities, requirements, department]:
        for hit in _hits(field_text, ONBOARDING_HARD_EXCLUSION + ONBOARDING_SOFT_EXCLUSION):
            if hit not in negatives:
                negatives.append(hit)

    return hits, negatives, score


def decide_context_rule(row: dict[str, Any]) -> ContextRuleDecision | None:
    title = str(row.get("title_clean") or "")
    text = str(row.get("context_text") or "")

    if title == "Onboarding Specialist":
        pos, neg, score = _weighted_onboarding_signal(row)
        hard_neg = [hit for hit in neg if hit in ONBOARDING_HARD_EXCLUSION]
        soft_neg = [hit for hit in neg if hit in ONBOARDING_SOFT_EXCLUSION]
        product_hits = [hit for hit in pos if hit in ONBOARDING_PRODUCT_SUPPORT]
        soft_neg_limit = 2 if score >= 10 else 1
        if score >= 7 and product_hits and not hard_neg and len(soft_neg) <= soft_neg_limit:
            return ContextRuleDecision(
                title_clean=title,
                normalized_title="customer_success_manager",
                role_family="customer_success",
                matched_rule_id="ctx_onboarding_specialist_customer_success_v2",
                confidence=0.88 if score >= 9 else 0.8,
                evidence_hits=pos,
                exclusion_hits=neg,
            )
        return None

    if title == "Producer":
        pos = _hits(text, PRODUCER_POSITIVE)
        neg = _hits(text, PRODUCER_EXCLUSION)
        if len(pos) >= 2 and len(neg) == 0:
            return ContextRuleDecision(
                title_clean=title,
                normalized_title="content_producer",
                role_family="content",
                matched_rule_id="ctx_producer_content_v1",
                confidence=0.84 if len(pos) >= 3 else 0.78,
                evidence_hits=pos,
                exclusion_hits=neg,
            )
        return None

    return None

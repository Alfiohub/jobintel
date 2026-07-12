from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Literal


RouteStatus = Literal["matched_role", "non_role", "taxonomy_gap", "manual_review"]
RouteLane = Literal["matched", "non_role", "taxonomy_gap", "attack_now", "recoverable_with_context", "long_tail"]


@dataclass(frozen=True)
class OpenSetRouteDecision:
    route_status: RouteStatus
    route_lane: RouteLane
    suggested_target_label: str | None
    suggested_role_family: str | None
    route_reason: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_TAXONOMY_GAP_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\bquant(itative)? research(er)?\b", re.IGNORECASE), "quantitative_researcher", "finance"),
    (re.compile(r"\bcredit analyst\b", re.IGNORECASE), "credit_analyst", "finance"),
    (re.compile(r"\bmarket access director\b", re.IGNORECASE), "market_access_director", "life_sciences"),
]

_ATTACK_NOW_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(
            r"\b("
            r"backend developer|back-end engineer|backend engineer|front-end engineer|frontend engineer|"
            r"full[- ]stack engineer|android engineer|ios engineer|software engineer|software developer"
            r")\b",
            re.IGNORECASE,
        ),
        "software_engineer",
        "software_engineering",
    ),
    (
        re.compile(r"\b(engineering director|manager, software (development|engineering)|head of engineering)\b", re.IGNORECASE),
        "engineering_manager",
        "software_engineering",
    ),
    (
        re.compile(r"\b(corporate development|business development|m&a)\b", re.IGNORECASE),
        "business_development_manager",
        "sales",
    ),
    (
        re.compile(r"\b(sales director|director, sales|vp, sales|director, enterprise sales)\b", re.IGNORECASE),
        "sales_director",
        "sales",
    ),
    (
        re.compile(r"\b(financial planning|fp&a|strategic finance|finance manager)\b", re.IGNORECASE),
        "financial_analyst",
        "finance",
    ),
    (
        re.compile(r"\b(it specialist|application support specialist|technical support engineer|cloud administrator)\b", re.IGNORECASE),
        "it_support_specialist",
        "it_operations",
    ),
    (
        re.compile(r"\b(thermal engineer|fluids engineer|rotor dynamics|propulsion design engineer)\b", re.IGNORECASE),
        "mechanical_engineer",
        "industrial_engineering",
    ),
    (
        re.compile(r"\b(systems administrator|business applications administrator|salesforce .*administrator)\b", re.IGNORECASE),
        "systems_administrator",
        "it_operations",
    ),
]

_CONTEXT_REVIEW_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(r"\b(onboarding specialist|customer onboarding specialist|saas onboarding specialist)\b", re.IGNORECASE),
        "customer_success_manager",
        "customer_success",
    ),
    (
        re.compile(
            r"\b(partner growth manager|partner development manager|partner director|account manager|engagement manager)\b",
            re.IGNORECASE,
        ),
        "account_manager",
        "sales",
    ),
    (
        re.compile(r"\b(project manager|project engineer|implementation specialist|implementation consultant)\b", re.IGNORECASE),
        "project_manager",
        "operations",
    ),
]


def route_open_set_row(row: dict[str, Any]) -> OpenSetRouteDecision:
    status = str(row.get("classification_status") or "").strip()
    normalized_title = str(row.get("normalized_title") or "").strip()
    role_family = str(row.get("role_family") or "").strip()
    title = str(row.get("title_clean") or row.get("title") or "").strip()

    if status == "non_role" or normalized_title == "non_role_recruiting_entry":
        return OpenSetRouteDecision(
            route_status="non_role",
            route_lane="non_role",
            suggested_target_label="non_role_recruiting_entry",
            suggested_role_family="non_role",
            route_reason="already_classified_non_role",
            confidence=0.99,
        )

    if status == "matched" and normalized_title not in {"other", "non_role_recruiting_entry"}:
        return OpenSetRouteDecision(
            route_status="matched_role",
            route_lane="matched",
            suggested_target_label=normalized_title,
            suggested_role_family=role_family,
            route_reason="already_classified_matched_role",
            confidence=float(row.get("confidence") or 0.99),
        )

    for pattern, label, family in _TAXONOMY_GAP_RULES:
        if pattern.search(title):
            return OpenSetRouteDecision(
                route_status="taxonomy_gap",
                route_lane="taxonomy_gap",
                suggested_target_label=label,
                suggested_role_family=family,
                route_reason="matches_known_taxonomy_gap_candidate",
                confidence=0.8,
            )

    for pattern, label, family in _ATTACK_NOW_RULES:
        if pattern.search(title):
            return OpenSetRouteDecision(
                route_status="manual_review",
                route_lane="attack_now",
                suggested_target_label=label,
                suggested_role_family=family,
                route_reason="matches_high_roi_title_only_candidate",
                confidence=0.72,
            )

    for pattern, label, family in _CONTEXT_REVIEW_RULES:
        if pattern.search(title):
            return OpenSetRouteDecision(
                route_status="manual_review",
                route_lane="recoverable_with_context",
                suggested_target_label=label,
                suggested_role_family=family,
                route_reason="matches_context_resolution_lane",
                confidence=0.68,
            )

    return OpenSetRouteDecision(
        route_status="manual_review",
        route_lane="long_tail",
        suggested_target_label=None,
        suggested_role_family=None,
        route_reason="residual_long_tail_unresolved",
        confidence=0.35,
    )

from __future__ import annotations

from jobintel_next.pipelines.titles.open_set_router import route_open_set_row


def test_route_open_set_row_preserves_matched_role() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "Senior Software Engineer",
            "normalized_title": "software_engineer",
            "role_family": "software_engineering",
            "classification_status": "matched",
            "confidence": 0.95,
        }
    )
    assert decision.route_status == "matched_role"
    assert decision.route_lane == "matched"
    assert decision.suggested_target_label == "software_engineer"


def test_route_open_set_row_routes_non_role() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "General Application",
            "normalized_title": "non_role_recruiting_entry",
            "role_family": "non_role",
            "classification_status": "non_role",
        }
    )
    assert decision.route_status == "non_role"
    assert decision.route_lane == "non_role"


def test_route_open_set_row_routes_taxonomy_gap() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "Senior Credit Analyst",
            "normalized_title": "other",
            "role_family": "other",
            "classification_status": "other",
        }
    )
    assert decision.route_status == "taxonomy_gap"
    assert decision.suggested_target_label == "credit_analyst"


def test_route_open_set_row_routes_attack_now_review() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "Backend Developer (Node.js)",
            "normalized_title": "other",
            "role_family": "other",
            "classification_status": "other",
        }
    )
    assert decision.route_status == "manual_review"
    assert decision.route_lane == "attack_now"
    assert decision.suggested_target_label == "software_engineer"


def test_route_open_set_row_routes_context_review() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "Onboarding Specialist",
            "normalized_title": "other",
            "role_family": "other",
            "classification_status": "other",
        }
    )
    assert decision.route_status == "manual_review"
    assert decision.route_lane == "recoverable_with_context"
    assert decision.suggested_target_label == "customer_success_manager"


def test_route_open_set_row_routes_long_tail_review() -> None:
    decision = route_open_set_row(
        {
            "title_clean": "Chief of Staff to the CEO",
            "normalized_title": "other",
            "role_family": "other",
            "classification_status": "other",
        }
    )
    assert decision.route_status == "manual_review"
    assert decision.route_lane == "long_tail"
    assert decision.suggested_target_label is None

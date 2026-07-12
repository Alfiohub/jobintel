from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.manual_review_prioritizer import build_prioritizer_payload


def test_build_prioritizer_payload_groups_manual_review(tmp_path: Path) -> None:
    input_path = tmp_path / "routed.jsonl"
    rows = [
        {
            "title_clean": "Backend Developer",
            "company_name": "acme",
            "route_status": "manual_review",
            "route_lane": "attack_now",
            "suggested_target_label": "software_engineer",
            "route_reason": "matches_high_roi_title_only_candidate",
            "url": "https://e/1",
        },
        {
            "title_clean": "Backend Engineer",
            "company_name": "beta",
            "route_status": "manual_review",
            "route_lane": "attack_now",
            "suggested_target_label": "software_engineer",
            "route_reason": "matches_high_roi_title_only_candidate",
            "url": "https://e/2",
        },
        {
            "title_clean": "Onboarding Specialist",
            "company_name": "gamma",
            "route_status": "manual_review",
            "route_lane": "recoverable_with_context",
            "suggested_target_label": "customer_success_manager",
            "route_reason": "matches_context_resolution_lane",
            "url": "https://e/3",
        },
    ]
    with input_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    payload = build_prioritizer_payload(input_path)
    assert payload["manual_review_total"] == 3
    assert payload["queues"]["attack_now"][0]["suggested_target_label"] == "software_engineer"
    assert payload["queues"]["recoverable_with_context"][0]["suggested_target_label"] == "customer_success_manager"

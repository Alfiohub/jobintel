from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json, write_jsonl


CUSTOMER_SUCCESS_PROMOTABLE = [
    re.compile(r"\bonboarding specialist\b", re.IGNORECASE),
    re.compile(r"\bcustomer onboarding specialist\b", re.IGNORECASE),
    re.compile(r"\bsaas onboarding specialist\b", re.IGNORECASE),
    re.compile(r"\bclient retention specialist\b", re.IGNORECASE),
    re.compile(r"\bcustomer adoption(?:\s*&\s*|\s+and\s+)?success\b", re.IGNORECASE),
    re.compile(r"\bservice enablement manager\b.*\bcx\b|\bcx\b.*\bservice enablement manager\b", re.IGNORECASE),
]

CUSTOMER_SUCCESS_REVIEW_ONLY = [
    re.compile(r"\bengagement manager\b", re.IGNORECASE),
]

CUSTOMER_SUCCESS_NEGATIVE = [
    re.compile(r"\bemployee engagement\b", re.IGNORECASE),
    re.compile(r"\btechnical engagement\b", re.IGNORECASE),
    re.compile(r"\bbrandwatch\b", re.IGNORECASE),
]

PROJECT_MANAGER_SERVICES = [
    re.compile(r"\bdelivery excellence manager\b", re.IGNORECASE),
    re.compile(r"\bprofessional services manager\b", re.IGNORECASE),
    re.compile(r"\bengagement manager\b", re.IGNORECASE),
    re.compile(r"\bportfolio management\b", re.IGNORECASE),
]

PROJECT_MANAGER_ENGINEERING = [
    re.compile(r"\bproject engineer\b", re.IGNORECASE),
    re.compile(r"\bengineering program support\b", re.IGNORECASE),
    re.compile(r"\bdata center development\b", re.IGNORECASE),
]

ACCOUNT_MANAGER_PARTNER = [
    re.compile(r"\bpartner development manager\b", re.IGNORECASE),
    re.compile(r"\bpartner growth manager\b", re.IGNORECASE),
    re.compile(r"\bpartner experience lead\b", re.IGNORECASE),
    re.compile(r"\bpartner director\b", re.IGNORECASE),
]

ACCOUNT_MANAGER_CLIENT = [
    re.compile(r"\bclient strategist\b", re.IGNORECASE),
    re.compile(r"\bclient strategy\b", re.IGNORECASE),
    re.compile(r"\bclient partnership specialist\b", re.IGNORECASE),
    re.compile(r"\bprovider engagement specialist\b", re.IGNORECASE),
    re.compile(r"\bcharter partnerships manager\b", re.IGNORECASE),
]


def _match_any(title: str, patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(title) for pattern in patterns)


def refine_phase_e11_clusters(joined_path: Path, out_json: Path, out_dir: Path) -> dict[str, Any]:
    rows = read_jsonl(joined_path)
    by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_cluster[str(row.get("context_cluster") or "")].append(row)

    customer_success_promotable = []
    customer_success_review = []
    customer_success_excluded = []
    for row in by_cluster["customer_success_manager"]:
        title = str(row.get("title_clean") or "")
        if _match_any(title, CUSTOMER_SUCCESS_NEGATIVE):
            customer_success_excluded.append(row)
        elif _match_any(title, CUSTOMER_SUCCESS_PROMOTABLE):
            customer_success_promotable.append(row)
        elif _match_any(title, CUSTOMER_SUCCESS_REVIEW_ONLY):
            customer_success_review.append(row)
        else:
            customer_success_excluded.append(row)

    project_services = []
    project_engineering = []
    project_review = []
    for row in by_cluster["project_manager"]:
        title = str(row.get("title_clean") or "")
        if _match_any(title, PROJECT_MANAGER_ENGINEERING):
            project_engineering.append(row)
        elif _match_any(title, PROJECT_MANAGER_SERVICES):
            project_services.append(row)
        else:
            project_review.append(row)

    account_partner = []
    account_client = []
    account_review = []
    for row in by_cluster["account_manager"]:
        title = str(row.get("title_clean") or "")
        if _match_any(title, ACCOUNT_MANAGER_PARTNER):
            account_partner.append(row)
        elif _match_any(title, ACCOUNT_MANAGER_CLIENT):
            account_client.append(row)
        else:
            account_review.append(row)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "phase_e11_customer_success_promotable_v1.jsonl", customer_success_promotable)
    write_jsonl(out_dir / "phase_e11_customer_success_review_only_v1.jsonl", customer_success_review)
    write_jsonl(out_dir / "phase_e11_project_services_v1.jsonl", project_services)
    write_jsonl(out_dir / "phase_e11_project_engineering_v1.jsonl", project_engineering)
    write_jsonl(out_dir / "phase_e11_account_partner_v1.jsonl", account_partner)
    write_jsonl(out_dir / "phase_e11_account_client_v1.jsonl", account_client)

    payload = {
        "customer_success_manager": {
            "promotable_count": len(customer_success_promotable),
            "review_only_count": len(customer_success_review),
            "excluded_count": len(customer_success_excluded),
            "top_promotable_titles": dict(Counter(r["title_clean"] for r in customer_success_promotable).most_common(12)),
            "top_review_titles": dict(Counter(r["title_clean"] for r in customer_success_review).most_common(12)),
            "decision": "ready_for_shadow_scoring_on_promotable_subset",
        },
        "project_manager": {
            "services_delivery_count": len(project_services),
            "engineering_delivery_count": len(project_engineering),
            "review_only_count": len(project_review),
            "top_services_titles": dict(Counter(r["title_clean"] for r in project_services).most_common(12)),
            "top_engineering_titles": dict(Counter(r["title_clean"] for r in project_engineering).most_common(12)),
            "decision": "split_before_any_context_gate",
        },
        "account_manager": {
            "partner_count": len(account_partner),
            "client_count": len(account_client),
            "review_only_count": len(account_review),
            "top_partner_titles": dict(Counter(r["title_clean"] for r in account_partner).most_common(12)),
            "top_client_titles": dict(Counter(r["title_clean"] for r in account_client).most_common(12)),
            "decision": "reviewer_first_keep_context",
        },
    }
    write_json(out_json, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    result = refine_phase_e11_clusters(
        joined_path=reports / "phase_e11_context_join_v1.jsonl",
        out_json=reports / "phase_e11_cluster_refinement_v1.json",
        out_dir=reports,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

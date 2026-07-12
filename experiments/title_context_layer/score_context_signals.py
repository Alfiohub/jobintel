from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, tokenize, write_json


CLUSTER_SIGNAL_MAP: dict[str, dict[str, list[str]]] = {
    "Onboarding Specialist": {
        "customer_success": ["customer", "client", "adoption", "merchant", "implementation", "onboarding"],
        "people_operations": ["employee", "hire", "new hire", "hr", "hris", "employee lifecycle"],
        "compliance_risk": ["kyc", "aml", "compliance", "due diligence", "verification"],
    },
    "Implementation Engineer": {
        "software_engineering": ["api", "integration", "deployment", "identity", "javascript"],
        "customer_success": ["merchant", "customer", "client", "onboarding", "solutions"],
        "sales": ["pre sales", "sales", "account manager", "merchant"],
    },
    "Partner Manager": {
        "sales": ["channel", "reseller", "partner ecosystem", "pipeline", "bookings", "sales"],
        "people_operations": ["talent", "people partner", "hr business partner", "employee"],
        "operations": ["ecosystem", "enablement", "alliances", "program"],
    },
    "Producer": {
        "content": ["content", "news", "broadcast", "creative", "video", "campaign"],
        "software_engineering": ["game", "jira", "scrum", "engineers", "technical"],
        "operations": ["project manage", "workflows", "stakeholders"],
    },
    "Designer": {
        "design": ["ux", "ui", "brand", "graphic", "motion", "visual", "figma"],
        "marketing": ["campaign", "social media", "display ads", "email campaigns", "collateral"],
        "product_management": ["design systems", "component libraries", "product"],
    },
    "Operations Analyst": {
        "operations": ["operations", "program manager", "admissions process", "enrollment", "stakeholders"],
        "data_analytics": ["analytics", "excel", "sql", "reporting", "pipeline monitoring"],
        "compliance_risk": ["security", "risk", "control"],
    },
}


def _score_text(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def score_context_signals(joined_path: Path, out_path: Path) -> dict[str, Any]:
    rows = read_jsonl(joined_path)
    scored_rows: list[dict[str, Any]] = []
    aggregate: dict[str, Counter[str]] = {}

    for row in rows:
        title = str(row.get("title_clean") or "")
        text = str(row.get("context_text") or "")
        family_map = CLUSTER_SIGNAL_MAP.get(title, {})
        family_scores = {family: _score_text(text, keywords) for family, keywords in family_map.items()}
        top_family = max(family_scores.items(), key=lambda x: x[1])[0] if family_scores else None
        top_score = max(family_scores.values()) if family_scores else 0
        confidence = "high" if top_score >= 4 else "medium" if top_score >= 2 else "low"
        scored_rows.append(
            {
                "url": row.get("url"),
                "title_clean": title,
                "company_name": row.get("company_name"),
                "departments_raw": row.get("departments_raw"),
                "skills": row.get("skills"),
                "seniority": row.get("seniority"),
                "employment_type": row.get("employment_type"),
                "family_scores": family_scores,
                "top_context_family": top_family,
                "top_context_score": top_score,
                "context_confidence": confidence,
            }
        )
        aggregate.setdefault(title, Counter())
        if top_family:
            aggregate[title][top_family] += 1

    payload = {
        "rows_scored": len(scored_rows),
        "rows": scored_rows,
        "aggregate_top_family_counts": {title: dict(counter) for title, counter in aggregate.items()},
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    result = score_context_signals(
        joined_path=reports / "context_join_v1.jsonl",
        out_path=reports / "context_signal_scores_v1.json",
    )
    print({"rows_scored": result["rows_scored"]})

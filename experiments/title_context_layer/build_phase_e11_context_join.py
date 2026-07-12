from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, tokenize, write_json, write_jsonl


TEXT_FIELDS = ["description_clean", "requirements_clean", "responsibilities_clean"]

CLUSTER_PATTERNS: dict[str, list[tuple[str, str]]] = {
    "customer_success_manager": [
        ("onboarding_specialist", r"\bonboarding specialist\b"),
        ("retention_specialist", r"\bclient retention specialist\b"),
        ("customer_adoption_success", r"\bcustomer adoption(?:\s*&\s*|\s+and\s+)?success\b"),
        ("service_enablement_cx", r"\bservice enablement manager\b.*\bcx\b|\bcx\b.*\bservice enablement manager\b"),
        ("gtm_onboarding_specialist", r"\bgtm onboarding specialist\b"),
        ("customer_engagement_manager", r"\bengagement manager\b"),
    ],
    "account_manager": [
        ("partner_development_manager", r"\bpartner development manager\b"),
        ("partner_growth_manager", r"\bpartner growth manager\b"),
        ("partner_experience_lead", r"\bpartner experience lead\b"),
        ("client_strategist", r"\bclient strategist\b"),
        ("client_strategy_manager", r"\bmanager client strategy\b|\bmanager, client strategy\b"),
        ("client_partnership_specialist", r"\bclient partnership specialist\b"),
        ("provider_engagement_specialist", r"\bprovider engagement specialist\b"),
        ("partner_director", r"\bpartner director\b"),
        ("charter_partnerships_manager", r"\bcharter partnerships manager\b"),
    ],
    "project_manager": [
        ("engagement_manager", r"\bengagement manager\b"),
        ("delivery_excellence_manager", r"\bdelivery excellence manager\b"),
        ("professional_services_manager", r"\bprofessional services manager\b"),
        ("engineering_program_support", r"\bengineering program support\b"),
        ("portfolio_management", r"\bportfolio management\b"),
        ("project_engineer", r"\bproject engineer\b"),
        ("data_center_development", r"\bdata center development\b"),
    ],
}


def _context_text(row: dict[str, Any]) -> str:
    return " ".join(str(row.get(field) or "") for field in TEXT_FIELDS).strip()


def _compile_patterns() -> dict[str, list[tuple[str, re.Pattern[str]]]]:
    compiled: dict[str, list[tuple[str, re.Pattern[str]]]] = {}
    for cluster, specs in CLUSTER_PATTERNS.items():
        compiled[cluster] = [(name, re.compile(pattern, re.IGNORECASE)) for name, pattern in specs]
    return compiled


def build_phase_e11_context_join(
    titled_path: Path,
    extracted_path: Path,
    out_jsonl: Path,
    out_summary: Path,
    out_customer_success_jsonl: Path,
) -> dict[str, Any]:
    extracted_rows = {row["url"]: row for row in read_jsonl(extracted_path) if row.get("url")}
    compiled = _compile_patterns()

    joined_rows: list[dict[str, Any]] = []
    customer_success_rows: list[dict[str, Any]] = []
    counts_by_cluster = {cluster: 0 for cluster in compiled}
    counts_by_pattern: dict[str, dict[str, int]] = {
        cluster: {pattern_name: 0 for pattern_name, _ in specs} for cluster, specs in compiled.items()
    }

    for row in read_jsonl(titled_path):
        if row.get("classification_status") != "other":
            continue
        title_clean = str(row.get("title_clean") or "")

        matched_cluster = None
        matched_pattern = None
        for cluster, specs in compiled.items():
            for pattern_name, pattern in specs:
                if pattern.search(title_clean):
                    matched_cluster = cluster
                    matched_pattern = pattern_name
                    break
            if matched_cluster:
                break
        if not matched_cluster:
            continue

        extracted = extracted_rows.get(str(row.get("url") or ""), {})
        context_text = _context_text(extracted)
        joined = {
            "url": row.get("url"),
            "company_name": row.get("company_name"),
            "title_clean": title_clean,
            "current_normalized_title": row.get("normalized_title"),
            "current_role_family": row.get("role_family"),
            "context_cluster": matched_cluster,
            "context_title_pattern": matched_pattern,
            "departments_raw": extracted.get("departments_raw"),
            "skills": extracted.get("skills") or [],
            "seniority": extracted.get("seniority"),
            "employment_type": extracted.get("employment_type"),
            "tags": extracted.get("tags") or {},
            "context_text": context_text,
            "context_token_count": len(tokenize(context_text)),
            "description_clean": extracted.get("description_clean"),
            "requirements_clean": extracted.get("requirements_clean"),
            "responsibilities_clean": extracted.get("responsibilities_clean"),
        }
        joined_rows.append(joined)
        counts_by_cluster[matched_cluster] += 1
        counts_by_pattern[matched_cluster][matched_pattern] += 1
        if matched_cluster == "customer_success_manager":
            customer_success_rows.append(joined)

    summary = {
        "titled_path": str(titled_path.relative_to(repo_root())),
        "extracted_path": str(extracted_path.relative_to(repo_root())),
        "joined_rows": len(joined_rows),
        "counts_by_cluster": counts_by_cluster,
        "counts_by_pattern": counts_by_pattern,
        "customer_success_rows": len(customer_success_rows),
    }

    write_jsonl(out_jsonl, joined_rows)
    write_jsonl(out_customer_success_jsonl, customer_success_rows)
    write_json(out_summary, summary)
    return summary


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    result = build_phase_e11_context_join(
        titled_path=root / "data/jobs/jobs_titled_en_recovery_v58_recoverability_batch.jsonl",
        extracted_path=root / "data/jobs/jobs_extracted_en.jsonl",
        out_jsonl=reports / "phase_e11_context_join_v1.jsonl",
        out_summary=reports / "phase_e11_context_join_v1_summary.json",
        out_customer_success_jsonl=reports / "phase_e11_customer_success_candidates_v1.jsonl",
    )
    print(result)

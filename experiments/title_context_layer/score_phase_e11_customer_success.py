from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import read_jsonl, repo_root, write_json


DEPARTMENT_POSITIVE = [
    "customer success",
    "client success",
    "customer onboarding",
    "onboarding",
    "getting started",
    "launch services",
    "customer operations",
    "customer service",
    "services",
]

DEPARTMENT_NEGATIVE = [
    "business management",
    "sales & trading",
    "data operations",
    "finops",
]

TEXT_POSITIVE = [
    "customer",
    "client",
    "onboarding",
    "adoption",
    "implementation",
    "launch",
    "go live",
    "time to value",
    "value realization",
    "platform",
    "product",
    "saas",
    "training",
]

TEXT_NEGATIVE = [
    "vendor",
    "counterparty",
    "procurement",
    "listed derivatives",
    "sales and trading",
    "patient",
    "clinical",
    "data operations",
    "compliance",
    "aml",
    "kyc",
]


def _text_blob(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(field) or "")
        for field in ("description_clean", "requirements_clean", "responsibilities_clean")
    ).lower()


def _department_blob(row: dict[str, Any]) -> str:
    return " ".join(str(item.get("name") or "") for item in (row.get("departments_raw") or [])).lower()


def _hits(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in text]


def _decide(row: dict[str, Any]) -> dict[str, Any]:
    title = str(row.get("title_clean") or "")
    dept = _department_blob(row)
    text = _text_blob(row)

    dept_pos = _hits(dept, DEPARTMENT_POSITIVE)
    dept_neg = _hits(dept, DEPARTMENT_NEGATIVE)
    text_pos = _hits(text, TEXT_POSITIVE)
    text_neg = _hits(text, TEXT_NEGATIVE)

    score = len(dept_pos) * 2 + len(text_pos) - len(dept_neg) * 2 - len(text_neg) * 2
    evidence = dept_pos + [t for t in text_pos if t not in dept_pos]
    exclusions = dept_neg + [t for t in text_neg if t not in dept_neg]

    hard_exclude = bool(text_neg or dept_neg)
    if "vendor" in exclusions or "counterparty" in exclusions or "sales & trading" in exclusions:
        decision = "exclude"
    elif hard_exclude and score < 4:
        decision = "exclude"
    elif "engagement manager" in title.lower():
        decision = "review_only"
    elif score >= 5 and (
        "onboarding" in title.lower()
        or "retention" in title.lower()
        or "adoption" in title.lower()
        or "enablement" in title.lower()
    ):
        decision = "shadow_match"
    else:
        decision = "review_only"

    return {
        "url": row.get("url"),
        "title_clean": title,
        "company_name": row.get("company_name"),
        "decision": decision,
        "score": score,
        "evidence_hits": evidence,
        "exclusion_hits": exclusions,
        "normalized_title": "customer_success_manager" if decision == "shadow_match" else None,
        "role_family": "customer_success" if decision == "shadow_match" else None,
    }


def score_phase_e11_customer_success(in_path: Path, out_json: Path) -> dict[str, Any]:
    rows = read_jsonl(in_path)
    scored = [_decide(row) for row in rows]
    counts = Counter(item["decision"] for item in scored)
    top_shadow_titles = Counter(item["title_clean"] for item in scored if item["decision"] == "shadow_match")
    top_review_titles = Counter(item["title_clean"] for item in scored if item["decision"] == "review_only")
    top_excluded_titles = Counter(item["title_clean"] for item in scored if item["decision"] == "exclude")

    payload = {
        "input_path": str(in_path.relative_to(repo_root())),
        "rows_scored": len(scored),
        "decision_counts": dict(counts),
        "top_shadow_titles": dict(top_shadow_titles.most_common(12)),
        "top_review_titles": dict(top_review_titles.most_common(12)),
        "top_excluded_titles": dict(top_excluded_titles.most_common(12)),
        "sample_shadow_matches": [item for item in scored if item["decision"] == "shadow_match"][:12],
        "sample_exclusions": [item for item in scored if item["decision"] == "exclude"][:12],
    }
    write_json(out_json, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/title_context_layer/reports"
    result = score_phase_e11_customer_success(
        in_path=reports / "phase_e11_customer_success_promotable_v1.jsonl",
        out_json=reports / "phase_e11_customer_success_scoring_v1.json",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from experiments.title_semantic_layer.common import normalize_title, read_json, read_jsonl, repo_root, tokenize, write_json, write_jsonl
from experiments.title_semantic_layer.semantic_retrieval import (
    _build_internal_candidates,
    _topk,
)


NOISE_PATTERNS = (
    "general application",
    "join our talent community",
    "don t see what you re looking for",
    "general interest",
    "talent community",
)

GENERIC_KEEP_OTHER = {
    "engineer",
    "designer",
    "producer",
    "manager",
    "analyst",
    "architect",
    "consultant",
    "specialist",
}

HR_TERMS = {"employee", "new hire", "hr", "hris", "recruiting", "talent", "benefits", "payroll"}
COMPLIANCE_TERMS = {"kyc", "aml", "verification", "due diligence", "underwriting", "compliance", "regulatory"}
CUSTOMER_SUCCESS_TERMS = {
    "customer",
    "client",
    "merchant",
    "implementation",
    "onboarding",
    "adoption",
    "platform",
    "account management",
    "revops",
}
CONTENT_TERMS = {"content", "news", "broadcast", "creative", "video", "campaign", "editorial", "media"}
FINANCE_TERMS = {"finance", "financial", "forecast", "budget", "fp&a", "accounting", "variance"}
SALES_TERMS = {"sales", "account executive", "pipeline", "quota", "business development", "territory"}
IT_TERMS = {"security", "devops", "software", "platform", "cloud", "administrator", "architect", "technical"}


def _text_blob(row: dict[str, Any]) -> str:
    return " ".join(
        str(row.get(k) or "")
        for k in [
            "title_clean",
            "description_excerpt",
            "responsibilities_excerpt",
            "requirements_excerpt",
            "departments",
            "skills",
        ]
    ).lower()


def _term_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(term for term in terms if term in text)


def _bucket_and_target(row: dict[str, Any], retrieval: dict[str, Any]) -> tuple[str, str | None, str | None, str, list[str], str]:
    title = str(row.get("title_clean") or "")
    norm_title = normalize_title(title)
    text = _text_blob(row)
    toks = tokenize(norm_title)

    top_internal = (retrieval.get("top_internal") or [{}])[0]
    i_score = float(top_internal.get("score", 0.0) or 0.0)
    target_label = top_internal.get("normalized_title")
    target_family = top_internal.get("role_family")

    evidence: list[str] = []

    if any(p in norm_title for p in NOISE_PATTERNS):
        return "noise_or_non_role", None, None, "high", ["noise_pattern"], "Generic application/community pattern."

    if norm_title in {"", "other"}:
        return "noise_or_non_role", None, None, "high", ["empty_title"], "Missing usable role title."

    if len(toks) == 1 and toks[0] in GENERIC_KEEP_OTHER:
        return "keep_other_by_policy", None, None, "high", [toks[0]], "Single generic title token is too broad."

    hr_hits = _term_hits(text, HR_TERMS)
    compliance_hits = _term_hits(text, COMPLIANCE_TERMS)
    cs_hits = _term_hits(text, CUSTOMER_SUCCESS_TERMS)
    content_hits = _term_hits(text, CONTENT_TERMS)
    finance_hits = _term_hits(text, FINANCE_TERMS)
    sales_hits = _term_hits(text, SALES_TERMS)
    it_hits = _term_hits(text, IT_TERMS)

    if "onboarding specialist" in norm_title:
        if len(cs_hits) >= 3 and not hr_hits[:2] and len(compliance_hits) <= 1:
            return "recoverable_with_context", "customer_success_manager", "customer_success", "medium", cs_hits[:6], "Ambiguous title but context strongly indicates customer onboarding."
        if hr_hits or len(compliance_hits) >= 2:
            evidence = (hr_hits + compliance_hits)[:6]
            return "keep_other_by_policy", None, None, "medium", evidence, "Onboarding title crosses HR/compliance boundaries."

    if norm_title == "producer":
        if len(content_hits) >= 2:
            return "recoverable_with_context", "content_producer", "content", "medium", content_hits[:6], "Producer becomes clear only with media/content context."
        return "keep_other_by_policy", None, None, "medium", ["producer"], "Bare producer remains cross-domain."

    if "data science manager" in norm_title:
        return "taxonomy_gap", "data_science_manager", "data_science", "medium", ["data science", "manager"], "Recurring managerial DS role likely needs explicit taxonomy decision."

    if "sales representative" in norm_title:
        return "taxonomy_gap", "sales_representative", "sales", "medium", ["sales representative"], "Generic sales role lacks a clean current canonical destination."

    if "procurement manager" in norm_title:
        return "taxonomy_gap", "procurement_manager", "logistics", "medium", ["procurement", "manager"], "Procurement leadership appears real but current taxonomy is too coarse."

    if i_score >= 0.86 and target_label and target_family:
        evidence = [f"internal:{target_label}", f"score:{i_score:.2f}"]
        if finance_hits:
            evidence.extend(finance_hits[:3])
        elif sales_hits:
            evidence.extend(sales_hits[:3])
        elif it_hits:
            evidence.extend(it_hits[:3])
        return "recoverable_now", target_label, target_family, "high", evidence[:6], "Top internal candidate is strong enough for a narrow deterministic rule review."

    if i_score >= 0.76 and target_label and target_family:
        evidence = [f"internal:{target_label}", f"score:{i_score:.2f}"]
        if cs_hits or content_hits or finance_hits or sales_hits or it_hits:
            evidence.extend((cs_hits + content_hits + finance_hits + sales_hits + it_hits)[:4])
            return "recoverable_with_context", target_label, target_family, "medium", evidence[:6], "Title likely recoverable, but context carries part of the disambiguation load."
        return "recoverable_now", target_label, target_family, "medium", evidence[:6], "Reasonably strong internal match with limited ambiguity."

    if any(term in norm_title for term in ("manager", "analyst", "specialist", "architect", "engineer", "partner")):
        return "keep_other_by_policy", None, None, "medium", toks[:4], "Generic cross-domain title with insufficient stable evidence."

    return "keep_other_by_policy", None, None, "low", toks[:4], "Insufficient evidence for a safe target."


def annotate_sample(sample_path: Path, corpus_path: Path, out_jsonl: Path, out_summary: Path) -> dict[str, Any]:
    internal_corpus = read_json(corpus_path)
    internal_candidates = _build_internal_candidates(internal_corpus)

    annotations: list[dict[str, Any]] = []
    bucket_counts: Counter[str] = Counter()

    for row in read_jsonl(sample_path):
        query = str(row.get("title_clean") or "")
        retrieval = {
            "top_internal": _topk(query, internal_candidates, k=3),
            "top_esco": [],
            "top_onet": [],
        }
        bucket, label, family, confidence, evidence, reason = _bucket_and_target(row, retrieval)
        annotations.append(
            {
                "sample_id": row["sample_id"],
                "audit_bucket": bucket,
                "suggested_target_label": label,
                "suggested_role_family": family,
                "confidence": confidence,
                "reasoning_summary": reason,
                "evidence_terms": evidence,
                "risk_notes": "Draft auto-annotation for review.",
                "top_internal_candidate": retrieval["top_internal"][0] if retrieval["top_internal"] else None,
                "top_esco_candidate": retrieval["top_esco"][0] if retrieval["top_esco"] else None,
                "top_onet_candidate": retrieval["top_onet"][0] if retrieval["top_onet"] else None,
            }
        )
        bucket_counts[bucket] += 1

    summary = {
        "input_sample": str(sample_path.relative_to(repo_root())),
        "annotations_output": str(out_jsonl.relative_to(repo_root())),
        "sample_size": len(annotations),
        "bucket_counts": dict(bucket_counts),
    }
    write_jsonl(out_jsonl, annotations)
    write_json(out_summary, summary)
    return summary


if __name__ == "__main__":
    root = repo_root()
    reports = root / "experiments/residual_audit/reports"
    result = annotate_sample(
        sample_path=reports / "residual_audit_sample_v1.jsonl",
        corpus_path=root / "experiments/title_semantic_layer/reports/internal_title_corpus.json",
        out_jsonl=reports / "residual_audit_annotations_draft_v1.jsonl",
        out_summary=reports / "residual_audit_annotations_draft_v1_summary.json",
    )
    print(result)

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from .common import AMBIGUOUS_TOKENS, normalize_title, read_json, repo_root, tokenize, write_json


NOISE_PATTERNS = (
    "general application",
    "join our talent community",
    "don t see what you re looking for",
    "general interest",
)

HARD_REJECT_PATTERNS = (
    "general manager",
    "restaurant manager",
    "office manager",
    "business analyst",
    "quantitative researcher",
    "producer",
    "client partner",
    "implementation engineer",
    "chief of staff",
    "payroll specialist",
    "principal engineer",
    "senior engineer",
)

SAFE_ANCHORS = (
    "mortgage loan officer",
    "community health worker",
    "data entry specialist",
    "salesforce administrator",
    "intelligence operations integrator",
    "machine learning researcher",
)


def _support_strength(esco_score: float, onet_score: float) -> str:
    best = max(esco_score, onet_score)
    if best >= 0.84:
        return "strong"
    if best >= 0.74:
        return "medium"
    if best >= 0.64:
        return "weak"
    return "none"


def _risk_level(title: str, internal_score: float) -> str:
    t = normalize_title(title)
    toks = set(tokenize(t))
    generic_overlap = len(toks & AMBIGUOUS_TOKENS)
    if any(p in t for p in HARD_REJECT_PATTERNS):
        return "high"
    if any(n in t for n in NOISE_PATTERNS):
        return "high"
    if generic_overlap >= 2 and internal_score < 0.74:
        return "high"
    if generic_overlap >= 1 and internal_score < 0.78:
        return "medium"
    if internal_score < 0.70:
        return "medium"
    return "low"


def _suggest_action(title: str, risk: str, internal_score: float, support: str) -> str:
    t = normalize_title(title)
    if any(p in t for p in HARD_REJECT_PATTERNS):
        return "keep_other_for_now"
    if any(n in t for n in NOISE_PATTERNS):
        return "noise_or_non_role"
    if risk == "low" and any(a in t for a in SAFE_ANCHORS) and internal_score >= 0.80 and support in {"strong", "medium"}:
        return "safe_rule_candidate"
    if risk in {"low", "medium"} and internal_score >= 0.76:
        return "needs_tighter_rule"
    if internal_score >= 0.70 and support == "strong":
        return "taxonomy_gap"
    if internal_score >= 0.64:
        return "semantic_layer_candidate"
    return "keep_other_for_now"


def rank_candidates(retrieval_path: Path, out_path: Path, sample_size: int = 60) -> dict[str, Any]:
    retrieval = read_json(retrieval_path)
    ranked_rows = []

    for row in retrieval.get("retrieval_rows", []):
        top_internal = (row.get("top_internal") or [{}])[0]
        top_esco = (row.get("top_esco") or [{}])[0]
        top_onet = (row.get("top_onet") or [{}])[0]

        i_score = float(top_internal.get("score", 0.0) or 0.0)
        e_score = float(top_esco.get("score", 0.0) or 0.0)
        o_score = float(top_onet.get("score", 0.0) or 0.0)

        support = _support_strength(e_score, o_score)
        risk = _risk_level(row.get("title", ""), i_score)
        action = _suggest_action(row.get("title", ""), risk, i_score, support)

        ranked_rows.append(
            {
                "title": row.get("title", ""),
                "count": int(row.get("count", 0)),
                "top_internal": top_internal,
                "top_esco": top_esco,
                "top_onet": top_onet,
                "support_strength": support,
                "overmatch_risk": risk,
                "suggested_action": action,
            }
        )

    ranked_rows.sort(key=lambda x: (x["count"], x.get("top_internal", {}).get("score", 0.0)), reverse=True)

    category_volume = Counter()
    for row in ranked_rows:
        category_volume[row["suggested_action"]] += row["count"]

    payload = {
        "titles_considered": len(ranked_rows),
        "category_volume": dict(category_volume),
        "ranked_rows": ranked_rows,
        "sample_rows": ranked_rows[:sample_size],
    }
    write_json(out_path, payload)
    return payload


if __name__ == "__main__":
    root = repo_root()
    out = root / "experiments/title_semantic_layer/reports/ranked_candidates.json"
    r = rank_candidates(
        retrieval_path=root / "experiments/title_semantic_layer/reports/semantic_retrieval.json",
        out_path=out,
    )
    print(f"ranked_candidates -> {out} ({r['titles_considered']} titles)")

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common import normalize_title, read_json, repo_root, tokenize, write_json

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None


INPUT_ACTIONS = {"semantic_layer_candidate", "needs_tighter_rule", "taxonomy_gap"}

NOISE_PATTERNS = {
    "general application",
    "general interest",
    "join our talent community",
    "don t see what you re looking for",
}

HIGH_RISK_PATTERNS = {
    "general manager",
    "restaurant manager",
    "business analyst",
    "quantitative researcher",
    "producer",
    "client partner",
    "implementation engineer",
    "chief of staff",
    "payroll specialist",
    "principal engineer",
    "senior engineer",
}

HIGH_RISK_RAW_PATTERNS = {
    "principal engineer",
    "senior engineer",
    "staff engineer",
    "general manager",
    "restaurant manager",
    "business analyst",
    "quantitative researcher",
    "client partner",
    "implementation engineer",
    "chief of staff",
}

SAFE_ANCHORS = {
    "mortgage loan officer",
    "community health worker",
    "data entry specialist",
    "salesforce administrator",
    "intelligence operations integrator",
    "machine learning researcher",
    "product support specialist",
}

GENERIC_TOKENS = {"manager", "analyst", "specialist", "engineer", "partner", "consultant", "coordinator"}
GENERIC_CLUSTER_NAMES = {"engineer", "designer", "production", "operations", "architect", "consultant"}
SHORTLIST_KEYWORDS = {
    "mortgage loan officer",
    "community health worker",
    "data entry specialist",
    "salesforce administrator",
    "firmware engineer",
    "product support specialist",
    "onboarding specialist",
    "intelligence operations integrator",
    "machine learning researcher",
}

ANCHOR_EXPECTED_LABELS = {
    "salesforce administrator": {"it_support_specialist", "systems_engineer", "operations_specialist"},
    "onboarding specialist": {"operations_specialist", "customer_service_specialist", "customer_success_manager"},
    "product support specialist": {"it_support_specialist", "customer_service_specialist"},
    "firmware engineer": {"software_engineer", "electrical_engineer", "mechanical_engineer"},
    "mortgage loan officer": {"account_executive", "account_manager", "sales_manager"},
}


@dataclass
class Cluster:
    cluster_name: str
    rows: list[dict[str, Any]]


def _sim(a: str, b: str) -> float:
    if fuzz is None:
        ta, tb = set(tokenize(a)), set(tokenize(b))
        if not ta or not tb:
            return 0.0
        return len(ta & tb) / len(ta | tb)
    return float(fuzz.token_sort_ratio(a, b)) / 100.0


def _cluster_rows(rows: list[dict[str, Any]], threshold: float = 0.9) -> list[Cluster]:
    seed_rows = sorted(rows, key=lambda r: int(r.get("count", 0)), reverse=True)
    clusters: list[Cluster] = []
    used: set[int] = set()

    for i, seed in enumerate(seed_rows):
        if i in used:
            continue
        seed_norm = normalize_title(seed.get("title", ""))
        group = [seed]
        used.add(i)
        for j in range(i + 1, len(seed_rows)):
            if j in used:
                continue
            cand = seed_rows[j]
            cand_norm = normalize_title(cand.get("title", ""))
            if _sim(seed_norm, cand_norm) >= threshold:
                group.append(cand)
                used.add(j)
        cluster_name = seed_norm.replace(" ", "_")[:90] or "empty_title"
        clusters.append(Cluster(cluster_name=cluster_name, rows=group))

    return clusters


def _weighted_mean(vals: list[tuple[float, int]]) -> float:
    num = sum(v * w for v, w in vals)
    den = sum(w for _, w in vals)
    return (num / den) if den else 0.0


def _support_strength(esco: float, onet: float) -> str:
    mx = max(esco, onet)
    if mx >= 0.84:
        return "strong"
    if mx >= 0.74:
        return "medium"
    if mx >= 0.64:
        return "weak"
    return "none"


def _semantic_confidence(internal: float, esco: float, onet: float, ambiguity_penalty: float) -> float:
    # Transparent weighted reviewer score
    support_bonus = 0.08 if _support_strength(esco, onet) == "strong" else 0.04 if _support_strength(esco, onet) == "medium" else 0.0
    agreement_bonus = 0.05 if (esco >= 0.72 and onet >= 0.72) else 0.0
    score = 0.55 * internal + 0.225 * esco + 0.225 * onet + support_bonus + agreement_bonus - ambiguity_penalty
    return max(0.0, min(1.0, score))


def _risk(raw_name: str, norm_name: str, internal_score: float) -> str:
    if any(p in raw_name for p in HIGH_RISK_RAW_PATTERNS):
        return "high"
    if any(p in norm_name for p in NOISE_PATTERNS):
        return "high"
    if any(p in norm_name for p in HIGH_RISK_PATTERNS):
        return "high"
    if norm_name in GENERIC_CLUSTER_NAMES:
        return "high"
    toks = set(tokenize(norm_name))
    generic = len(toks & GENERIC_TOKENS)
    if generic >= 2 and internal_score < 0.80:
        return "high"
    if generic >= 1 and internal_score < 0.78:
        return "medium"
    return "low"


def _confidence_label(v: float) -> str:
    if v >= 0.78:
        return "high"
    if v >= 0.62:
        return "medium"
    return "low"


def _verdict(
    raw_name: str,
    norm_name: str,
    conf: float,
    risk: str,
    internal_score: float,
    support_strength: str,
    internal_label: str,
) -> str:
    if any(p in raw_name for p in HIGH_RISK_RAW_PATTERNS):
        return "keep_other_for_now"
    if any(p in norm_name for p in NOISE_PATTERNS):
        return "noise_or_non_role"
    if any(p in norm_name for p in HIGH_RISK_PATTERNS):
        return "keep_other_for_now"
    for anchor, allowed_labels in ANCHOR_EXPECTED_LABELS.items():
        if anchor in raw_name and internal_label not in allowed_labels:
            return "needs_taxonomy_decision"

    if conf >= 0.78 and risk == "low" and (support_strength in {"strong", "medium"} or any(a in norm_name for a in SAFE_ANCHORS)):
        return "promote_safe"
    if conf >= 0.68 and risk in {"low", "medium"}:
        return "promote_with_tighter_rule"
    if conf >= 0.62 and support_strength == "strong" and internal_score < 0.65:
        return "needs_taxonomy_decision"
    return "keep_other_for_now"


def run_reviewer_safe_batch_generation(root: Path) -> dict[str, Any]:
    ranked_path = root / "experiments/title_semantic_layer/reports/ranked_candidates.json"
    phase_path = root / "experiments/title_semantic_layer/reports/phase_e_bootstrap_report.json"

    ranked = read_json(ranked_path)
    phase = read_json(phase_path)

    base = phase["baseline"]

    filtered_rows = [r for r in ranked.get("ranked_rows", []) if r.get("suggested_action") in INPUT_ACTIONS]
    clusters = _cluster_rows(filtered_rows, threshold=0.9)

    reviewed_clusters = []
    convergence_high = 0
    conflict_count = 0
    keep_other_count = 0

    for cl in clusters:
        total_volume = sum(int(r.get("count", 0)) for r in cl.rows)
        rep_titles = sorted(
            [{"title": r.get("title", ""), "count": int(r.get("count", 0))} for r in cl.rows],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        top_internal = cl.rows[0].get("top_internal", {})
        top_esco = cl.rows[0].get("top_esco", {})
        top_onet = cl.rows[0].get("top_onet", {})

        internal_score = _weighted_mean([(float(r.get("top_internal", {}).get("score", 0.0)), int(r.get("count", 0))) for r in cl.rows])
        esco_score = _weighted_mean([(float(r.get("top_esco", {}).get("score", 0.0)), int(r.get("count", 0))) for r in cl.rows])
        onet_score = _weighted_mean([(float(r.get("top_onet", {}).get("score", 0.0)), int(r.get("count", 0))) for r in cl.rows])

        rep0 = rep_titles[0]["title"] if rep_titles else cl.cluster_name.replace("_", " ")
        raw_name = str(rep0).lower().strip()
        norm_name = normalize_title(rep0)

        ambiguity_penalty = (
            0.15
            if any(p in raw_name for p in HIGH_RISK_RAW_PATTERNS)
            else 0.12
            if any(p in norm_name for p in HIGH_RISK_PATTERNS) or norm_name in GENERIC_CLUSTER_NAMES
            else 0.05
            if any(tok in tokenize(norm_name) for tok in GENERIC_TOKENS)
            else 0.0
        )
        conf_val = _semantic_confidence(internal_score, esco_score, onet_score, ambiguity_penalty)
        conf_label = _confidence_label(conf_val)

        risk = _risk(raw_name, norm_name, internal_score)
        support = _support_strength(esco_score, onet_score)
        verdict = _verdict(
            raw_name,
            norm_name,
            conf_val,
            risk,
            internal_score,
            support,
            str(top_internal.get("normalized_title", "")),
        )

        if esco_score >= 0.74 and onet_score >= 0.74:
            convergence_high += 1
        if abs(esco_score - onet_score) >= 0.22 or (max(esco_score, onet_score) >= 0.82 and internal_score < 0.62):
            conflict_count += 1
        if verdict == "keep_other_for_now":
            keep_other_count += 1

        reviewed_clusters.append(
            {
                "cluster_name": cl.cluster_name,
                "representative_titles": rep_titles,
                "estimated_volume": total_volume,
                "top_internal_candidate": {
                    "label": top_internal.get("normalized_title", ""),
                    "role_family": top_internal.get("role_family", ""),
                    "score": round(internal_score, 4),
                },
                "top_esco_candidate": {
                    "label": top_esco.get("esco_preferred_label", top_esco.get("text", "")),
                    "score": round(esco_score, 4),
                },
                "top_onet_candidate": {
                    "label": top_onet.get("onet_title", top_onet.get("text", "")),
                    "score": round(onet_score, 4),
                },
                "support_strength": support,
                "semantic_confidence": conf_label,
                "semantic_confidence_score": round(conf_val, 4),
                "overmatch_risk": risk,
                "verdict": verdict,
                "recommended_action": "safe_rule_candidate"
                if verdict == "promote_safe"
                else "tight_rule_candidate"
                if verdict == "promote_with_tighter_rule"
                else "taxonomy_gap_do_not_promote_yet"
                if verdict == "needs_taxonomy_decision"
                else "keep_other_for_now",
            }
        )

    reviewed_clusters.sort(key=lambda x: (x["estimated_volume"], x["semantic_confidence_score"]), reverse=True)

    shortlisted = []
    for c in reviewed_clusters:
        if c["verdict"] not in {"promote_safe", "promote_with_tighter_rule", "needs_taxonomy_decision"}:
            continue
        if c["estimated_volume"] < 8:
            continue
        if c["overmatch_risk"] == "high":
            continue
        if c["cluster_name"] in GENERIC_CLUSTER_NAMES:
            continue
        rep_text = " ".join(x["title"].lower() for x in c["representative_titles"][:3])
        if not any(k in rep_text for k in SHORTLIST_KEYWORDS):
            continue
        shortlisted.append(c)
        if len(shortlisted) >= 5:
            break

    taxonomy_gap = [c for c in reviewed_clusters if c["verdict"] == "needs_taxonomy_decision"][:15]
    failures = [c for c in reviewed_clusters if c["verdict"] in {"keep_other_for_now", "noise_or_non_role"}][:15]

    payload = {
        "baseline": {
            "repo": "joballert2",
            "dataset": base["dataset"],
            "rows_total": base["rows_total"],
            "other_baseline": base["other_total"],
            "status": base["status"],
        },
        "semantic_reviewer_summary": {
            "clusters_reviewed": len(reviewed_clusters),
            "clusters_convergence_high": convergence_high,
            "clusters_with_conflict": conflict_count,
            "clusters_keep_other": keep_other_count,
        },
        "reviewer_table": reviewed_clusters,
        "candidate_safe_batch_shortlist": shortlisted,
        "taxonomy_gap_list": taxonomy_gap,
        "failure_modes": failures,
    }

    # recommendation
    if len(shortlisted) >= 3 and all(s["verdict"] != "needs_taxonomy_decision" for s in shortlisted[:3]):
        rec = "ready_for_semantic_assisted_safe_batch"
        reason = "Reviewer found multiple low/medium-low risk clusters with convergent internal+external evidence."
    elif len(taxonomy_gap) >= 3:
        rec = "need_taxonomy_cleanup_before_next_batch"
        reason = "Several meaningful clusters lack a reliable internal target label despite good external support."
    else:
        rec = "semantic_layer_not_yet_actionable"
        reason = "Signal is still mixed and not enough high-confidence clusters pass conservative guardrails."

    payload["final_recommendation"] = {"decision": rec, "reason": reason}

    write_json(root / "experiments/title_semantic_layer/reports/phase_e1_reviewer_safe_batch.json", payload)
    return payload


def render_markdown(payload: dict[str, Any], out_path: Path) -> None:
    lines: list[str] = []
    b = payload["baseline"]
    s = payload["semantic_reviewer_summary"]
    lines.append("# Fase E.1 — Reviewer-Driven Safe Batch Generation")
    lines.append("")
    lines.append("## A. Baseline confirmation")
    lines.append(f"- repo: `{b['repo']}`")
    lines.append(f"- dataset: `{b['dataset']}`")
    lines.append(f"- total rows: `{b['rows_total']}`")
    lines.append(f"- other baseline: `{b['other_baseline']}`")
    lines.append(f"- status: `{b['status']}`")

    lines.append("")
    lines.append("## B. Semantic reviewer summary")
    lines.append(f"- cluster reviewati: `{s['clusters_reviewed']}`")
    lines.append(f"- convergenza alta: `{s['clusters_convergence_high']}`")
    lines.append(f"- cluster con conflitto: `{s['clusters_with_conflict']}`")
    lines.append(f"- cluster keep_other: `{s['clusters_keep_other']}`")

    lines.append("")
    lines.append("## C. Reviewer table (top 30)")
    for i, c in enumerate(payload["reviewer_table"][:30], 1):
        reps = "; ".join(f"{x['title']} ({x['count']})" for x in c["representative_titles"][:3])
        lines.append(
            f"{i}. `{c['cluster_name']}` | reps: {reps} | internal `{c['top_internal_candidate']['label']}` {c['top_internal_candidate']['score']} | ESCO `{c['top_esco_candidate']['label']}` {c['top_esco_candidate']['score']} | O*NET `{c['top_onet_candidate']['label']}` {c['top_onet_candidate']['score']} | conf `{c['semantic_confidence']}` | risk `{c['overmatch_risk']}` | verdict `{c['verdict']}`"
        )

    lines.append("")
    lines.append("## D. Candidate safe batch shortlist (max 5)")
    for i, c in enumerate(payload["candidate_safe_batch_shortlist"], 1):
        reps = "; ".join(f"{x['title']} ({x['count']})" for x in c["representative_titles"][:3])
        lines.append(f"{i}. `{c['cluster_name']}`")
        lines.append(f"- representative titles: {reps}")
        lines.append(f"- suggested target label: `{c['top_internal_candidate']['label']}`")
        lines.append(f"- suggested role family: `{c['top_internal_candidate']['role_family']}`")
        lines.append(f"- support internal/ESCO/O*NET: `{c['top_internal_candidate']['score']}` / `{c['top_esco_candidate']['score']}` / `{c['top_onet_candidate']['score']}`")
        lines.append(f"- risk: `{c['overmatch_risk']}`")
        lines.append(f"- promotion type: `{c['recommended_action']}`")

    lines.append("")
    lines.append("## E. Taxonomy gap list")
    for c in payload["taxonomy_gap_list"]:
        reps = "; ".join(f"{x['title']} ({x['count']})" for x in c["representative_titles"][:2])
        lines.append(
            f"- `{c['cluster_name']}` | reps: {reps} | possible family: `{c['top_internal_candidate']['role_family']}` | why insufficient: internal target confidence not robust enough for safe promotion"
        )

    lines.append("")
    lines.append("## F. Failure modes")
    for c in payload["failure_modes"][:15]:
        reps = "; ".join(f"{x['title']} ({x['count']})" for x in c["representative_titles"][:2])
        lines.append(f"- `{c['cluster_name']}` | reps: {reps} | verdict `{c['verdict']}` | reason: ambiguity/overmatch risk remains high")

    lines.append("")
    lines.append("## G. Final recommendation")
    lines.append(f"- `{payload['final_recommendation']['decision']}`")
    lines.append(f"- reason: {payload['final_recommendation']['reason']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    root = repo_root()
    payload = run_reviewer_safe_batch_generation(root)
    out_md = root / "docs/title_semantic_layer_phase_e1_reviewer.md"
    render_markdown(payload, out_md)
    print(f"report_json=experiments/title_semantic_layer/reports/phase_e1_reviewer_safe_batch.json")
    print(f"report_md=docs/title_semantic_layer_phase_e1_reviewer.md")

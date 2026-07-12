from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from statistics import mean

from common import normalize_title

try:
    from rapidfuzz import fuzz, process
except Exception:  # pragma: no cover
    fuzz = None
    process = None


CLUSTER_DEFS = [
    {
        "cluster_name": "support_engineer_it_core",
        "pattern": r"\b(?:support engineer|application support engineer|cloud support engineer|software support engineer|systems support engineer|production support engineer|infrastructure support engineer|enterprise support engineer|database support engineer|platform support engineer|data center support engineer|tech support engineer|l2 support engineer|l3 support engineer|tier\s*[123]\s*support engineer)\b",
        "suggested_action": "map_to_existing",
        "target_label": "it_support_specialist",
        "target_family": "it_operations",
        "overmatch_risk": "medium",
        "roi": "high",
    },
    {
        "cluster_name": "occupational_therapist_core",
        "pattern": r"\boccupational therapist\b",
        "suggested_action": "add_new_normalized_title",
        "target_label": "occupational_therapist",
        "target_family": "healthcare_clinical",
        "overmatch_risk": "low",
        "roi": "medium",
    },
    {
        "cluster_name": "respiratory_therapist_core",
        "pattern": r"\brespiratory therapist\b",
        "suggested_action": "add_new_normalized_title",
        "target_label": "respiratory_therapist",
        "target_family": "healthcare_clinical",
        "overmatch_risk": "low",
        "roi": "medium",
    },
    {
        "cluster_name": "paralegal_specialty_cluster",
        "pattern": r"\bparalegal\b",
        "suggested_action": "add_new_normalized_title",
        "target_label": "paralegal",
        "target_family": "legal",
        "overmatch_risk": "medium",
        "roi": "medium",
    },
    {
        "cluster_name": "hr_generalist_cluster",
        "pattern": r"\bhr generalist\b|\bhuman resources generalist\b",
        "suggested_action": "add_new_normalized_title",
        "target_label": "hr_generalist",
        "target_family": "people_operations",
        "overmatch_risk": "low",
        "roi": "medium",
    },
    {
        "cluster_name": "implementation_engineer_cluster",
        "pattern": r"\bimplementation engineer\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "medium",
    },
    {
        "cluster_name": "client_partner_cluster",
        "pattern": r"\bclient partner\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
    {
        "cluster_name": "client_success_manager_cluster",
        "pattern": r"\bclient success manager\b",
        "suggested_action": "map_to_existing",
        "target_label": "customer_success_manager",
        "target_family": "customer_success",
        "overmatch_risk": "medium",
        "roi": "medium",
    },
    {
        "cluster_name": "data_architect_cluster",
        "pattern": r"\bdata architect\b",
        "suggested_action": "map_to_existing",
        "target_label": "solutions_architect",
        "target_family": "architecture",
        "overmatch_risk": "medium",
        "roi": "medium",
    },
    {
        "cluster_name": "devsecops_engineer_cluster",
        "pattern": r"\bdevsecops engineer\b",
        "suggested_action": "map_to_existing",
        "target_label": "devops_engineer",
        "target_family": "devops",
        "overmatch_risk": "low",
        "roi": "medium",
    },
    {
        "cluster_name": "onboarding_specialist_cluster",
        "pattern": r"\bonboarding specialist\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
    {
        "cluster_name": "chief_of_staff_cluster",
        "pattern": r"\bchief of staff\b",
        "suggested_action": "add_new_normalized_title",
        "target_label": "chief_of_staff",
        "target_family": "operations",
        "overmatch_risk": "medium",
        "roi": "medium",
    },
    {
        "cluster_name": "procurement_manager_cluster",
        "pattern": r"\bprocurement manager\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
    {
        "cluster_name": "office_manager_cluster",
        "pattern": r"\boffice manager\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
    {
        "cluster_name": "business_analyst_cluster",
        "pattern": r"\bbusiness analyst\b",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
    {
        "cluster_name": "producer_naked_cluster",
        "pattern": r"^producer$",
        "suggested_action": "keep_other_for_now",
        "target_label": "",
        "target_family": "",
        "overmatch_risk": "high",
        "roi": "low",
    },
]


def load_lookup_titles(path: Path) -> list[str]:
    out: list[str] = []
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            t = row.get("normalized_title")
            if isinstance(t, str) and t:
                out.append(t)
    return out


def support_strength(scores: list[int]) -> str:
    if not scores:
        return "none"
    avg = mean(scores)
    if avg >= 90:
        return "strong"
    if avg >= 82:
        return "medium"
    if avg >= 72:
        return "weak"
    return "none"


def best_scores(representatives: list[str], lookup_titles: list[str]) -> list[int]:
    if not representatives or not lookup_titles or process is None:
        return []
    scores: list[int] = []
    for r in representatives:
        match = process.extractOne(normalize_title(r), lookup_titles, scorer=fuzz.token_sort_ratio)
        if match:
            scores.append(int(match[1]))
    return scores


def score_item(item: dict[str, object]) -> float:
    volume = float(item["estimated_volume"])
    roi_w = {"high": 1.0, "medium": 0.7, "low": 0.4}[str(item["roi"])]
    risk_w = {"low": 1.0, "medium": 0.75, "high": 0.35}[str(item["overmatch_risk"])]
    support_w = {"strong": 1.0, "medium": 0.85, "weak": 0.65, "none": 0.5}[str(item["combined_support"])]
    return volume * roi_w * risk_w * support_w


def run(input_path: Path, esco_lookup: Path, onet_lookup: Path, outdir: Path) -> dict[str, object]:
    counter: Counter[str] = Counter()
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("classification_status") != "other":
                continue
            title = (row.get("title_clean") or row.get("title_raw") or "").strip()
            if title:
                counter[title] += 1

    esco_titles = load_lookup_titles(esco_lookup)
    onet_titles = load_lookup_titles(onet_lookup)

    candidates: list[dict[str, object]] = []
    for cdef in CLUSTER_DEFS:
        pat = re.compile(str(cdef["pattern"]))
        hits = [(t, c) for t, c in counter.items() if pat.search(t.lower())]
        if not hits:
            continue
        hits.sort(key=lambda x: x[1], reverse=True)
        reps = [t for t, _ in hits[:8]]
        vol = sum(c for _, c in hits)

        esco_scores = best_scores(reps, esco_titles)
        onet_scores = best_scores(reps, onet_titles)
        esco_support = support_strength(esco_scores)
        onet_support = support_strength(onet_scores)

        combined_support = "none"
        if "strong" in (esco_support, onet_support):
            combined_support = "strong"
        elif "medium" in (esco_support, onet_support):
            combined_support = "medium"
        elif "weak" in (esco_support, onet_support):
            combined_support = "weak"

        item = {
            "cluster_name": cdef["cluster_name"],
            "estimated_volume": vol,
            "representative_titles": [{"title": t, "count": c} for t, c in hits[:12]],
            "suggested_action": cdef["suggested_action"],
            "target_label": cdef["target_label"],
            "target_family": cdef["target_family"],
            "overmatch_risk": cdef["overmatch_risk"],
            "roi": cdef["roi"],
            "support_from_esco": esco_support,
            "support_from_onet": onet_support,
            "combined_support": combined_support,
            "lexical_pattern": cdef["pattern"],
        }
        item["priority_score"] = round(score_item(item), 2)
        candidates.append(item)

    candidates.sort(key=lambda x: float(x["priority_score"]), reverse=True)
    top15 = candidates[:15]

    selectable = [
        c
        for c in candidates
        if c["suggested_action"] != "keep_other_for_now" and c["overmatch_risk"] in {"low", "medium"}
    ]
    selected3 = sorted(selectable, key=lambda x: float(x["priority_score"]), reverse=True)[:3]

    report = {
        "candidates": candidates,
        "top_15": top15,
        "selected_for_shadow_batch": selected3,
    }
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "candidate_clusters.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate ESCO/O*NET-assisted candidate clusters")
    ap.add_argument("--input", required=True)
    ap.add_argument("--esco-lookup", required=True)
    ap.add_argument("--onet-lookup", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    run(Path(args.input), Path(args.esco_lookup), Path(args.onet_lookup), Path(args.outdir))


if __name__ == "__main__":
    main()

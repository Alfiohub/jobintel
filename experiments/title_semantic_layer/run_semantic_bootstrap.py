from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .build_esco_index import build_esco_index
from .build_onet_index import build_onet_index
from .build_title_corpus import build_title_corpus
from .common import normalize_title, read_json, read_jsonl, repo_root, tokenize, write_json
from .embed_titles import build_embedding_manifest
from .generate_candidate_clusters import generate_candidate_clusters
from .rank_candidates import rank_candidates
from .review_candidates import build_reviewer_output
from .semantic_retrieval import run_semantic_retrieval


def _ngram_counts(residual_rows: list[dict[str, Any]], n: int, top_k: int) -> list[dict[str, Any]]:
    c = Counter()
    for row in residual_rows:
        t = normalize_title(str(row.get("title_raw") or ""))
        toks = tokenize(t)
        if len(toks) < n:
            continue
        for i in range(0, len(toks) - n + 1):
            c[" ".join(toks[i : i + n])] += 1
    return [{"ngram": k, "count": v} for k, v in c.most_common(top_k)]


def _residual_discovery(dataset_path: Path) -> dict[str, Any]:
    rows = read_jsonl(dataset_path)
    residual = [r for r in rows if str(r.get("classification_status") or "") == "other"]

    raw_counter = Counter(str(r.get("title_raw") or "").strip() for r in residual if str(r.get("title_raw") or "").strip())
    norm_counter = Counter(normalize_title(str(r.get("title_raw") or "")) for r in residual)
    token_counter = Counter()
    for title, cnt in norm_counter.items():
        for tok in tokenize(title):
            token_counter[tok] += cnt

    return {
        "rows_total": len(rows),
        "other_total": len(residual),
        "top_raw_titles": [{"title": k, "count": v} for k, v in raw_counter.most_common(50)],
        "top_normalized_titles": [{"title": k, "count": v} for k, v in norm_counter.most_common(50)],
        "top_tokens": [{"token": k, "count": v} for k, v in token_counter.most_common(50)],
        "top_bigrams": _ngram_counts(residual, 2, 30),
        "top_trigrams": _ngram_counts(residual, 3, 30),
    }


def _build_markdown_report(report_payload: dict[str, Any], out_path: Path) -> None:
    baseline = report_payload["baseline"]
    summary = report_payload["semantic_bootstrap_summary"]
    reviewer = report_payload["reviewer_output"]
    retrieval_sample = report_payload["retrieval_quality_sample"]

    lines: list[str] = []
    lines.append("# Phase E — Semantic Layer Bootstrap Report")
    lines.append("")
    lines.append("## 1. Baseline confirmation")
    lines.append(f"- repo: `joballert2`")
    lines.append(f"- dataset: `{baseline['dataset']}`")
    lines.append(f"- total rows: `{baseline['rows_total']}`")
    lines.append(f"- other baseline: `{baseline['other_total']}`")
    lines.append(f"- status: `{baseline['status']}`")
    lines.append("")
    lines.append("## 2. Semantic layer bootstrap summary")
    lines.append(f"- internal canonical titles: `{summary['internal_canonical_count']}`")
    lines.append(f"- ESCO rows indexed: `{summary['esco_rows']}`")
    lines.append(f"- O*NET rows indexed: `{summary['onet_rows']}`")
    lines.append(f"- embedding approach: `{summary['embedding_method']}`")
    lines.append(f"- fallback note: `{summary['embedding_fallback_reason']}`")
    lines.append("")
    lines.append("## 3. Retrieval quality sample (30)")
    for idx, row in enumerate(retrieval_sample, 1):
        ti = row.get("top_internal", {})
        te = row.get("top_esco", {})
        to = row.get("top_onet", {})
        lines.append(
            f"{idx}. `{row.get('title','')}` ({row.get('count',0)}) | internal: `{ti.get('normalized_title','')}` {ti.get('score',0)} | ESCO: `{te.get('esco_preferred_label','')}` {te.get('score',0)} | O*NET: `{to.get('onet_title','')}` {to.get('score',0)} | action: `{row.get('suggested_action','')}`"
        )
    lines.append("")
    lines.append("## 4. Residual category split")
    for k, v in sorted(reviewer.get("category_split", {}).items(), key=lambda kv: kv[1], reverse=True):
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## 5. Top opportunities")
    for row in report_payload.get("top_opportunities", [])[:12]:
        lines.append(
            f"- `{row['cluster_or_title']}` | vol `{row['estimated_volume']}` | target `{row['target_label']}/{row['target_family']}` | risk `{row['risk']}` | action `{row['suggested_action']}`"
        )
    lines.append("")
    lines.append("## 6. Top failure modes")
    for row in report_payload.get("top_failure_modes", [])[:12]:
        lines.append(f"- `{row['cluster_or_title']}` | vol `{row['estimated_volume']}` | reason `{row['reason']}` | risk `{row['risk']}`")
    lines.append("")
    lines.append("## 7. Recommendation")
    lines.append(f"- `{report_payload['recommendation']}`")
    lines.append(f"- rationale: {report_payload['recommendation_rationale']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_phase_e_semantic_bootstrap(dataset_path: Path, apply_overlay: bool = True, output_prefix: str = "") -> dict[str, Any]:
    root = repo_root()
    reports = root / "experiments/title_semantic_layer/reports"
    suffix = f"{output_prefix}_" if output_prefix else ""
    docs_name = f"title_semantic_layer_bootstrap_{output_prefix}.md" if output_prefix else "title_semantic_layer_bootstrap_v1.md"
    docs_out = root / "docs" / docs_name

    discovery = _residual_discovery(dataset_path)

    internal = build_title_corpus(dataset_path, reports / f"{suffix}internal_title_corpus.json", apply_overlay=apply_overlay)
    esco_meta = build_esco_index(
        root / "ESCOfiles/ESCO dataset - v1.2.1 - classification - en - csv",
        reports / f"{suffix}esco_index.jsonl",
        reports / f"{suffix}esco_index_meta.json",
    )
    onet_meta = build_onet_index(
        root / "ONETfiles/db_30_2_excel",
        reports / f"{suffix}onet_index.jsonl",
        reports / f"{suffix}onet_index_meta.json",
    )
    embed_manifest = build_embedding_manifest(
        reports / f"{suffix}internal_title_corpus.json",
        reports / f"{suffix}esco_index.jsonl",
        reports / f"{suffix}onet_index.jsonl",
        reports / f"{suffix}embedding_manifest.json",
    )
    retrieval = run_semantic_retrieval(
        dataset_path=dataset_path,
        internal_corpus_path=reports / f"{suffix}internal_title_corpus.json",
        esco_index_path=reports / f"{suffix}esco_index.jsonl",
        onet_index_path=reports / f"{suffix}onet_index.jsonl",
        out_path=reports / f"{suffix}semantic_retrieval.json",
        top_n_residual=350,
    )
    ranked = rank_candidates(
        retrieval_path=reports / f"{suffix}semantic_retrieval.json",
        out_path=reports / f"{suffix}ranked_candidates.json",
        sample_size=80,
    )
    _ = generate_candidate_clusters(
        ranked_path=reports / f"{suffix}ranked_candidates.json",
        out_path=reports / f"{suffix}semantic_candidate_clusters.json",
    )
    reviewer = build_reviewer_output(
        ranked_path=reports / f"{suffix}ranked_candidates.json",
        out_path=reports / f"{suffix}reviewer_output.json",
        min_samples=30,
    )

    sample_rows = reviewer.get("sample_rows", [])[:30]

    recommendation = "semantic_layer_useful_only_as_reviewer"
    rationale = (
        "The residual has many high-ambiguity manager/analyst/partner titles; semantic retrieval improves triage and candidate ranking, "
        "but confidence is insufficient for direct auto-adoption without tighter human-in-the-loop review."
    )

    payload = {
        "baseline": {
            "dataset": str(dataset_path.relative_to(root)),
            "rows_total": discovery["rows_total"],
            "other_total": discovery["other_total"],
            "status": "ok" if (discovery["rows_total"] == 81011 and discovery["other_total"] == 36092) else "mismatch",
        },
        "semantic_bootstrap_summary": {
            "internal_canonical_count": internal["canonical_count"],
            "overlay_enabled": apply_overlay,
            "esco_rows": esco_meta["occupations_rows"],
            "onet_rows": onet_meta["index_rows"],
            "embedding_method": embed_manifest["embedding_method"],
            "embedding_fallback_reason": embed_manifest["fallback_reason"],
            "esco_assets": esco_meta["files"],
            "onet_assets": onet_meta["files"],
        },
        "residual_discovery": discovery,
        "retrieval_quality_sample": sample_rows,
        "reviewer_output": {
            "category_split": reviewer.get("category_split", {}),
            "category_counts": reviewer.get("category_counts", {}),
        },
        "top_opportunities": reviewer.get("top_opportunities", []),
        "top_failure_modes": reviewer.get("top_failure_modes", []),
        "recommendation": recommendation,
        "recommendation_rationale": rationale,
    }

    report_name = f"phase_e_bootstrap_report_{output_prefix}.json" if output_prefix else "phase_e_bootstrap_report.json"
    write_json(reports / report_name, payload)
    _build_markdown_report(payload, docs_out)
    return payload


if __name__ == "__main__":
    root = repo_root()
    dataset = root / "data/jobs/jobs_titled_en_recovery_v53_safe.jsonl"
    result = run_phase_e_semantic_bootstrap(dataset, apply_overlay=True, output_prefix="")
    print(json.dumps(result["baseline"], ensure_ascii=False))
    print(f"report_json=experiments/title_semantic_layer/reports/phase_e_bootstrap_report.json")
    print(f"report_md=docs/title_semantic_layer_bootstrap_v1.md")

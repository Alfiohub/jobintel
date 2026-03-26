from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.search_api import search_jobs
except ModuleNotFoundError:
    from search_api import search_jobs


def _s(v: Any) -> str:
    return str(v or "").strip()


def _n(v: Any) -> str:
    return _s(v).lower()


def _set(v: Any) -> set[str]:
    if v is None:
        return set()
    if isinstance(v, list):
        return {_n(x) for x in v if _s(x)}
    if isinstance(v, (str, int, float, bool)):
        s = _s(v)
        return {_n(s)} if s else set()
    return set()


def _title_family_score(job: dict[str, Any], exp_titles: set[str], exp_families: set[str]) -> float:
    jt = _n(job.get("normalized_title"))
    jf = _n(job.get("role_family"))
    title_hit = 1.0 if exp_titles and jt in exp_titles else 0.0
    family_hit = 1.0 if exp_families and jf in exp_families else 0.0
    if exp_titles and exp_families:
        return max(title_hit, 0.85 * family_hit)
    if exp_titles:
        return title_hit
    if exp_families:
        return family_hit
    return 0.0


def _geo_score(job: dict[str, Any], exp_countries: set[str], exp_location_types: set[str]) -> float:
    vals: list[float] = []
    if exp_countries:
        vals.append(1.0 if _n(job.get("country")) in exp_countries else 0.0)
    if exp_location_types:
        vals.append(1.0 if _n(job.get("location_type")) in exp_location_types else 0.0)
    if not vals:
        return 0.0
    return sum(vals) / float(len(vals))


def _coherence(job: dict[str, Any], expect: dict[str, Any]) -> float:
    exp_titles = _set(expect.get("normalized_titles"))
    exp_families = _set(expect.get("role_families"))
    exp_countries = _set(expect.get("countries"))
    exp_location_types = _set(expect.get("location_types"))

    tf = _title_family_score(job, exp_titles, exp_families)
    geo = _geo_score(job, exp_countries, exp_location_types)

    has_geo = bool(exp_countries or exp_location_types)
    if has_geo:
        score = 0.65 * tf + 0.35 * geo
    else:
        score = tf
    return round(score, 4)


def _load_queries(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError("queries file must be a JSON list")
    out: list[dict[str, Any]] = []
    for row in data:
        if isinstance(row, dict):
            out.append(row)
    if not out:
        raise RuntimeError("no valid queries found")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate ranking/search coherence on a small user query set.")
    ap.add_argument("--db", default="data/jobintel_microsaas_taxonomy_v1_final_2k_20260326_r3.sqlite")
    ap.add_argument("--queries", default="docs/search_quality_queries_v1.json")
    ap.add_argument("--out-dir", default="docs/search_quality_eval_v1")
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--relevant-threshold", type=float, default=0.75)
    args = ap.parse_args()

    queries = _load_queries(Path(args.queries))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    top_k = max(1, int(args.top_k))
    rel_thr = float(args.relevant_threshold)

    detailed_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for q in queries:
        qid = _s(q.get("query_id")) or "query"
        desc = _s(q.get("description"))
        params = q.get("params") if isinstance(q.get("params"), dict) else {}
        expect = q.get("expect") if isinstance(q.get("expect"), dict) else {}

        result = search_jobs(db_path=args.db, use_ranking=True, **params)
        jobs = list(result.get("results") or [])
        top = jobs[:top_k]

        coherences: list[float] = []
        relevant_count = 0

        for rank, job in enumerate(top, start=1):
            c = _coherence(job, expect)
            coherences.append(c)
            if c >= rel_thr:
                relevant_count += 1
            detailed_rows.append(
                {
                    "query_id": qid,
                    "description": desc,
                    "rank": rank,
                    "coherence": c,
                    "job_id": job.get("id"),
                    "title_clean": _s(job.get("title_clean")),
                    "normalized_title": _s(job.get("normalized_title")),
                    "role_family": _s(job.get("role_family")),
                    "country": _s(job.get("country")),
                    "location_type": _s(job.get("location_type")),
                    "url": _s(job.get("url")),
                }
            )

        avg_c = round(sum(coherences) / float(len(coherences)), 4) if coherences else 0.0
        hit_at_k = 1 if relevant_count > 0 else 0
        summary_rows.append(
            {
                "query_id": qid,
                "description": desc,
                "returned_count": len(jobs),
                f"avg_coherence_at_{top_k}": avg_c,
                f"relevant_at_{top_k}": relevant_count,
                f"hit_at_{top_k}": hit_at_k,
            }
        )

    overall_avg = round(
        sum(float(r[f"avg_coherence_at_{top_k}"]) for r in summary_rows) / float(len(summary_rows)), 4
    )
    overall_hit = round(
        sum(float(r[f"hit_at_{top_k}"]) for r in summary_rows) / float(len(summary_rows)), 4
    )

    with (out_dir / "query_set_used.json").open("w", encoding="utf-8") as f:
        json.dump(queries, f, ensure_ascii=False, indent=2)

    with (out_dir / "results_detailed.csv").open("w", encoding="utf-8", newline="") as f:
        if detailed_rows:
            w = csv.DictWriter(f, fieldnames=list(detailed_rows[0].keys()))
            w.writeheader()
            w.writerows(detailed_rows)

    with (out_dir / "results_summary.csv").open("w", encoding="utf-8", newline="") as f:
        if summary_rows:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)

    summary = {
        "db": args.db,
        "queries_file": args.queries,
        "queries_count": len(summary_rows),
        "top_k": top_k,
        "relevant_threshold": rel_thr,
        "overall_avg_coherence": overall_avg,
        "overall_hit_rate": overall_hit,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Search Quality Eval v1",
        "",
        f"- db: `{args.db}`",
        f"- queries: `{args.queries}`",
        f"- query count: `{len(summary_rows)}`",
        f"- top-k: `{top_k}`",
        f"- relevant threshold: `{rel_thr}`",
        "",
        "## Aggregate",
        "",
        f"- overall_avg_coherence: `{overall_avg}`",
        f"- overall_hit_rate: `{overall_hit}`",
        "",
        "## Per Query",
        "",
        f"| query_id | avg_coherence@{top_k} | hit@{top_k} | relevant@{top_k} | returned_count |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in summary_rows:
        md_lines.append(
            f"| {r['query_id']} | {r[f'avg_coherence_at_{top_k}']} | {r[f'hit_at_{top_k}']} | {r[f'relevant_at_{top_k}']} | {r['returned_count']} |"
        )
    md_lines.append("")
    (out_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote: {out_dir / 'query_set_used.json'}")
    print(f"Wrote: {out_dir / 'results_detailed.csv'}")
    print(f"Wrote: {out_dir / 'results_summary.csv'}")
    print(f"Wrote: {out_dir / 'summary.json'}")
    print(f"Wrote: {out_dir / 'summary.md'}")
    print(f"overall_avg_coherence={overall_avg} overall_hit_rate={overall_hit}")


if __name__ == "__main__":
    main()

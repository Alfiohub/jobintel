from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from jobintel.api import _compute_query_embedding, _cosine, _to_float_list


DEFAULT_QUERIES = [
    "senior data engineer remote",
    "python airflow dbt",
    "analytics director healthcare",
    "business analyst retail energy",
    "staff machine learning scientist",
    "solutions architect cloud",
    "enterprise account executive saas",
    "customer success manager",
    "technical recruiter contract",
    "product manager platform",
    "frontend react typescript",
    "devops kubernetes terraform",
    "data analyst tableau sql",
    "bi analyst power bi",
    "head of engineering",
    "hr business partner",
    "implementation consultant",
    "field cto",
    "ml engineer llm",
    "sales development representative",
]


@dataclass
class QueryBenchmark:
    query: str
    overlap_at_k: int
    hash_top1: str
    openai_top1: str


def _load_embeddings(db_path: str) -> dict[str, list[float]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT url, embedding_json FROM jobs_indexed "
        "WHERE url IS NOT NULL AND url <> '' AND embedding_json IS NOT NULL AND embedding_json <> ''"
    ).fetchall()
    out: dict[str, list[float]] = {}
    for row in rows:
        url = str(row["url"]).strip()
        if not url:
            continue
        emb = _to_float_list(row["embedding_json"])
        if emb:
            out[url] = emb
    return out


def _rank_urls(url_to_emb: dict[str, list[float]], q_emb: list[float], k: int) -> list[str]:
    scored: list[tuple[float, str]] = []
    for url, emb in url_to_emb.items():
        scored.append((_cosine(q_emb, emb), url))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [url for _, url in scored[:k]]


def _to_markdown(
    *,
    hash_db: str,
    openai_db: str,
    openai_model: str,
    k: int,
    common_urls: int,
    rows: list[QueryBenchmark],
) -> str:
    lines = []
    lines.append("# Semantic Benchmark: Hash vs OpenAI (Common Corpus)")
    lines.append("")
    lines.append(f"- hash DB: `{hash_db}`")
    lines.append(f"- openai DB: `{openai_db}`")
    lines.append(f"- openai model: `{openai_model}`")
    lines.append(f"- top-k: `{k}`")
    lines.append(f"- common URLs compared: `{common_urls}`")
    lines.append("")
    lines.append("| Query | Overlap@k | Hash Top-1 | OpenAI Top-1 |")
    lines.append("|---|---:|---|---|")
    for row in rows:
        lines.append(f"| {row.query} | {row.overlap_at_k}/{k} | {row.hash_top1} | {row.openai_top1} |")
    lines.append("")
    if rows:
        avg_overlap = sum(r.overlap_at_k for r in rows) / (len(rows) * k)
        lines.append(f"- Avg overlap@{k}: `{avg_overlap:.3f}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Benchmark hash vs openai semantic ranking on same URL corpus.")
    ap.add_argument("--hash-db", default="data/jobintel_microsaas.sqlite")
    ap.add_argument("--openai-db", default="data/jobintel_microsaas_openai.sqlite")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--openai-model", default="text-embedding-3-small")
    ap.add_argument("--timeout-sec", type=int, default=20)
    ap.add_argument("--queries-json", default="", help="Optional JSON file containing list[str] queries")
    ap.add_argument("--out", default="docs/semantic_benchmark_hash_vs_openai.md")
    args = ap.parse_args()

    queries = DEFAULT_QUERIES
    if args.queries_json:
        raw = json.loads(Path(args.queries_json).read_text(encoding="utf-8"))
        if isinstance(raw, list) and all(isinstance(x, str) for x in raw):
            queries = raw

    hash_map = _load_embeddings(args.hash_db)
    openai_map = _load_embeddings(args.openai_db)
    common = sorted(set(hash_map.keys()) & set(openai_map.keys()))
    if not common:
        raise RuntimeError("No common URLs between hash/openai DBs. Rebuild DBs on same corpus first.")

    hash_common = {u: hash_map[u] for u in common}
    openai_common = {u: openai_map[u] for u in common}
    hash_dim = len(next(iter(hash_common.values())))

    rows: list[QueryBenchmark] = []
    for query in queries:
        q_hash, _ = _compute_query_embedding(
            query,
            semantic_provider="hash",
            semantic_model=None,
            timeout_sec=args.timeout_sec,
            hash_dim=hash_dim,
        )
        q_openai, _ = _compute_query_embedding(
            query,
            semantic_provider="openai",
            semantic_model=args.openai_model,
            timeout_sec=args.timeout_sec,
            hash_dim=hash_dim,
        )
        hash_top = _rank_urls(hash_common, q_hash, args.k)
        openai_top = _rank_urls(openai_common, q_openai, args.k)
        overlap = len(set(hash_top) & set(openai_top))
        rows.append(
            QueryBenchmark(
                query=query,
                overlap_at_k=overlap,
                hash_top1=hash_top[0] if hash_top else "",
                openai_top1=openai_top[0] if openai_top else "",
            )
        )

    md = _to_markdown(
        hash_db=args.hash_db,
        openai_db=args.openai_db,
        openai_model=args.openai_model,
        k=args.k,
        common_urls=len(common),
        rows=rows,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Wrote benchmark report: {out_path}")
    print(f"Common URLs: {len(common)}")


if __name__ == "__main__":
    main()


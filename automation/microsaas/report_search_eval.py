from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QueryMetrics:
    query: str
    hash_p3: float
    hash_hit3: int
    hash_mrr3: float
    openai_p3: float
    openai_hit3: int
    openai_mrr3: float
    winner: str


def _as_rel(value: str) -> int:
    v = (value or "").strip().lower()
    if v in {"1", "true", "yes", "y"}:
        return 1
    return 0


def _p_at_k(rels: list[int], k: int) -> float:
    if not rels or k <= 0:
        return 0.0
    return sum(rels[:k]) / float(k)


def _hit_at_k(rels: list[int], k: int) -> int:
    return 1 if any(rels[:k]) else 0


def _mrr_at_k(rels: list[int], k: int) -> float:
    for idx, rel in enumerate(rels[:k], start=1):
        if rel:
            return 1.0 / float(idx)
    return 0.0


def _winner(hash_p3: float, hash_mrr3: float, openai_p3: float, openai_mrr3: float) -> str:
    # Primary metric: Precision@3, tie-breaker: MRR@3
    if openai_p3 > hash_p3:
        return "openai"
    if hash_p3 > openai_p3:
        return "hash"
    if openai_mrr3 > hash_mrr3:
        return "openai"
    if hash_mrr3 > openai_mrr3:
        return "hash"
    return "tie"


def _load_rows(path: Path) -> list[QueryMetrics]:
    rows: list[QueryMetrics] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            query = (raw.get("query") or "").strip()
            if not query:
                continue
            h = [
                _as_rel(raw.get("hash_top1_relevant") or ""),
                _as_rel(raw.get("hash_top2_relevant") or ""),
                _as_rel(raw.get("hash_top3_relevant") or ""),
            ]
            o = [
                _as_rel(raw.get("openai_top1_relevant") or ""),
                _as_rel(raw.get("openai_top2_relevant") or ""),
                _as_rel(raw.get("openai_top3_relevant") or ""),
            ]
            hash_p3 = _p_at_k(h, 3)
            hash_hit3 = _hit_at_k(h, 3)
            hash_mrr3 = _mrr_at_k(h, 3)
            openai_p3 = _p_at_k(o, 3)
            openai_hit3 = _hit_at_k(o, 3)
            openai_mrr3 = _mrr_at_k(o, 3)
            rows.append(
                QueryMetrics(
                    query=query,
                    hash_p3=hash_p3,
                    hash_hit3=hash_hit3,
                    hash_mrr3=hash_mrr3,
                    openai_p3=openai_p3,
                    openai_hit3=openai_hit3,
                    openai_mrr3=openai_mrr3,
                    winner=_winner(hash_p3, hash_mrr3, openai_p3, openai_mrr3),
                )
            )
    return rows


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _to_md(rows: list[QueryMetrics], source_csv: str) -> str:
    hash_wins = sum(1 for r in rows if r.winner == "hash")
    openai_wins = sum(1 for r in rows if r.winner == "openai")
    ties = sum(1 for r in rows if r.winner == "tie")

    hash_p3 = _avg([r.hash_p3 for r in rows])
    openai_p3 = _avg([r.openai_p3 for r in rows])
    hash_hit3 = _avg([float(r.hash_hit3) for r in rows])
    openai_hit3 = _avg([float(r.openai_hit3) for r in rows])
    hash_mrr3 = _avg([r.hash_mrr3 for r in rows])
    openai_mrr3 = _avg([r.openai_mrr3 for r in rows])

    lines: list[str] = []
    lines.append("# Search Benchmark Results v1 (Manual Relevance)")
    lines.append("")
    lines.append(f"- source csv: `{source_csv}`")
    lines.append(f"- queries: `{len(rows)}`")
    lines.append("- judged depth: `top-3`")
    lines.append("")
    lines.append("## Aggregate Metrics")
    lines.append("")
    lines.append("| Provider | Precision@3 | Hit@3 | MRR@3 |")
    lines.append("|---|---:|---:|---:|")
    lines.append(f"| hash | {hash_p3:.3f} | {hash_hit3:.3f} | {hash_mrr3:.3f} |")
    lines.append(f"| openai | {openai_p3:.3f} | {openai_hit3:.3f} | {openai_mrr3:.3f} |")
    lines.append("")
    lines.append(f"- wins: `openai={openai_wins}` `hash={hash_wins}` `tie={ties}`")
    lines.append("")
    lines.append("## Query Breakdown")
    lines.append("")
    lines.append("| Query | Hash P@3 | OpenAI P@3 | Hash MRR@3 | OpenAI MRR@3 | Winner |")
    lines.append("|---|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            f"| {r.query} | {r.hash_p3:.3f} | {r.openai_p3:.3f} | {r.hash_mrr3:.3f} | {r.openai_mrr3:.3f} | {r.winner} |"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `Top-10` relevance is not included in this report because the current manual eval set is top-3 only.")
    lines.append("- Next step: add a `top-10` judged CSV and extend this report with `P@10` and `MRR@10`.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate search benchmark report from manually judged top-3 CSV.")
    ap.add_argument("--csv", default="docs/semantic_eval_top3_prefilled.csv")
    ap.add_argument("--out", default="docs/search_benchmark_results_v1.md")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    rows = _load_rows(csv_path)
    if not rows:
        raise RuntimeError(f"No valid rows found in {csv_path}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_to_md(rows, source_csv=str(csv_path)), encoding="utf-8")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()


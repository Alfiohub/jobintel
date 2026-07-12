from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from common import ngrams, normalize_title, tokenize

try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover
    fuzz = None


def build_fuzzy_clusters(normalized_counter: Counter[str], max_titles: int, threshold: int) -> list[dict[str, object]]:
    items = normalized_counter.most_common(max_titles)
    clusters: list[dict[str, object]] = []

    for title, count in items:
        assigned = False
        for c in clusters:
            rep = c["representative"]
            score = 0
            if fuzz is not None:
                score = int(fuzz.token_sort_ratio(title, rep))
            else:
                score = 100 if title == rep else 0
            if score >= threshold:
                c["total_frequency"] += count
                if len(c["titles"]) < 8:
                    c["titles"].append({"title": title, "count": count})
                assigned = True
                break
        if not assigned:
            clusters.append(
                {
                    "representative": title,
                    "total_frequency": count,
                    "titles": [{"title": title, "count": count}],
                }
            )

    clusters.sort(key=lambda x: int(x["total_frequency"]), reverse=True)
    return clusters


def run(input_path: Path, outdir: Path) -> dict[str, object]:
    rows_total = 0
    other_total = 0
    raw_counter: Counter[str] = Counter()
    norm_counter: Counter[str] = Counter()
    token_counter: Counter[str] = Counter()
    bi_counter: Counter[str] = Counter()
    tri_counter: Counter[str] = Counter()

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows_total += 1
            row = json.loads(line)
            if row.get("classification_status") != "other":
                continue
            other_total += 1
            raw = (row.get("title_clean") or row.get("title_raw") or "").strip()
            if not raw:
                continue
            raw_counter[raw] += 1
            norm = normalize_title(raw)
            norm_counter[norm] += 1
            toks = tokenize(norm)
            token_counter.update(toks)
            bi_counter.update(ngrams(toks, 2))
            tri_counter.update(ngrams(toks, 3))

    fuzzy_clusters = build_fuzzy_clusters(norm_counter, max_titles=1500, threshold=92)

    report = {
        "rows_total": rows_total,
        "other_total": other_total,
        "top_raw_titles": [{"title": t, "count": c} for t, c in raw_counter.most_common(50)],
        "top_normalized_titles": [{"title": t, "count": c} for t, c in norm_counter.most_common(50)],
        "top_tokens": [{"token": t, "count": c} for t, c in token_counter.most_common(50)],
        "top_bigrams": [{"ngram": t, "count": c} for t, c in bi_counter.most_common(30)],
        "top_trigrams": [{"ngram": t, "count": c} for t, c in tri_counter.most_common(30)],
        "fuzzy_clusters": fuzzy_clusters[:120],
    }

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "residual_analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Residual analysis for shadow title recovery")
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    run(Path(args.input), Path(args.outdir))


if __name__ == "__main__":
    main()

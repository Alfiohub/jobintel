from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Optional

from .title_classifier import TitleClassifier
from .title_schema import TitleNormalizationResult


def classify_titles(titles: Iterable[str], classifier: Optional[TitleClassifier] = None) -> List[TitleNormalizationResult]:
    model = classifier or TitleClassifier()
    return [model.classify(t) for t in titles]


def build_coverage_report(results: List[TitleNormalizationResult], top_k: int = 20) -> Dict[str, object]:
    total = len(results)
    by_title = Counter(r.normalized_title for r in results)
    by_family = Counter(r.role_family for r in results)
    by_status = Counter(r.classification_status for r in results)
    by_rule = Counter((r.matched_rule_id or "") for r in results if r.matched_rule_id)
    other_by_reason = Counter(
        (r.notes[0] if r.notes else f"status:{r.classification_status}")
        for r in results
        if r.normalized_title == "other"
    )

    unmatched = Counter(r.title_clean for r in results if r.normalized_title == "other")
    other_count = by_title.get("other", 0)

    return {
        "rows": total,
        "other_rows": other_count,
        "other_pct": round((other_count * 100.0 / total), 2) if total else 0.0,
        "counts_by_normalized_title": dict(by_title),
        "counts_by_role_family": dict(by_family),
        "counts_by_status": dict(by_status),
        "rule_usage": [{"rule_id": rule_id, "count": count} for rule_id, count in by_rule.most_common()],
        "other_by_reason": [{"reason": reason, "count": count} for reason, count in other_by_reason.most_common()],
        "top_unmatched_titles": [{"title_clean": t, "count": c} for t, c in unmatched.most_common(top_k)],
    }

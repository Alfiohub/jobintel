from __future__ import annotations

import argparse
import json
import re
from typing import Any


# Conservative thresholds: only propose fallback when O*NET signal is strong.
HIGH_CONF_THRESHOLD = 0.85
MEDIUM_CONF_THRESHOLD = 0.75


def _s(value: Any) -> str:
    return str(value or "").strip()


def _title_to_slug(title: str) -> str:
    t = _s(title).lower()
    if not t:
        return ""
    t = re.sub(r"[^a-z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def apply_onet_fallback(
    normalized_title: str,
    role_family: str,
    onet_soc_code: str | None,
    onet_title: str | None,
    onet_match_score: float | None,
) -> dict[str, Any]:
    norm = _s(normalized_title).lower()
    _ = _s(role_family)  # reserved for future family-aware policy
    soc = _s(onet_soc_code)
    onet_lbl = _s(onet_title)

    try:
        score = float(onet_match_score) if onet_match_score is not None else 0.0
    except Exception:
        score = 0.0

    out = {
        "fallback_title": None,
        "fallback_reason": "not_applicable",
        "fallback_confidence": 0.0,
    }

    # Fallback policy only applies to weak internal title classification.
    if norm != "other":
        out["fallback_reason"] = "normalized_title_not_other"
        return out

    if not soc or not onet_lbl:
        out["fallback_reason"] = "missing_onet_mapping"
        return out

    if score >= HIGH_CONF_THRESHOLD:
        out["fallback_title"] = _title_to_slug(onet_lbl)
        out["fallback_reason"] = "other_with_high_conf_onet"
        out["fallback_confidence"] = round(score, 4)
        return out

    if score >= MEDIUM_CONF_THRESHOLD:
        out["fallback_title"] = _title_to_slug(onet_lbl)
        out["fallback_reason"] = "other_with_medium_conf_onet_review"
        out["fallback_confidence"] = round(score * 0.9, 4)
        return out

    out["fallback_reason"] = "onet_score_too_low"
    out["fallback_confidence"] = round(score, 4)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Example usage for O*NET fallback policy")
    ap.add_argument("--normalized-title", default="other")
    ap.add_argument("--role-family", default="other")
    ap.add_argument("--onet-soc-code", default="")
    ap.add_argument("--onet-title", default="")
    ap.add_argument("--onet-match-score", type=float, default=0.0)
    args = ap.parse_args()

    result = apply_onet_fallback(
        normalized_title=args.normalized_title,
        role_family=args.role_family,
        onet_soc_code=(args.onet_soc_code or None),
        onet_title=(args.onet_title or None),
        onet_match_score=args.onet_match_score,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

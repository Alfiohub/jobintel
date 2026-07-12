from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")
_META_TOKEN_RE = re.compile(
    r"\b(remote|hybrid|onsite|shift|gmt|utc|ist|pst|cst|est|cet|cest|"
    r"emea|apac|americas?)\b",
    re.IGNORECASE,
)
_TIMEZONE_OFFSET_RE = re.compile(r"\b(?:utc|gmt)\s*[+-]\s*\d{1,2}\b", re.IGNORECASE)


def clean_title(title_raw: str) -> str:
    text = _WS_RE.sub(" ", str(title_raw or "")).strip()
    if not text:
        return ""

    # Normalize punctuation/separators deterministically.
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"[|/]+", " - ", text)
    text = _WS_RE.sub(" ", text).strip()

    # Remove bracket blocks that are mostly metadata.
    text = re.sub(
        r"\((?:[^)]*\b(?:remote|hybrid|onsite|shift|gmt|utc|ist|pst|cst|est|cet|cest|emea|apac|americas?)\b[^)]*)\)",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = _WS_RE.sub(" ", text).strip()

    parts = re.split(r"\s+[-|]\s+", text)
    if len(parts) <= 1:
        return text

    # Keep core segment only when trailing parts look like metadata (not role semantics).
    def _looks_metadata(part: str) -> bool:
        p = _WS_RE.sub(" ", part).strip()
        if not p:
            return True
        # Keep cleaning deterministic/syntactic: metadata tokens and timezone offsets only.
        return bool(_META_TOKEN_RE.search(p) or _TIMEZONE_OFFSET_RE.search(p))

    if all(_looks_metadata(p) for p in parts[1:]):
        return _WS_RE.sub(" ", parts[0]).strip()

    return text


def normalize_for_match(title_clean: str) -> str:
    t = str(title_clean or "").lower().strip()
    t = re.sub(r"\([^\)]*\)", " ", t)
    t = re.sub(r"[^a-z0-9+/#& -]+", " ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t

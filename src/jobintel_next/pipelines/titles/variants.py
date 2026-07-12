from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")

_ABBREVIATIONS = [
    (re.compile(r"\bsr\.?\b", re.IGNORECASE), "senior"),
    (re.compile(r"\bjr\.?\b", re.IGNORECASE), "junior"),
    (re.compile(r"\bvp\b", re.IGNORECASE), "vice president"),
]

_PLURAL_RULES = [
    (re.compile(r"\bmanagers\b", re.IGNORECASE), "manager"),
    (re.compile(r"\bengineers\b", re.IGNORECASE), "engineer"),
    (re.compile(r"\banalysts\b", re.IGNORECASE), "analyst"),
    (re.compile(r"\brecruiters\b", re.IGNORECASE), "recruiter"),
]


def normalize_variants(text: str) -> str:
    t = str(text or "")
    for pattern, replacement in _ABBREVIATIONS:
        t = pattern.sub(replacement, t)
    for pattern, replacement in _PLURAL_RULES:
        t = pattern.sub(replacement, t)
    return _WS_RE.sub(" ", t).strip()


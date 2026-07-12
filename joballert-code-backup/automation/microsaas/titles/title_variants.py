from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")

_PLURAL_MAP = {
    "managers": "manager",
    "technicians": "technician",
    "drivers": "driver",
    "psychotherapists": "psychotherapist",
}

_ABBREVIATION_PATTERNS = [
    (re.compile(r"\bsr\.?\b", re.IGNORECASE), "senior"),
    (re.compile(r"\bjr\.?\b", re.IGNORECASE), "junior"),
    (re.compile(r"\bvp\b", re.IGNORECASE), "vice president"),
]

_ALIAS_PATTERNS = [
    (re.compile(r"\bbiz dev\b", re.IGNORECASE), "business development"),
]

_SENIORITY_PATTERNS = [
    re.compile(r"\bsenior\b", re.IGNORECASE),
    re.compile(r"\bjunior\b", re.IGNORECASE),
]


def normalize_plural_forms(text: str) -> str:
    out = str(text or "")
    for plural, singular in _PLURAL_MAP.items():
        out = re.sub(rf"\b{re.escape(plural)}\b", singular, out, flags=re.IGNORECASE)
    return _WS_RE.sub(" ", out).strip()


def expand_abbreviations(text: str) -> str:
    out = str(text or "")
    for pat, repl in _ABBREVIATION_PATTERNS:
        out = pat.sub(repl, out)
    return _WS_RE.sub(" ", out).strip()


def normalize_simple_aliases(text: str) -> str:
    out = str(text or "")
    for pat, repl in _ALIAS_PATTERNS:
        out = pat.sub(repl, out)
    return _WS_RE.sub(" ", out).strip()


def strip_seniority_tokens(text: str) -> str:
    out = str(text or "")
    for pat in _SENIORITY_PATTERNS:
        out = pat.sub(" ", out)
    out = _WS_RE.sub(" ", out).strip()
    return out


def normalize_lexical_variants(text: str) -> str:
    out = str(text or "")
    out = expand_abbreviations(out)
    out = normalize_plural_forms(out)
    out = normalize_simple_aliases(out)
    out = _WS_RE.sub(" ", out).strip()
    return out

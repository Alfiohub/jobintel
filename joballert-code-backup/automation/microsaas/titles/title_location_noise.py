from __future__ import annotations

import re

try:
    from automation.microsaas.location_normalization import CITY_TO_COUNTRY, COUNTRY_ALIASES, REGION_TOKENS
except ModuleNotFoundError:
    from location_normalization import CITY_TO_COUNTRY, COUNTRY_ALIASES, REGION_TOKENS


_WS_RE = re.compile(r"\s+")
_SEP_RE = re.compile(r"\s+[-|]\s+")
_GEO_MODE_RE = re.compile(r"\b(remote|hybrid|onsite|wfh|work from home)\b", re.IGNORECASE)
_VALID_ISO2 = {str(v).strip().lower() for v in COUNTRY_ALIASES.values() if str(v).strip()}
_US_STATE_ABBR = {
    "al",
    "ak",
    "az",
    "ar",
    "ca",
    "co",
    "ct",
    "de",
    "fl",
    "ga",
    "hi",
    "id",
    "il",
    "in",
    "ia",
    "ks",
    "ky",
    "la",
    "me",
    "md",
    "ma",
    "mi",
    "mn",
    "ms",
    "mo",
    "mt",
    "ne",
    "nv",
    "nh",
    "nj",
    "nm",
    "ny",
    "nc",
    "nd",
    "oh",
    "ok",
    "or",
    "pa",
    "ri",
    "sc",
    "sd",
    "tn",
    "tx",
    "ut",
    "vt",
    "va",
    "wa",
    "wv",
    "wi",
    "wy",
    "dc",
}


def _norm(text: str) -> str:
    t = re.sub(r"[^a-z0-9 ]", " ", str(text or "").lower())
    return _WS_RE.sub(" ", t).strip()


def is_country_noise(token: str) -> bool:
    norm = _norm(token)
    if not norm:
        return False
    if norm in COUNTRY_ALIASES:
        return True
    compact = norm.replace(" ", "")
    if len(compact) == 2 and compact.isalpha() and compact in _VALID_ISO2:
        return True
    return False


def is_region_scope_noise(token: str) -> bool:
    norm = _norm(token)
    if not norm:
        return False
    if norm in REGION_TOKENS:
        return True
    return any(re.search(rf"\b{re.escape(alias)}\b", norm) for alias in REGION_TOKENS)


def is_city_or_region_noise(token: str) -> bool:
    norm = _norm(token)
    if not norm:
        return False
    if norm in CITY_TO_COUNTRY:
        return True
    if is_region_scope_noise(norm):
        return True
    return False


def _is_location_tail(part: str) -> bool:
    p = _WS_RE.sub(" ", str(part or "")).strip()
    if not p:
        return True
    norm = _norm(p)
    if _GEO_MODE_RE.search(norm):
        return True
    if is_region_scope_noise(norm):
        return True
    if is_country_noise(norm):
        return True
    if is_city_or_region_noise(norm):
        return True

    tokens = norm.split()
    if any(tok in _US_STATE_ABBR for tok in tokens):
        return True
    if any(tok in CITY_TO_COUNTRY for tok in tokens):
        return True
    if any(tok in COUNTRY_ALIASES for tok in tokens):
        return True
    return False


def strip_simple_location_noise(text: str) -> str:
    s = _WS_RE.sub(" ", str(text or "")).strip()
    if not s:
        return s

    parts = [p.strip() for p in _SEP_RE.split(s) if p.strip()]
    if len(parts) > 1 and all(_is_location_tail(p) for p in parts[1:]):
        return _WS_RE.sub(" ", parts[0]).strip()

    # Soft suffix trim for patterns like "sales director apac" (no explicit separator).
    tokens = s.split()
    while tokens:
        tail = tokens[-1]
        if _is_location_tail(tail):
            tokens.pop()
            continue
        if len(tokens) >= 2 and _is_location_tail(" ".join(tokens[-2:])):
            tokens = tokens[:-2]
            continue
        break
    out = _WS_RE.sub(" ", " ".join(tokens)).strip()
    return out or s

from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")
_TAIL_SEP_RE = re.compile(r"\s*[-|,]\s*")
_NOISE_TOKEN_RE = re.compile(
    r"\b(remote|hybrid|onsite|wfh|emea|apac|latam|amer|americas?|dach|europe middle east and africa|asia pacific)\b",
    re.IGNORECASE,
)
_CITY_COUNTRY_RE = re.compile(
    r"\b(berlin|london|paris|new york|san francisco|austin|seattle|germany|france|italy|spain|portugal|netherlands|switzerland|austria|canada|united states|usa|uk)\b",
    re.IGNORECASE,
)


def _looks_state_code(token: str) -> bool:
    t = str(token or "").strip()
    return len(t) == 2 and t.isalpha()


def strip_simple_location_noise(text: str) -> str:
    t = _WS_RE.sub(" ", str(text or "")).strip()
    if not t:
        return ""
    parts = _TAIL_SEP_RE.split(t)
    if len(parts) <= 1:
        return t
    core = parts[0].strip()
    tails = [p.strip() for p in parts[1:] if p.strip()]
    if tails and all(_NOISE_TOKEN_RE.search(p) or _CITY_COUNTRY_RE.search(p) or _looks_state_code(p) for p in tails):
        return core
    return t

from __future__ import annotations

import re
from collections.abc import Iterable

_WORD_RE = re.compile(r"[a-z0-9]+")
_PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
_SPACE_RE = re.compile(r"\s+")
_LOCATION_TAIL_RE = re.compile(r"\s*[-,]\s*[a-z .']+,\s*[a-z]{2}\s*$")
_SENIORITY_RE = re.compile(r"\b(senior|sr\.?|staff|principal|lead|junior|jr\.?|associate)\b")
_ROMAN_RE = re.compile(r"\b(i|ii|iii|iv|v|vi|vii|viii|ix|x)\b")


def normalize_title(text: str) -> str:
    s = (text or "").lower().strip()
    s = _LOCATION_TAIL_RE.sub("", s)
    s = _PUNCT_RE.sub(" ", s)
    s = _SENIORITY_RE.sub(" ", s)
    s = _ROMAN_RE.sub(" ", s)
    s = _SPACE_RE.sub(" ", s).strip()
    return s


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


def ngrams(tokens: list[str], n: int) -> Iterable[str]:
    if n <= 0 or len(tokens) < n:
        return []
    return (" ".join(tokens[i : i + n]) for i in range(0, len(tokens) - n + 1))

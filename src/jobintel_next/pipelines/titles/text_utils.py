from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")
_PAREN_RE = re.compile(r"\(([^)]*)\)")

# Keep only high-signal classifier context from parenthetical chunks.
# This enables conservative recovery of contextual titles such as:
# - Stylist (Retail)
# - Field Technician (Mechanic) (Pump, Power & HVAC)
_PAREN_CONTEXT_KEEP = {
    "retail",
    "store",
    "floor",
    "mechanic",
    "pump",
    "power",
    "hvac",
    "automotive",
    "parts",
}


def normalize_title_for_match(title_clean: str) -> str:
    t = str(title_clean or "").strip().lower()
    paren_chunks = _PAREN_RE.findall(t)
    keep_tokens: list[str] = []
    seen: set[str] = set()
    for chunk in paren_chunks:
        c = re.sub(r"[^a-z0-9+/#& -]+", " ", chunk.lower())
        for token in _WS_RE.split(c.strip()):
            tok = token.strip("-_/")
            if not tok:
                continue
            if tok in _PAREN_CONTEXT_KEEP and tok not in seen:
                keep_tokens.append(tok)
                seen.add(tok)

    t = _PAREN_RE.sub(" ", t)
    if keep_tokens:
        t = f"{t} {' '.join(keep_tokens)}"
    t = re.sub(r"[^a-z0-9+/#& -]+", " ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t

from __future__ import annotations

from html import unescape
import re


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def clean_description_for_language(text: str | None) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    plain = unescape(raw)
    plain = re.sub(r"(?i)<br\s*/?>", " ", plain)
    plain = re.sub(r"(?i)</p>|</div>|</li>|</h[1-6]>", " ", plain)
    plain = _HTML_TAG_RE.sub(" ", plain)
    plain = _WS_RE.sub(" ", plain).strip()
    return plain


def text_for_language_decision(title: str, description_raw: str | None, *, max_desc_chars: int = 2000) -> str:
    title_part = _WS_RE.sub(" ", str(title or "")).strip()
    desc_part = clean_description_for_language(description_raw)
    if max_desc_chars > 0:
        desc_part = desc_part[:max_desc_chars]
    merged = f"{title_part}\n{desc_part}".strip()
    return _WS_RE.sub(" ", merged)

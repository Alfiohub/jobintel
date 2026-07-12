from __future__ import annotations

from html import unescape
import re


_WS_RE = re.compile(r"\s+")
_TAG_RE = re.compile(r"<[^>]+>")
_SEP_RE = re.compile(r"[\u2010-\u2015]")

_RESP_HEAD_RE = re.compile(
    r"^(responsibilit(?:y|ies)|what you(?:'| wi)ll do|what you do|your mission|role and responsibilities)\b[: ]*$",
    re.IGNORECASE,
)
_REQ_HEAD_RE = re.compile(
    r"^(requirements?|qualifications?|what you(?:'| wi)ll need|what you bring|must have|skills?)\b[: ]*$",
    re.IGNORECASE,
)

_RESP_SENTENCE_RE = re.compile(r"\b(you(?:'| wi)ll|responsible for|own|lead|deliver)\b", re.IGNORECASE)
_REQ_SENTENCE_RE = re.compile(r"\b(required|must have|qualifications?|experience with|strong knowledge)\b", re.IGNORECASE)


def clean_title_text(title: str | None) -> str:
    t = str(title or "").strip()
    if not t:
        return ""
    t = _SEP_RE.sub("-", t)
    t = re.sub(r"[|/]+", " - ", t)
    t = re.sub(r"\s*,\s*", ", ", t)
    t = _WS_RE.sub(" ", t).strip(" -")
    return t


def clean_location_text(location: str | None) -> str:
    return _WS_RE.sub(" ", str(location or "")).strip()


def html_to_plain_lines(raw: str | None) -> list[str]:
    text = str(raw or "").strip()
    if not text:
        return []
    text = unescape(unescape(text))
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|li|ul|ol|h[1-6]|section|article|tr)>", "\n", text)
    text = _TAG_RE.sub(" ", text)
    lines: list[str] = []
    for line in text.splitlines():
        clean = _WS_RE.sub(" ", line).strip()
        if clean:
            lines.append(clean)
    return lines


def clean_description_text(raw: str | None) -> str:
    lines = html_to_plain_lines(raw)
    if not lines:
        return ""
    # Keep description readable but deterministic in one field.
    return _WS_RE.sub(" ", " ".join(lines)).strip()


def _capture_section(lines: list[str], header_re: re.Pattern[str]) -> str:
    chunks: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not header_re.match(line):
            i += 1
            continue
        i += 1
        while i < len(lines):
            cur = lines[i]
            if _RESP_HEAD_RE.match(cur) or _REQ_HEAD_RE.match(cur):
                break
            if re.match(r"^[-*•]\s*", cur) or re.match(r"^\d+[.)]\s+", cur):
                cur = re.sub(r"^[-*•]\s*|^\d+[.)]\s+", "", cur).strip()
            chunks.append(cur)
            i += 1
        if chunks:
            break
    return _WS_RE.sub(" ", " ".join(chunks)).strip()


def _fallback_from_sentences(description_clean: str, pattern: re.Pattern[str], *, max_sentences: int = 4) -> str:
    if not description_clean:
        return ""
    selected: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", description_clean):
        s = sentence.strip()
        if s and pattern.search(s):
            selected.append(s)
            if len(selected) >= max_sentences:
                break
    return _WS_RE.sub(" ", " ".join(selected)).strip()


def extract_simple_sections(raw_description: str | None, description_clean: str) -> tuple[str, str]:
    lines = html_to_plain_lines(raw_description)
    responsibilities = _capture_section(lines, _RESP_HEAD_RE)
    requirements = _capture_section(lines, _REQ_HEAD_RE)

    if not responsibilities:
        responsibilities = _fallback_from_sentences(description_clean, _RESP_SENTENCE_RE)
    if not requirements:
        requirements = _fallback_from_sentences(description_clean, _REQ_SENTENCE_RE)
    return requirements, responsibilities

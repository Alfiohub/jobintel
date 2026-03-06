from __future__ import annotations

import argparse
import json
from html import unescape
import re
from pathlib import Path
from typing import Any


SKILL_PATTERNS: list[tuple[str, str]] = [
    (r"\bpython\b", "SKILL"),
    (r"\bsql\b", "SKILL"),
    (r"\bpostgres(?:ql)?\b", "SKILL"),
    (r"\bmysql\b", "SKILL"),
    (r"\bsnowflake\b", "SKILL"),
    (r"\bbigquery\b", "SKILL"),
    (r"\bredshift\b", "SKILL"),
    (r"\bdbt\b", "SKILL"),
    (r"\bspark\b", "SKILL"),
    (r"\bairflow\b", "SKILL"),
    (r"\bdatabricks\b", "SKILL"),
    (r"\bpandas\b", "SKILL"),
    (r"\bnumpy\b", "SKILL"),
    (r"\bscikit-learn\b", "SKILL"),
    (r"\btensorflow\b", "SKILL"),
    (r"\bpytorch\b", "SKILL"),
    (r"\br\b", "SKILL"),
    (r"\btableau\b", "SKILL"),
    (r"\bpower\s?bi\b", "SKILL"),
    (r"\blooker\b", "SKILL"),
    (r"\bexcel\b", "SKILL"),
    (r"\baws\b", "SKILL"),
    (r"\bazure\b", "SKILL"),
    (r"\bgcp\b", "SKILL"),
    (r"\bgoogle cloud\b", "SKILL"),
    (r"\bdocker\b", "SKILL"),
    (r"\bkubernetes\b|\bk8s\b", "SKILL"),
    (r"\bterraform\b", "SKILL"),
    (r"\bjava\b", "SKILL"),
    (r"\bjavascript\b", "SKILL"),
    (r"\btypescript\b", "SKILL"),
    (r"\breact\b", "SKILL"),
    (r"\bnode(?:\.js)?\b", "SKILL"),
    (r"\betl\b", "SKILL"),
    (r"\bmachine learning\b", "SKILL"),
    (r"\bdeep learning\b", "SKILL"),
    (r"\bllm\b|\blarge language model", "SKILL"),
]

SENIORITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bintern(?:ship)?\b", "SENIORITY"),
    (r"\bjunior\b|\bjr\.?\b", "SENIORITY"),
    (r"\bassociate\b", "SENIORITY"),
    (r"\bsenior\b|\bsr\.?\b", "SENIORITY"),
    (r"\bstaff\b", "SENIORITY"),
    (r"\bprincipal\b", "SENIORITY"),
    (r"\blead\b", "SENIORITY"),
    (r"\bmanager\b", "SENIORITY"),
    (r"\bdirector\b", "SENIORITY"),
    (r"\bhead\b", "SENIORITY"),
    (r"\bvp\b|\bvice president\b", "SENIORITY"),
    (r"\bchief\b|\bcfo\b|\bcto\b|\bceo\b", "SENIORITY"),
]

WORKPLACE_PATTERNS: list[tuple[str, str]] = [
    (r"\bremote\b|\bwork from home\b|\bdistributed\b|\banywhere\b", "WORKPLACE_TYPE"),
    (r"\bhybrid\b", "WORKPLACE_TYPE"),
    (r"\bon[\s-]?site\b", "WORKPLACE_TYPE"),
]

EMPLOYMENT_PATTERNS: list[tuple[str, str]] = [
    (r"\bfull[\s-]?time\b", "EMPLOYMENT_TYPE"),
    (r"\bpart[\s-]?time\b", "EMPLOYMENT_TYPE"),
    (r"\bcontract(?:or)?\b|\bfreelance\b|\btemp(?:orary)?\b", "EMPLOYMENT_TYPE"),
    (r"\bintern(?:ship)?\b", "EMPLOYMENT_TYPE"),
]

ROLE_KEYWORDS = (
    "engineer",
    "developer",
    "analyst",
    "scientist",
    "manager",
    "designer",
    "architect",
    "administrator",
    "consultant",
    "specialist",
    "coordinator",
    "technician",
    "recruiter",
    "sales",
    "marketer",
    "marketing",
    "product manager",
    "product owner",
    "program manager",
    "project manager",
    "writer",
    "editor",
    "researcher",
)

REMOTE_LOCATION_HINTS = {"remote", "hybrid", "onsite", "on site", "on-site"}
SALARY_PATTERNS: list[str] = [
    r"(?:\$|EUR|GBP|CAD|AUD)\s?\d[\d,]*(?:\.\d+)?\s?(?:-|to|–|—)\s?(?:\$|EUR|GBP|CAD|AUD)?\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:/|per)\s?(?:year|yr|hour|hr))?",
    r"\b\d[\d,]*(?:\.\d+)?\s?(?:-|to|–|—)\s?\d[\d,]*(?:\.\d+)?\s?(?:USD|EUR|GBP|CAD|AUD)\b",
    r"\$\d[\d,]*(?:\.\d+)?\s?(?:/|per)\s?(?:year|yr|hour|hr)",
]
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError as e:
                raise ValueError(f"invalid JSON at {path}:{line_no}: {e}") from e
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_existing_id_map(paths: list[Path]) -> dict[str, str]:
    out: dict[str, str] = {}
    for path in paths:
        for row in read_jsonl(path):
            url = str(row.get("url") or "").strip()
            row_id = str(row.get("id") or "").strip()
            if url and row_id:
                out[url] = row_id
    return out


def _strip_html(text: str) -> str:
    plain = unescape(text)
    plain = re.sub(r"(?i)<br\s*/?>", "\n", plain)
    plain = re.sub(r"(?i)</p>|</div>|</li>|</h[1-6]>", "\n", plain)
    plain = _HTML_TAG_RE.sub(" ", plain)
    plain = _WS_RE.sub(" ", plain)
    return plain.strip()


def row_description(row: dict[str, Any]) -> str:
    description = str(row.get("description_text") or "").strip()
    if description:
        return description
    raw_payload = row.get("raw_payload")
    if isinstance(raw_payload, dict):
        content = raw_payload.get("content")
        if isinstance(content, str) and content.strip():
            return _strip_html(content)
    return ""


def _has_overlap(entities: list[dict[str, Any]], source_field: str, start: int, end: int) -> bool:
    for ent in entities:
        if str(ent.get("source_field") or "") != source_field:
            continue
        ent_start = int(ent.get("start") or 0)
        ent_end = int(ent.get("end") or 0)
        if start < ent_end and end > ent_start:
            return True
    return False


def _add_entity(
    entities: list[dict[str, Any]],
    *,
    label: str,
    source_field: str,
    text: str,
    start: int,
    end: int,
) -> None:
    if start < 0 or end <= start or end > len(text):
        return
    span_text = text[start:end]
    if not span_text.strip():
        return
    if _has_overlap(entities, source_field, start, end):
        return
    entities.append(
        {
            "label": label,
            "text": span_text,
            "source_field": source_field,
            "start": start,
            "end": end,
        }
    )


def _find_first_pattern(text: str, patterns: list[tuple[str, str]]) -> tuple[str, int, int] | None:
    for pattern, label in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return label, match.start(), match.end()
    return None


def _find_all_patterns(
    text: str,
    patterns: list[tuple[str, str]],
    *,
    limit: int | None = None,
) -> list[tuple[str, int, int]]:
    found: list[tuple[str, int, int]] = []
    seen_spans: set[tuple[int, int]] = set()
    for pattern, label in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            key = (match.start(), match.end())
            if key in seen_spans:
                continue
            seen_spans.add(key)
            found.append((label, match.start(), match.end()))
            if limit is not None and len(found) >= limit:
                return found
    found.sort(key=lambda item: (item[1], item[2]))
    return found


def _find_salary_spans(text: str, *, limit: int = 2) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for pattern in SALARY_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            key = (match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
            if len(out) >= limit:
                return out
    out.sort()
    return out


def _extract_role_from_title(title: str) -> tuple[int, int] | None:
    if not title.strip():
        return None
    left = len(title) - len(title.lstrip())
    right = len(title.rstrip())
    core = title[left:right]
    lowered = core.lower()
    if not any(keyword in lowered for keyword in ROLE_KEYWORDS):
        return None

    prefix_end = 0
    for pattern, _label in SENIORITY_PATTERNS:
        match = re.match(rf"(?:{pattern})[\s,/:-]+", core, flags=re.IGNORECASE)
        if match:
            prefix_end = max(prefix_end, match.end())
            break

    role_start = left + prefix_end
    role_end = right
    role_text = title[role_start:role_end].strip()
    if len(role_text) < 4:
        return None
    return role_start, role_end


def generate_entities(row: dict[str, Any], *, max_skills: int) -> list[dict[str, Any]]:
    title = str(row.get("title") or "")
    description = row_description(row)
    location = str(row.get("location_raw") or "")
    entities: list[dict[str, Any]] = []

    role_span = _extract_role_from_title(title)
    if role_span is not None:
        _add_entity(entities, label="ROLE", source_field="title", text=title, start=role_span[0], end=role_span[1])

    seniority = _find_first_pattern(title, SENIORITY_PATTERNS)
    if seniority is not None:
        label, start, end = seniority
        _add_entity(entities, label=label, source_field="title", text=title, start=start, end=end)

    for source_field, text in (("title", title), ("location_raw", location), ("description_text", description)):
        workplace = _find_first_pattern(text, WORKPLACE_PATTERNS)
        if workplace is not None:
            label, start, end = workplace
            _add_entity(entities, label=label, source_field=source_field, text=text, start=start, end=end)
            break

    for source_field, text in (("title", title), ("description_text", description)):
        employment = _find_first_pattern(text, EMPLOYMENT_PATTERNS)
        if employment is not None:
            label, start, end = employment
            _add_entity(entities, label=label, source_field=source_field, text=text, start=start, end=end)
            break

    for start, end in _find_salary_spans(description):
        _add_entity(entities, label="SALARY", source_field="description_text", text=description, start=start, end=end)

    skill_hits: list[tuple[str, str, int, int]] = []
    for source_field, text in (("title", title), ("description_text", description)):
        for label, start, end in _find_all_patterns(text, SKILL_PATTERNS, limit=max_skills * 2):
            skill_hits.append((source_field, label, start, end))
    for source_field, label, start, end in skill_hits[:max_skills]:
        text = title if source_field == "title" else description
        _add_entity(entities, label=label, source_field=source_field, text=text, start=start, end=end)

    location_norm = location.strip().lower()
    if location_norm and location_norm not in REMOTE_LOCATION_HINTS:
        _add_entity(
            entities,
            label="LOCATION",
            source_field="location_raw",
            text=location,
            start=0,
            end=len(location),
        )

    entities.sort(key=lambda ent: (str(ent["source_field"]), int(ent["start"]), int(ent["end"])))
    return entities


def keep_row(
    row: dict[str, Any],
    entities: list[dict[str, Any]],
    *,
    min_entities: int,
    min_priority_labels: int,
    min_description_chars: int,
) -> bool:
    description = row_description(row)
    if len(description.strip()) < min_description_chars:
        return False
    if len(entities) < min_entities:
        return False
    priority = {
        "ROLE",
        "SKILL",
        "SENIORITY",
        "WORKPLACE_TYPE",
        "EMPLOYMENT_TYPE",
        "SALARY",
    }
    distinct_priority = {str(ent.get("label") or "") for ent in entities if str(ent.get("label") or "") in priority}
    return len(distinct_priority) >= min_priority_labels


def build_output_row(row: dict[str, Any], entities: list[dict[str, Any]], existing_id_map: dict[str, str]) -> dict[str, Any]:
    url = str(row.get("url") or "").strip()
    row_id = existing_id_map.get(url) or str(row.get("id") or "").strip()
    return {
        "id": row_id,
        "source": str(row.get("source") or ""),
        "url": url,
        "company_name": str(row.get("company_name") or ""),
        "title": str(row.get("title") or ""),
        "description_text": row_description(row),
        "location_raw": str(row.get("location_raw") or ""),
        "language": str(row.get("language") or "en"),
        "entities": entities,
        "annotation_status": "preannotated",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Mine rich Greenhouse English jobs and add weak NER labels.")
    ap.add_argument("--input", required=True, help="Greenhouse English corpus JSONL")
    ap.add_argument("--output", required=True, help="Weak-labeled output JSONL")
    ap.add_argument("--id-map-input", action="append", default=[], help="Existing NER JSONL used to reuse ids by url")
    ap.add_argument("--min-entities", type=int, default=3)
    ap.add_argument("--min-priority-labels", type=int, default=2)
    ap.add_argument("--min-description-chars", type=int, default=200)
    ap.add_argument("--max-skills", type=int, default=8)
    args = ap.parse_args()

    rows = read_jsonl(Path(args.input))
    existing_id_map = load_existing_id_map([Path(p) for p in args.id_map_input])
    kept: list[dict[str, Any]] = []

    for row in rows:
        entities = generate_entities(row, max_skills=max(1, args.max_skills))
        if not keep_row(
            row,
            entities,
            min_entities=max(1, args.min_entities),
            min_priority_labels=max(1, args.min_priority_labels),
            min_description_chars=max(0, args.min_description_chars),
        ):
            continue
        kept.append(build_output_row(row, entities, existing_id_map))

    write_jsonl(Path(args.output), kept)
    print(f"Input rows: {len(rows)}")
    print(f"Output rows: {len(kept)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

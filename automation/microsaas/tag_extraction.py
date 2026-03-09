from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SKILL_PATTERNS: dict[str, str] = {
    r"\bpy\b": "py",
    r"\bpython\b": "python",
    r"\bjs\b": "js",
    r"\bsql\b": "sql",
    r"\bpostgres(?:ql)?\b": "postgresql",
    r"\bmysql\b": "mysql",
    r"\bsnowflake\b": "snowflake",
    r"\bbigquery\b": "bigquery",
    r"\bdbt\b": "dbt",
    r"\bspark\b": "spark",
    r"\bairflow\b": "airflow",
    r"\bdatabricks\b": "databricks",
    r"\baws\b": "aws",
    r"\bazure\b": "azure",
    r"\bgcp\b|\bgoogle cloud\b": "gcp",
    r"\bdocker\b": "docker",
    r"\bkubernetes\b|\bk8s\b": "kubernetes",
    r"\bterraform\b": "terraform",
    r"\bexcel\b": "excel",
    r"\btableau\b": "tableau",
    r"\bpower\s?bi\b": "power_bi",
    r"\breact\b": "react",
    r"\bnode(?:\.js)?\b": "nodejs",
    r"\bts\b": "ts",
    r"\btypescript\b": "typescript",
    r"\bjavascript\b": "javascript",
    r"\bjava\b": "java",
    r"\bmachine learning\b": "machine_learning",
    r"\bllm\b|\blarge language model": "llm",
}


_ALIASES_PATH = Path(__file__).with_name("skills_aliases_v1.json")
try:
    _ALIASES_RAW = json.loads(_ALIASES_PATH.read_text(encoding="utf-8"))
    SKILL_ALIASES: dict[str, str] = {
        str(k).strip().lower(): str(v).strip().lower()
        for k, v in _ALIASES_RAW.items()
        if str(k).strip() and str(v).strip()
    }
except FileNotFoundError:
    SKILL_ALIASES = {}

SENIORITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bintern(?:ship)?\b", "intern"),
    (r"\bjunior\b|\bjr\.?\b", "junior"),
    (r"\bassociate\b", "associate"),
    (r"\bsenior\b|\bsr\.?\b", "senior"),
    (r"\bstaff\b", "staff"),
    (r"\bprincipal\b", "principal"),
    (r"\blead\b", "lead"),
    (r"\bmanager\b", "manager"),
    (r"\bdirector\b", "director"),
    (r"\bhead\b", "head"),
    (r"\bvp\b|\bvice president\b", "vp"),
]

SALARY_PATTERNS: list[str] = [
    r"(?:\$|EUR|GBP|CAD|AUD)\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:-|to|–|—)\s?(?:\$|EUR|GBP|CAD|AUD)?\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?(?:\s?(?:/|per)\s?(?:year|yr|hour|hr))?",
    r"\b\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:-|to|–|—)\s?\d[\d,]*(?:\.\d+)?\s*[kmb]?\s?(?:USD|EUR|GBP|CAD|AUD)\b",
]

_SALARY_POSITIVE_CONTEXT_RE = re.compile(
    r"\bsalary\b|\bcompensation\b|\bpay range\b|\bbase pay\b|\bbase salary\b|\bote\b|\bannual(?:ly)?\b|\bper year\b|\byearly\b|\bper hour\b|\bhourly\b",
    flags=re.IGNORECASE,
)
_SALARY_NEGATIVE_CONTEXT_RE = re.compile(
    r"\bbacked by\b|\braised\b|\bfunding\b|\bseries [a-z]\b|\bvaluation\b|\bpatients?\b|\bcustomers?\b|\busers?\b|\bemployees?\b",
    flags=re.IGNORECASE,
)

_EXPERIENCE_RANGE_RE = re.compile(
    r"(?i)\b(\d{1,2})\s*(?:\+|plus)?\s*(?:-|to|–|—)\s*(\d{1,2})\+?\s+years?\s+(?:of\s+)?experience\b"
)
_EXPERIENCE_MIN_RE = re.compile(
    r"(?i)\b(?:at least|min(?:imum)?|minimum of|required:?)?\s*(\d{1,2})\+?\s+years?\s+(?:of\s+)?experience\b"
)

_EDUCATION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)\bph\.?d\b|\bdoctorate\b"), "phd"),
    (re.compile(r"(?i)\bmaster'?s?\b|\bmsc\b|\bms\b|\bma\b|\bmba\b"), "master"),
    (re.compile(r"(?i)\bbachelor'?s?\b|\bbsc\b|\bbs\b|\bba\b"), "bachelor"),
    (re.compile(r"(?i)\bhigh school\b"), "high_school"),
]


def _extract_seniority(text: str) -> str | None:
    for pattern, value in SENIORITY_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return value
    return None


def _extract_employment_type(text: str) -> str | None:
    if re.search(r"\bfull[ -]?time\b", text, flags=re.IGNORECASE):
        return "full_time"
    if re.search(r"\bpart[ -]?time\b", text, flags=re.IGNORECASE):
        return "part_time"
    if re.search(r"\bcontract(?:or)?\b|\bfreelance\b", text, flags=re.IGNORECASE):
        return "contract"
    if re.search(r"\bintern(?:ship)?\b", text, flags=re.IGNORECASE):
        return "internship"
    if re.search(r"\btemporary\b|\btemp\b", text, flags=re.IGNORECASE):
        return "temporary"
    return None


def extract_location_type(text: str) -> str | None:
    if re.search(r"\bhybrid\b", text, flags=re.IGNORECASE):
        return "hybrid"
    if re.search(r"\bon[ -]?site\b|\bin office\b", text, flags=re.IGNORECASE):
        return "onsite"
    if re.search(r"\bremote\b|\bwork from home\b|\bdistributed\b|\banywhere\b", text, flags=re.IGNORECASE):
        return "remote"
    return None


def _parse_salary_number(num_text: str) -> int | None:
    m = re.match(r"(?i)^\s*(\d[\d,]*(?:\.\d+)?)\s*([kmb])?\s*$", num_text)
    if not m:
        return None
    base = float(m.group(1).replace(",", ""))
    mult = (m.group(2) or "").lower()
    if mult == "k":
        base *= 1_000
    elif mult == "m":
        base *= 1_000_000
    elif mult == "b":
        base *= 1_000_000_000
    return int(base)


def extract_salary(text: str) -> tuple[int | None, int | None, str | None]:
    text_upper = text.upper()
    default_currency: str | None = None
    if "$" in text:
        default_currency = "USD"
    elif "EUR" in text_upper or "€" in text:
        default_currency = "EUR"
    elif "GBP" in text_upper or "£" in text:
        default_currency = "GBP"
    elif "CAD" in text_upper:
        default_currency = "CAD"
    elif "AUD" in text_upper:
        default_currency = "AUD"

    chunks = [c.strip() for c in re.split(r"[.\n;]+", text) if c.strip()]
    for chunk in chunks:
        if _SALARY_NEGATIVE_CONTEXT_RE.search(chunk):
            continue
        has_positive_context = bool(_SALARY_POSITIVE_CONTEXT_RE.search(chunk))
        for pattern in SALARY_PATTERNS:
            m = re.search(pattern, chunk, flags=re.IGNORECASE)
            if not m:
                continue
            span = m.group(0)
            span_upper = span.upper()
            currency = default_currency
            if "$" in span:
                currency = "USD"
            elif "EUR" in span_upper or "€" in span:
                currency = "EUR"
            elif "GBP" in span_upper or "£" in span:
                currency = "GBP"
            elif "CAD" in span_upper:
                currency = "CAD"
            elif "AUD" in span_upper:
                currency = "AUD"

            if re.search(r"(?i)\d[\d,]*(?:\.\d+)?\s*[mb]\+?", span) and not has_positive_context:
                continue

            nums_raw = re.findall(r"(?i)\d[\d,]*(?:\.\d+)?\s*[kmb]?", span)
            vals = [v for v in (_parse_salary_number(x) for x in nums_raw) if v is not None]
            if not vals:
                continue
            s_min = min(vals)
            s_max = max(vals)
            if s_max > 2_000_000 and not re.search(r"(?i)\b(per hour|hourly|/hr|per day|daily)\b", chunk):
                continue
            if not has_positive_context and not re.search(r"(?i)\b(per year|yearly|annual|/yr|/year|per hour|hourly|/hr)\b", chunk):
                continue
            return s_min, s_max, currency

    return None, None, None


def _extract_skills(text: str) -> list[str]:
    found: list[str] = []
    for pattern, skill in SKILL_PATTERNS.items():
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(skill)
    normalized = [SKILL_ALIASES.get(s.strip().lower(), s.strip().lower()) for s in found]
    return sorted(set(normalized))


def _extract_experience(text: str) -> tuple[int | None, int | None, bool | None, str | None]:
    for m in _EXPERIENCE_RANGE_RE.finditer(text):
        lo = int(m.group(1))
        hi = int(m.group(2))
        if 0 <= lo <= 40 and 0 <= hi <= 40 and lo <= hi:
            return lo, hi, True, m.group(0).strip()
    m = _EXPERIENCE_MIN_RE.search(text)
    if m:
        lo = int(m.group(1))
        if 0 <= lo <= 40:
            return lo, None, True, m.group(0).strip()
    return None, None, None, None


def _extract_education(text: str) -> tuple[str | None, bool | None, str | None]:
    lowered = text.lower()
    degree_required: bool | None = None
    if re.search(r"\b(?:degree|required|required qualification)\b", lowered):
        degree_required = True
    elif re.search(r"\bdegree preferred\b|\bequivalent experience\b", lowered):
        degree_required = False

    for pattern, level in _EDUCATION_PATTERNS:
        m = pattern.search(text)
        if m:
            return level, degree_required, m.group(0).strip()
    return None, degree_required, None


def _split_location(location_clean: str) -> tuple[str | None, str | None]:
    if not location_clean:
        return None, None
    parts = [p.strip() for p in location_clean.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0], None


def extract_tags(clean: Any, normalized_title: str) -> dict[str, Any]:
    text = f"{clean.title_clean}\n{clean.location_clean}\n{clean.description_clean}"
    seniority = _extract_seniority(text)
    employment_type = _extract_employment_type(text)
    location_type = extract_location_type(text)
    city, region = _split_location(clean.location_clean)
    salary_min, salary_max, salary_currency = extract_salary(clean.description_clean)
    exp_min, exp_max, exp_required, exp_raw = _extract_experience(clean.description_clean)
    edu_level, degree_required, edu_raw = _extract_education(clean.description_clean)
    skills = _extract_skills(text)
    confidence = 0.35
    for value in (seniority, employment_type, location_type, salary_min):
        if value:
            confidence += 0.1
    if skills:
        confidence += min(0.25, len(skills) * 0.03)
    confidence = max(0.0, min(1.0, confidence))
    return {
        "normalized_title": normalized_title,
        "seniority": seniority,
        "employment_type": employment_type,
        "location_type": location_type,
        "city": city,
        "region": region,
        "country": None,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "experience_years_min": exp_min,
        "experience_years_max": exp_max,
        "experience_required": exp_required,
        "experience_text_raw": exp_raw,
        "education_level": edu_level,
        "degree_required": degree_required,
        "education_text_raw": edu_raw,
        "skills": skills,
        "tags": {
            "skills_count": len(skills),
            "has_salary": bool(salary_min or salary_max),
            "has_experience": bool(exp_min is not None or exp_max is not None),
            "has_education": bool(edu_level),
        },
        "tagger_version": "rules_v1",
        "tag_confidence": round(confidence, 4),
    }

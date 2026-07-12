from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    from automation.microsaas.location_normalization import normalize_location as _normalize_location
except ModuleNotFoundError:
    from location_normalization import normalize_location as _normalize_location
try:
    from automation.microsaas.reference_aliases import load_currency_aliases
except ModuleNotFoundError:
    from reference_aliases import load_currency_aliases


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
    r"(?:\$|€|£|[A-Z]{3})\s?\d[\d.,]*\s*[kmb]?\s?(?:-|to|–|—)\s?(?:\$|€|£|[A-Z]{3})?\s?\d[\d.,]*\s*[kmb]?(?:\s?(?:/|per)\s?(?:year|yr|hour|hr))?",
    r"\b\d[\d.,]*\s*[kmb]?\s?(?:-|to|–|—)\s?\d[\d.,]*\s*[kmb]?\s?[A-Z]{3}\b",
    r"\b\d[\d.,]*\s*[kmb]?\s?[A-Z]{3}\s?(?:-|to|–|—)\s?\d[\d.,]*\s*[kmb]?\s?[A-Z]{3}\b",
    r"\b\d[\d.,]*\s*[kmb]?\s?(?:-|to|–|—)\s?\d[\d.,]*\s*[kmb]?\b",
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

_CURRENCY_ALIASES = load_currency_aliases(
    {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
    }
)


def _detect_currency(text: str) -> str | None:
    if "$" in text:
        return "USD"
    if "€" in text:
        return "EUR"
    if "£" in text:
        return "GBP"

    lowered = text.lower()
    for alias in sorted(_CURRENCY_ALIASES.keys(), key=len, reverse=True):
        if alias in {"$", "€", "£"}:
            continue
        if not alias:
            continue
        if re.search(rf"\b{re.escape(alias)}\b", lowered):
            return _CURRENCY_ALIASES[alias]
    return None


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
    m = re.match(r"(?i)^\s*(\d[\d.,]*)\s*([kmb])?\s*$", num_text)
    if not m:
        return None
    raw = m.group(1).strip().strip(".,")
    if not raw:
        return None
    if "." in raw and "," in raw:
        if raw.rfind(",") > raw.rfind("."):
            # e.g. 90.000,50
            raw = raw.replace(".", "").replace(",", ".")
        else:
            # e.g. 90,000.50
            raw = raw.replace(",", "")
    elif re.match(r"^\d{1,3}(?:\.\d{3})+$", raw):
        # e.g. 90.000
        raw = raw.replace(".", "")
    else:
        raw = raw.replace(",", "")

    base = float(raw)
    mult = (m.group(2) or "").lower()
    if mult == "k":
        base *= 1_000
    elif mult == "m":
        base *= 1_000_000
    elif mult == "b":
        base *= 1_000_000_000
    return int(base)


def extract_salary(text: str) -> tuple[int | None, int | None, str | None]:
    # Normalize common HTML spaces from raw postings.
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")
    default_currency: str | None = _detect_currency(text)

    # Keep '.' to avoid breaking european thousands/decimals inside salary spans.
    chunks = [c.strip() for c in re.split(r"[\n;]+", text) if c.strip()]
    for chunk in chunks:
        if _SALARY_NEGATIVE_CONTEXT_RE.search(chunk):
            continue
        has_positive_context = bool(_SALARY_POSITIVE_CONTEXT_RE.search(chunk))
        for pattern in SALARY_PATTERNS:
            m = re.search(pattern, chunk, flags=re.IGNORECASE)
            if not m:
                continue
            span = m.group(0)
            currency = _detect_currency(span) or default_currency

            if re.search(r"(?i)\d[\d,]*(?:\.\d+)?\s*[mb]\+?", span) and not has_positive_context:
                continue

            nums_raw = re.findall(r"(?i)\d[\d.,]*\s*[kmb]?", span)
            vals = [v for v in (_parse_salary_number(x) for x in nums_raw) if v is not None]
            if not vals:
                continue
            s_min = min(vals)
            s_max = max(vals)
            if s_max > 2_000_000 and not re.search(r"(?i)\b(per hour|hourly|/hr|per day|daily)\b", chunk):
                continue
            has_period_hint = bool(re.search(r"(?i)\b(per year|yearly|annual|annually|/yr|/year|per hour|hourly|/hr)\b", chunk))
            if not has_positive_context and not has_period_hint:
                # Accept clear currency ranges even without explicit "salary"/"annual" tokens.
                if not currency or s_max < 10_000:
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


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def extract_tags(clean: Any, normalized_title: str) -> dict[str, Any]:
    text = f"{clean.title_clean}\n{clean.location_clean}\n{clean.description_clean}"
    seniority = _extract_seniority(text)
    employment_type = _extract_employment_type(text)
    location_type = extract_location_type(text)
    location_info = _normalize_location(
        location_clean=str(clean.location_clean or ""),
        description_clean=str(clean.description_clean or ""),
        location_type=location_type,
    )
    salary_min, salary_max, salary_currency = extract_salary(clean.description_clean)
    exp_min, exp_max, exp_required, exp_raw = _extract_experience(clean.description_clean)
    edu_level, degree_required, edu_raw = _extract_education(clean.description_clean)
    skills = _extract_skills(text)
    title_confidence = 0.3
    if str(clean.title_clean or "").strip():
        title_confidence += 0.2
    if normalized_title and normalized_title != "other":
        title_confidence += 0.4
    if seniority:
        title_confidence += 0.1
    title_confidence = _clamp01(title_confidence)

    location_confidence = 0.1
    if location_type:
        location_confidence += 0.2
    if location_info.get("country"):
        location_confidence += 0.4
    if location_info.get("city"):
        location_confidence += 0.3
    elif location_info.get("region"):
        location_confidence += 0.15
    location_confidence = _clamp01(location_confidence)

    salary_confidence = 0.05
    if salary_min is not None:
        salary_confidence += 0.25
    if salary_max is not None:
        salary_confidence += 0.25
    if salary_min is not None and salary_max is not None:
        salary_confidence += 0.2
    if salary_currency:
        salary_confidence += 0.25
    salary_confidence = _clamp01(salary_confidence)

    experience_confidence = 0.05
    if exp_raw:
        experience_confidence += 0.25
    if exp_min is not None:
        experience_confidence += 0.3
    if exp_max is not None:
        experience_confidence += 0.3
    if exp_min is not None and exp_max is not None:
        experience_confidence += 0.1
    experience_confidence = _clamp01(experience_confidence)

    education_confidence = 0.05
    if edu_raw:
        education_confidence += 0.25
    if edu_level in {"bachelor", "master", "phd", "high_school"}:
        education_confidence += 0.6
    elif edu_level:
        education_confidence += 0.35
    if degree_required is not None:
        education_confidence += 0.1
    education_confidence = _clamp01(education_confidence)

    confidence = _clamp01(
        (
            title_confidence
            + location_confidence
            + salary_confidence
            + experience_confidence
            + education_confidence
        )
        / 5.0
    )
    return {
        "normalized_title": normalized_title,
        "seniority": seniority,
        "employment_type": employment_type,
        "location_type": location_type,
        "city": location_info.get("city"),
        "region": location_info.get("region"),
        "country": location_info.get("country"),
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
        "title_confidence": round(title_confidence, 4),
        "location_confidence": round(location_confidence, 4),
        "salary_confidence": round(salary_confidence, 4),
        "experience_confidence": round(experience_confidence, 4),
        "education_confidence": round(education_confidence, 4),
        "skills": skills,
        "tags": {
            "skills_count": len(skills),
            "has_salary": bool(salary_min or salary_max),
            "has_experience": bool(exp_min is not None or exp_max is not None),
            "has_education": bool(edu_level),
            "country_source": location_info.get("country_source"),
            "location_resolution_notes": location_info.get("location_resolution_notes"),
        },
        "tagger_version": "rules_v2",
        "tag_confidence": round(confidence, 4),
    }

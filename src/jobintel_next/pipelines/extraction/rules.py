from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")

SENIORITY_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("vp", re.compile(r"\b(vice president|vp)\b", re.IGNORECASE)),
    ("head", re.compile(r"\bhead\b", re.IGNORECASE)),
    ("director", re.compile(r"\bdirector\b", re.IGNORECASE)),
    ("manager", re.compile(r"\bmanager\b", re.IGNORECASE)),
    ("principal", re.compile(r"\bprincipal\b", re.IGNORECASE)),
    ("staff", re.compile(r"\bstaff\b", re.IGNORECASE)),
    ("lead", re.compile(r"\blead\b", re.IGNORECASE)),
    ("senior", re.compile(r"\b(senior|sr\.?)\b", re.IGNORECASE)),
    ("associate", re.compile(r"\bassociate\b", re.IGNORECASE)),
    ("junior", re.compile(r"\b(junior|jr\.?)\b", re.IGNORECASE)),
    ("intern", re.compile(r"\b(intern|internship)\b", re.IGNORECASE)),
]

EMPLOYMENT_TYPE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("internship", re.compile(r"\b(internship|intern)\b", re.IGNORECASE)),
    ("part_time", re.compile(r"\bpart[\s-]?time\b", re.IGNORECASE)),
    ("full_time", re.compile(r"\bfull[\s-]?time\b|\bfte\b", re.IGNORECASE)),
    ("contract", re.compile(r"\b(contract|contractor|1099|freelance)\b", re.IGNORECASE)),
    ("temporary", re.compile(r"\b(temporary|temp\b|fixed[\s-]?term)\b", re.IGNORECASE)),
]

LOCATION_TYPE_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("hybrid", re.compile(r"\bhybrid\b", re.IGNORECASE)),
    ("remote", re.compile(r"\b(remote|work from home|wfh)\b", re.IGNORECASE)),
    ("onsite", re.compile(r"\b(on[\s-]?site|in[\s-]?office)\b", re.IGNORECASE)),
]

_CURRENCY_MAP = {
    "$": "USD",
    "usd": "USD",
    "€": "EUR",
    "eur": "EUR",
    "£": "GBP",
    "gbp": "GBP",
    "cad": "CAD",
    "aud": "AUD",
}

SALARY_RANGE_RE = re.compile(
    r"(?P<c1>\$|€|£|usd|eur|gbp|cad|aud)\s*"
    r"(?P<min>\d[\d,]*(?:\.\d+)?(?:\s*[kKmM](?![a-zA-Z]))?)\s*"
    r"(?:-|to|–|—)\s*"
    r"(?:(?P<c2>\$|€|£|usd|eur|gbp|cad|aud)\s*)?"
    r"(?P<max>\d[\d,]*(?:\.\d+)?(?:\s*[kKmM](?![a-zA-Z]))?)",
    re.IGNORECASE,
)

SALARY_SINGLE_FROM_RE = re.compile(
    r"\b(from|starting at)\s*"
    r"(?P<c>\$|€|£|usd|eur|gbp|cad|aud)\s*"
    r"(?P<v>\d[\d,]*(?:\.\d+)?(?:\s*[kKmM](?![a-zA-Z]))?)",
    re.IGNORECASE,
)

SKILL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("python", re.compile(r"\bpython\b", re.IGNORECASE)),
    ("sql", re.compile(r"\bsql\b", re.IGNORECASE)),
    ("java", re.compile(r"\bjava\b", re.IGNORECASE)),
    ("javascript", re.compile(r"\bjavascript\b", re.IGNORECASE)),
    ("typescript", re.compile(r"\btypescript\b", re.IGNORECASE)),
    ("react", re.compile(r"\breact\b", re.IGNORECASE)),
    ("node", re.compile(r"\bnode(?:\.?js)?\b", re.IGNORECASE)),
    ("aws", re.compile(r"\baws\b", re.IGNORECASE)),
    ("gcp", re.compile(r"\bgcp\b|\bgoogle cloud\b", re.IGNORECASE)),
    ("azure", re.compile(r"\bazure\b", re.IGNORECASE)),
    ("docker", re.compile(r"\bdocker\b", re.IGNORECASE)),
    ("kubernetes", re.compile(r"\bkubernetes\b|\bk8s\b", re.IGNORECASE)),
    ("dbt", re.compile(r"\bdbt\b", re.IGNORECASE)),
    ("tableau", re.compile(r"\btableau\b", re.IGNORECASE)),
    ("power_bi", re.compile(r"\bpower\s*bi\b", re.IGNORECASE)),
    ("excel", re.compile(r"\bexcel\b", re.IGNORECASE)),
    ("salesforce", re.compile(r"\bsalesforce\b", re.IGNORECASE)),
    ("tensorflow", re.compile(r"\btensorflow\b", re.IGNORECASE)),
    ("pytorch", re.compile(r"\bpytorch\b", re.IGNORECASE)),
    ("machine_learning", re.compile(r"\bmachine learning\b|\bml\b", re.IGNORECASE)),
]

_SKILL_STRONG_CONTEXT_RE = re.compile(
    r"\b("
    r"required|required skills|requirements|qualifications|must have|"
    r"experience with|experienced in|proficient in|proficiency in|"
    r"expertise in|knowledge of|familiar(?:ity)? with|"
    r"preferred|nice to have|tech stack|technology stack|tools?|technologies?"
    r")\b",
    re.IGNORECASE,
)

SALARY_PERIOD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("hour", re.compile(r"\b(per\s+hour|hourly|/hr\b|/hour\b)\b", re.IGNORECASE)),
    ("year", re.compile(r"\b(per\s+year|annually|annual salary|/year\b)\b", re.IGNORECASE)),
    ("day", re.compile(r"\b(per\s+day|daily|/day\b)\b", re.IGNORECASE)),
    ("month", re.compile(r"\b(per\s+month|monthly|/month\b)\b", re.IGNORECASE)),
    ("week", re.compile(r"\b(per\s+week|weekly|/week\b)\b", re.IGNORECASE)),
]


def _norm(text: str) -> str:
    return _WS_RE.sub(" ", str(text or "")).strip()


def extract_seniority(title_clean: str, description_clean: str) -> tuple[str | None, str | None]:
    title = _norm(title_clean)
    desc = _norm(description_clean)
    for value, pattern in SENIORITY_RULES:
        if pattern.search(title):
            return value, "title"
    for value, pattern in SENIORITY_RULES:
        if pattern.search(desc):
            return value, "description"
    return None, None


def extract_employment_type(title_clean: str, description_clean: str) -> tuple[str | None, str | None]:
    title = _norm(title_clean)
    desc = _norm(description_clean)
    for value, pattern in EMPLOYMENT_TYPE_RULES:
        if pattern.search(title):
            return value, "title"
    for value, pattern in EMPLOYMENT_TYPE_RULES:
        if pattern.search(desc):
            return value, "description"
    return None, None


def extract_location_type(location_clean: str, title_clean: str, description_clean: str) -> tuple[str | None, str | None]:
    loc = _norm(location_clean)
    title = _norm(title_clean)
    desc = _norm(description_clean)
    checks = [("location", loc), ("title", title), ("description", desc)]
    for value, pattern in LOCATION_TYPE_RULES:
        for source, text in checks:
            if pattern.search(text):
                return value, source
    return None, None


def _parse_amount(value: str) -> int | None:
    v = str(value or "").strip().lower().replace(",", "")
    mult = 1
    if v.endswith("k"):
        mult = 1000
        v = v[:-1]
    elif v.endswith("m"):
        mult = 1000000
        v = v[:-1]
    try:
        return int(float(v) * mult)
    except Exception:
        return None


def _currency_code(token: str | None) -> str | None:
    t = str(token or "").strip().lower()
    return _CURRENCY_MAP.get(t)


def _extract_salary_period(text: str) -> str | None:
    for period, pattern in SALARY_PERIOD_PATTERNS:
        if pattern.search(text):
            return period
    return None


def extract_salary(description_clean: str) -> tuple[int | None, int | None, str | None, str | None]:
    text = _norm(description_clean)
    if not text:
        return None, None, None, None

    m = SALARY_RANGE_RE.search(text)
    if m:
        salary_min = _parse_amount(m.group("min"))
        salary_max = _parse_amount(m.group("max"))
        currency = _currency_code(m.group("c1")) or _currency_code(m.group("c2"))
        window_start = max(0, m.start() - 24)
        window_end = min(len(text), m.end() + 72)
        salary_period = _extract_salary_period(text[window_start:window_end])
        return salary_min, salary_max, currency, salary_period

    m2 = SALARY_SINGLE_FROM_RE.search(text)
    if m2:
        salary_min = _parse_amount(m2.group("v"))
        currency = _currency_code(m2.group("c"))
        window_start = max(0, m2.start() - 24)
        window_end = min(len(text), m2.end() + 72)
        salary_period = _extract_salary_period(text[window_start:window_end])
        return salary_min, None, currency, salary_period

    return None, None, None, None


def _has_contextual_match(text: str, pattern: re.Pattern[str]) -> bool:
    for m in pattern.finditer(text):
        start = max(0, m.start() - 80)
        end = min(len(text), m.end() + 40)
        window = text[start:end]
        if _SKILL_STRONG_CONTEXT_RE.search(window):
            return True
    return False


def extract_skills(
    title_clean: str,
    description_clean: str,
    requirements_clean: str = "",
    responsibilities_clean: str = "",
) -> list[str]:
    title = _norm(title_clean)
    description = _norm(description_clean)
    requirements = _norm(requirements_clean)
    responsibilities = _norm(responsibilities_clean)

    out: list[str] = []
    for skill, pattern in SKILL_PATTERNS:
        # Title match is considered a strong signal.
        if pattern.search(title):
            out.append(skill)
            continue

        # Requirements section is high-signal only if section-level cue exists.
        if requirements and _SKILL_STRONG_CONTEXT_RE.search(requirements) and pattern.search(requirements):
            out.append(skill)
            continue

        # Description/responsibilities need local contextual cues around the match.
        if _has_contextual_match(description, pattern) or _has_contextual_match(responsibilities, pattern):
            out.append(skill)
            continue

    return out

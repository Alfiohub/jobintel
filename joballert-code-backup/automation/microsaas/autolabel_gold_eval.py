from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import time
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

try:
    from automation.microsaas.title_normalization import TITLE_RULES
except ModuleNotFoundError:
    from title_normalization import TITLE_RULES
try:
    from automation.microsaas.reference_aliases import load_country_aliases, load_currency_aliases
except ModuleNotFoundError:
    from reference_aliases import load_country_aliases, load_currency_aliases


ALLOWED_EDUCATION = {"none", "high_school", "bachelor", "master", "phd", "unspecified"}
ALLOWED_LOCATION_TYPE = {"remote", "hybrid", "onsite", "unspecified"}
ALLOWED_EMPLOYMENT_TYPE = {"full_time", "part_time", "contract", "internship", "temporary", "unspecified"}
ALLOWED_SENIORITY = {"intern", "junior", "mid", "senior", "lead", "manager", "director", "executive", "unspecified"}
ALLOWED_SALARY_PERIOD = {"hourly", "daily", "weekly", "monthly", "yearly", "unspecified"}

COUNTRY_ALIASES = {
    "us": "US",
    "u s": "US",
    "u.s": "US",
    "u.s.": "US",
    "usa": "US",
    "u.s.a": "US",
    "u.s.a.": "US",
    "united states": "US",
    "united states of america": "US",
    "america": "US",
    "uk": "GB",
    "u k": "GB",
    "u.k": "GB",
    "u.k.": "GB",
    "united kingdom": "GB",
    "great britain": "GB",
    "england": "GB",
    "ca": "CA",
    "canada": "CA",
    "au": "AU",
    "australia": "AU",
    "de": "DE",
    "germany": "DE",
    "fr": "FR",
    "france": "FR",
    "es": "ES",
    "spain": "ES",
    "it": "IT",
    "italy": "IT",
    "in": "IN",
    "india": "IN",
    "br": "BR",
    "brazil": "BR",
    "pk": "PK",
    "pakistan": "PK",
    "cn": "CN",
    "china": "CN",
    "tw": "TW",
    "taiwan": "TW",
    "nl": "NL",
    "netherlands": "NL",
    "the netherlands": "NL",
    "pl": "PL",
    "poland": "PL",
    "pt": "PT",
    "portugal": "PT",
    "ie": "IE",
    "ireland": "IE",
    "ch": "CH",
    "switzerland": "CH",
    "ro": "RO",
    "romania": "RO",
}
COUNTRY_ALIASES = load_country_aliases(COUNTRY_ALIASES)
CURRENCY_ALIASES = load_currency_aliases(
    {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
    }
)

PROMPT_HEADER = (
    "You are labeling one job posting for a strict evaluation dataset.\n"
    "Return ONLY one JSON object with exactly these keys:\n"
    "gold_normalized_title, gold_role_family, gold_experience_years_min, gold_experience_years_max,\n"
    "gold_experience_required, gold_education_level, gold_degree_required, gold_soft_skills,\n"
    "gold_location_type, gold_country, gold_location_city, gold_employment_type, gold_seniority,\n"
    "gold_language_requirements, gold_salary_min, gold_salary_max, gold_salary_currency, gold_salary_period,\n"
    "gold_tools_tech,\n"
    "confidence, needs_review, notes.\n"
    "Rules:\n"
    "- Use null when unknown.\n"
    "- experience fields must be numbers (0..40) or null.\n"
    "- education level must be one of: none, high_school, bachelor, master, phd, unspecified, or null.\n"
    "- gold_soft_skills should be semicolon-separated canonical labels or empty string.\n"
    "- gold_location_type must be one of: remote, hybrid, onsite, unspecified, or null.\n"
    "- gold_country should be a country name or ISO-2 country code, or null.\n"
    "- gold_employment_type must be one of: full_time, part_time, contract, internship, temporary, unspecified, or null.\n"
    "- gold_seniority must be one of: intern, junior, mid, senior, lead, manager, director, executive, unspecified, or null.\n"
    "- gold_language_requirements and gold_tools_tech should be semicolon-separated labels or empty string.\n"
    "- salary fields: min/max are integers, currency is ISO-3 (e.g., USD), period in {hourly,daily,weekly,monthly,yearly,unspecified}, or null.\n"
    "- needs_review must be true if confidence < 0.65 or if ambiguous.\n"
)

EXTRA_FIELDNAMES = (
    "gold_location_type",
    "gold_country",
    "gold_location_city",
    "gold_employment_type",
    "gold_seniority",
    "gold_language_requirements",
    "gold_salary_min",
    "gold_salary_max",
    "gold_salary_currency",
    "gold_salary_period",
    "gold_tools_tech",
    "label_source",
    "label_model",
    "label_confidence",
    "needs_review",
    "suggested_normalized_title",
    "suggested_role_family",
)

ALLOWED_NORMALIZED_TITLE = {n for _, n, _, _ in TITLE_RULES} | {"other"}
ALLOWED_ROLE_FAMILY = {f for _, _, f, _ in TITLE_RULES} | {"other"}

PROMPT_HEADER_TITLE_ROLE_ONLY = (
    "You are classifying ONLY job title taxonomy.\n"
    "Return ONLY one JSON object with exactly these keys:\n"
    "gold_normalized_title, gold_role_family, confidence, needs_review, notes, suggested_normalized_title, suggested_role_family.\n"
    "Rules:\n"
    "- If no reliable match exists, set gold_normalized_title='other' and gold_role_family='other'.\n"
    "- If you use 'other', you MAY add suggestions in suggested_normalized_title and suggested_role_family (free text).\n"
    "- Use short snake_case labels.\n"
    "- confidence in [0,1], needs_review true when ambiguous.\n"
)


def _to_bool_01(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y"}:
        return "1"
    if s in {"0", "false", "no", "n"}:
        return "0"
    return ""


def _to_int_str(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        i = int(float(value))
    except Exception:
        return ""
    if i < 0 or i > 40:
        return ""
    return str(i)


def _to_salary_int_str(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        i = int(float(value))
    except Exception:
        return ""
    if i < 0 or i > 10_000_000:
        return ""
    return str(i)


def _normalize_token(value: Any, *, allowed: set[str]) -> str:
    if value is None:
        return ""
    s = str(value).strip().lower()
    if not s:
        return ""
    s = s.replace("-", "_").replace(" ", "_")
    return s if s in allowed else "unspecified"


def _normalize_currency(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    s = raw.upper()
    if not s:
        return ""
    mapped = CURRENCY_ALIASES.get(raw.lower(), "")
    if mapped:
        return mapped
    if len(s) == 3 and s.isalpha():
        return s
    return ""


def _normalize_semicolon_list(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    items = re.split(r"[;,]", raw)
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        tok = re.sub(r"\s+", "_", item.strip().lower())
        tok = re.sub(r"[^a-z0-9_+#.\-]", "", tok)
        if not tok or tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
    return ";".join(out)


def _normalize_country(value: Any) -> str:
    if value is None:
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    parts = [p.strip() for p in re.split(r"[|,;/]+", raw) if p.strip()]
    if not parts:
        parts = [raw]
    for p in reversed(parts):
        k = re.sub(r"[^a-z0-9 ]", " ", p.lower())
        k = re.sub(r"\s+", " ", k).strip()
        if not k:
            continue
        if k in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[k]
        compact = k.replace(" ", "")
        if len(compact) == 2 and compact.isalpha():
            return compact.upper()
    return ""


def _extract_first_json_obj(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    start = -1
    depth = 0
    in_string = False
    escaped = False
    for i, ch in enumerate(text):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_string:
            escaped = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    parsed = json.loads(text[start : i + 1])
                except Exception:
                    continue
                if isinstance(parsed, dict):
                    return parsed
    return None


def _row_context(row: dict[str, str], *, max_desc_chars: int, include_desc: bool) -> str:
    excerpt = (row.get("description_clean_excerpt") or "").strip()
    if max_desc_chars > 0:
        excerpt = excerpt[:max_desc_chars]
    base = (
        f"title_raw: {row.get('title_raw', '')}\n"
        f"title_clean: {row.get('title_clean', '')}\n"
        f"pred_normalized_title: {row.get('pred_normalized_title', '')}\n"
        f"pred_role_family: {row.get('pred_role_family', '')}\n"
    )
    if not include_desc:
        return base
    return (
        base
        + f"description_clean_excerpt: {excerpt}\n"
        + f"pred_seniority: {row.get('pred_seniority', '')}\n"
        + f"pred_employment_type: {row.get('pred_employment_type', '')}\n"
        + f"pred_location_type: {row.get('pred_location_type', '')}\n"
        + f"pred_city: {row.get('pred_city', '')}\n"
        + f"pred_country: {row.get('pred_country', '')}\n"
        + f"pred_salary_min: {row.get('pred_salary_min', '')}\n"
        + f"pred_salary_max: {row.get('pred_salary_max', '')}\n"
        + f"pred_salary_currency: {row.get('pred_salary_currency', '')}\n"
    )


def _prompt_for_row(row: dict[str, str], *, max_desc_chars: int, title_role_only: bool) -> str:
    if title_role_only:
        return f"{PROMPT_HEADER_TITLE_ROLE_ONLY}\n{_row_context(row, max_desc_chars=max_desc_chars, include_desc=False)}"
    return f"{PROMPT_HEADER}\n{_row_context(row, max_desc_chars=max_desc_chars, include_desc=True)}"


def _call_ollama(
    prompt: str,
    *,
    model: str,
    url: str,
    timeout_sec: int,
    num_ctx: int,
    num_predict: int,
    num_thread: int | None,
) -> dict[str, Any]:
    options: dict[str, Any] = {
        "temperature": 0,
        "num_ctx": num_ctx,
        "num_predict": num_predict,
    }
    if num_thread is not None and num_thread > 0:
        options["num_thread"] = num_thread

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": options,
    }

    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")

    obj = json.loads(body)
    raw = obj.get("response", "")
    if not isinstance(raw, str):
        raise RuntimeError("Ollama response missing 'response' string")

    parsed = _extract_first_json_obj(raw)
    if not parsed:
        raise RuntimeError("Could not parse JSON object from Ollama response")
    return parsed


def _call_groq(
    prompt: str,
    *,
    model: str,
    api_key: str,
    url: str,
    timeout_sec: int,
    num_predict: int,
) -> dict[str, Any]:
    if not api_key.strip():
        raise RuntimeError("GROQ_API_KEY missing")

    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": num_predict,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urlrequest.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
        body = resp.read().decode("utf-8")

    obj = json.loads(body)
    content = (
        obj.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    if not isinstance(content, str):
        raise RuntimeError("Groq response missing message content")
    parsed = _extract_first_json_obj(content)
    if not parsed:
        raise RuntimeError("Could not parse JSON object from Groq response")
    return parsed


def _call_google(
    prompt: str,
    *,
    model: str,
    api_key: str,
    url_base: str,
    timeout_sec: int,
    num_predict: int,
    google_max_retries: int,
    google_backoff_base_ms: int,
    google_backoff_max_ms: int,
) -> dict[str, Any]:
    if not api_key.strip():
        raise RuntimeError("GOOGLE_API_KEY missing")

    base = url_base.rstrip("/")
    url = f"{base}/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": num_predict,
            "responseMimeType": "application/json",
        },
    }
    attempts = max(1, google_max_retries + 1)
    body = ""
    last_err: Exception | None = None
    for attempt in range(1, attempts + 1):
        req = urlrequest.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=timeout_sec) as resp:
                body = resp.read().decode("utf-8")
            break
        except urlerror.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                err_body = ""
            msg = (err_body or str(e)).lower()

            # Explicit model/url context for 404 debugging
            if e.code == 404:
                raise RuntimeError(f"Google model endpoint not found (model={model}, url={url}): HTTP 404")

            # Retry on quota/rate-limits
            retryable = e.code in {429, 503} or "resource_exhausted" in msg or "too many requests" in msg
            last_err = RuntimeError(f"Google HTTP {e.code}: {err_body or e}")
            if retryable and attempt < attempts:
                exp = google_backoff_base_ms * (2 ** (attempt - 1))
                wait_ms = min(max(1, google_backoff_max_ms), max(1, exp))
                jitter = random.randint(0, max(50, wait_ms // 10))
                time.sleep((wait_ms + jitter) / 1000.0)
                continue
            raise last_err
        except (TimeoutError, urlerror.URLError) as e:
            last_err = e
            if attempt < attempts:
                exp = google_backoff_base_ms * (2 ** (attempt - 1))
                wait_ms = min(max(1, google_backoff_max_ms), max(1, exp))
                jitter = random.randint(0, max(50, wait_ms // 10))
                time.sleep((wait_ms + jitter) / 1000.0)
                continue
            raise

    if not body:
        raise last_err if last_err is not None else RuntimeError("Google response body is empty")

    obj = json.loads(body)
    candidates = obj.get("candidates", [])
    text = ""
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts and isinstance(parts[0], dict):
            text = str(parts[0].get("text") or "")
    if not text:
        raise RuntimeError("Google response missing candidate text")

    parsed = _extract_first_json_obj(text)
    if not parsed:
        raise RuntimeError("Could not parse JSON object from Google response")
    return parsed


def _provider_chain(provider: str) -> list[str]:
    p = str(provider or "ollama").strip().lower()
    if p == "auto":
        return ["groq", "google", "ollama"]
    if p in {"ollama", "groq", "google"}:
        return [p]
    return ["ollama"]


def _call_llm(
    prompt: str,
    *,
    provider: str,
    model: str,
    timeout_sec: int,
    num_ctx: int,
    num_predict: int,
    num_thread: int | None,
    ollama_url: str,
    groq_url: str,
    groq_api_key: str,
    groq_model: str,
    google_api_key: str,
    google_model: str,
    google_url_base: str,
    google_max_retries: int,
    google_backoff_base_ms: int,
    google_backoff_max_ms: int,
) -> tuple[dict[str, Any], str, str]:
    last_err: Exception | None = None
    for p in _provider_chain(provider):
        try:
            if p == "ollama":
                out = _call_ollama(
                    prompt,
                    model=model,
                    url=ollama_url,
                    timeout_sec=timeout_sec,
                    num_ctx=num_ctx,
                    num_predict=num_predict,
                    num_thread=num_thread,
                )
                return out, "ollama", model

            if p == "groq":
                m = groq_model.strip() or model
                out = _call_groq(
                    prompt,
                    model=m,
                    api_key=groq_api_key,
                    url=groq_url,
                    timeout_sec=timeout_sec,
                    num_predict=num_predict,
                )
                return out, "groq", m

            if p == "google":
                m = google_model.strip() or "gemini-1.5-flash"
                out = _call_google(
                    prompt,
                    model=m,
                    api_key=google_api_key,
                    url_base=google_url_base,
                    timeout_sec=timeout_sec,
                    num_predict=num_predict,
                    google_max_retries=google_max_retries,
                    google_backoff_base_ms=google_backoff_base_ms,
                    google_backoff_max_ms=google_backoff_max_ms,
                )
                return out, "google", m

        except Exception as e:
            last_err = e
            continue

    raise last_err if last_err is not None else RuntimeError("No LLM provider available")


def _merge_notes(existing: str, incoming: str) -> str:
    a = (existing or "").strip()
    b = (incoming or "").strip()
    if not a:
        return b
    if not b:
        return a
    if b in a:
        return a
    return f"{a} | {b}"


def _normalize_llm_output(out: dict[str, Any], *, min_confidence: float) -> dict[str, str]:
    conf = out.get("confidence")
    try:
        conf_f = float(conf)
    except Exception:
        conf_f = 0.0

    needs_review = bool(out.get("needs_review")) or conf_f < min_confidence

    edu = out.get("gold_education_level")
    edu_s = str(edu).strip().lower() if edu is not None else ""
    if edu_s and edu_s not in ALLOWED_EDUCATION:
        edu_s = "unspecified"

    loc = out.get("gold_location_type")
    loc_s = str(loc).strip().lower() if loc is not None else ""
    if loc_s and loc_s not in ALLOWED_LOCATION_TYPE:
        loc_s = "unspecified"

    emp_s = _normalize_token(out.get("gold_employment_type"), allowed=ALLOWED_EMPLOYMENT_TYPE)
    sen_s = _normalize_token(out.get("gold_seniority"), allowed=ALLOWED_SENIORITY)
    sal_period_s = _normalize_token(out.get("gold_salary_period"), allowed=ALLOWED_SALARY_PERIOD)

    exp_min = _to_int_str(out.get("gold_experience_years_min"))
    exp_max = _to_int_str(out.get("gold_experience_years_max"))
    if exp_min and exp_max and int(exp_min) > int(exp_max):
        exp_min, exp_max = exp_max, exp_min

    salary_min = _to_salary_int_str(out.get("gold_salary_min"))
    salary_max = _to_salary_int_str(out.get("gold_salary_max"))
    if salary_min and salary_max and int(salary_min) > int(salary_max):
        salary_min, salary_max = salary_max, salary_min
    salary_currency = _normalize_currency(out.get("gold_salary_currency"))

    # Heuristic fallback for missing salary period:
    # - large numeric ranges with currency are almost always yearly
    # - smaller numeric ranges with currency are treated as hourly
    if not sal_period_s and salary_currency and (salary_min or salary_max):
        anchor = int(salary_max or salary_min or "0")
        if anchor >= 1000:
            sal_period_s = "yearly"
        elif anchor > 0:
            sal_period_s = "hourly"

    return {
        "gold_normalized_title": str(out.get("gold_normalized_title") or "").strip(),
        "gold_role_family": str(out.get("gold_role_family") or "").strip(),
        "gold_experience_years_min": exp_min,
        "gold_experience_years_max": exp_max,
        "gold_experience_required": _to_bool_01(out.get("gold_experience_required")),
        "gold_education_level": edu_s,
        "gold_degree_required": _to_bool_01(out.get("gold_degree_required")),
        "gold_soft_skills": _normalize_semicolon_list(out.get("gold_soft_skills")),
        "gold_location_type": loc_s,
        "gold_country": _normalize_country(out.get("gold_country")),
        "gold_location_city": str(out.get("gold_location_city") or "").strip(),
        "gold_employment_type": emp_s,
        "gold_seniority": sen_s,
        "gold_language_requirements": _normalize_semicolon_list(out.get("gold_language_requirements")),
        "gold_salary_min": salary_min,
        "gold_salary_max": salary_max,
        "gold_salary_currency": salary_currency,
        "gold_salary_period": sal_period_s,
        "gold_tools_tech": _normalize_semicolon_list(out.get("gold_tools_tech")),
        "review_status": "in_review" if needs_review else "approved",
        "notes": str(out.get("notes") or "").strip(),
        "label_confidence": f"{conf_f:.3f}",
        "needs_review": "1" if needs_review else "0",
    }


def _normalize_free_token(value: Any) -> str:
    if value is None:
        return ""
    s = str(value).strip().lower()
    if not s:
        return ""
    s = s.replace("-", "_").replace(" ", "_")
    s = re.sub(r"[^a-z0-9_+#.\-]", "", s)
    return s


def _normalize_title_role_only_output(out: dict[str, Any], *, min_confidence: float) -> dict[str, str]:
    conf = out.get("confidence")
    try:
        conf_f = float(conf)
    except Exception:
        conf_f = 0.0

    title_raw = _normalize_free_token(out.get("gold_normalized_title"))
    family_raw = _normalize_free_token(out.get("gold_role_family"))
    title = title_raw if title_raw in ALLOWED_NORMALIZED_TITLE else ""
    family = family_raw if family_raw in ALLOWED_ROLE_FAMILY else ""

    if not title:
        title = "other"
    if not family:
        family = "other"

    needs_review = bool(out.get("needs_review")) or conf_f < min_confidence or title == "other" or family == "other"

    suggested_title = _normalize_free_token(out.get("suggested_normalized_title"))
    suggested_family = _normalize_free_token(out.get("suggested_role_family"))
    notes = str(out.get("notes") or "").strip()
    if (title == "other" or family == "other") and (suggested_title or suggested_family):
        sug_msg = f"suggested_title={suggested_title or '-'};suggested_role_family={suggested_family or '-'}"
        notes = _merge_notes(notes, sug_msg)

    return {
        "gold_normalized_title": title,
        "gold_role_family": family,
        "suggested_normalized_title": suggested_title,
        "suggested_role_family": suggested_family,
        "review_status": "in_review" if needs_review else "approved",
        "notes": notes,
        "label_confidence": f"{conf_f:.3f}",
        "needs_review": "1" if needs_review else "0",
    }


def _apply_rule_based_review(update: dict[str, str]) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if not update.get("gold_normalized_title", "").strip():
        reasons.append("missing_normalized_title")

    if not update.get("gold_role_family", "").strip():
        reasons.append("missing_role_family")

    loc_type = update.get("gold_location_type", "").strip()
    country = update.get("gold_country", "").strip()
    city = update.get("gold_location_city", "").strip()
    if loc_type in {"onsite", "hybrid"} and not country and not city:
        reasons.append("location_without_country")

    salary_present = bool(update.get("gold_salary_min", "").strip() or update.get("gold_salary_max", "").strip())
    if salary_present:
        if not update.get("gold_salary_currency", "").strip():
            reasons.append("salary_without_currency")
        if not update.get("gold_salary_period", "").strip():
            reasons.append("salary_without_period")

    exp_min = update.get("gold_experience_years_min", "").strip()
    exp_max = update.get("gold_experience_years_max", "").strip()
    if exp_min and exp_max:
        try:
            if int(exp_min) > int(exp_max):
                reasons.append("experience_range_invalid")
        except ValueError:
            reasons.append("experience_parse_invalid")

    important_missing = sum(
        1
        for k in (
            "gold_normalized_title",
            "gold_role_family",
            "gold_location_type",
            "gold_employment_type",
            "gold_seniority",
        )
        if not update.get(k, "").strip()
    )
    if important_missing >= 3:
        reasons.append("too_many_core_fields_missing")

    return (len(reasons) > 0, reasons)


def _classify_error(e: Exception) -> str:
    msg = str(e).lower()
    if isinstance(e, TimeoutError):
        return "timeout_error"
    if isinstance(e, (urlerror.URLError, urlerror.HTTPError)):
        return "network_error"
    if "json" in msg:
        return "json_parse_error"
    return "runtime_error"


def _should_label(row: dict[str, str], *, overwrite: bool, title_role_only: bool) -> bool:
    if overwrite:
        return True
    if title_role_only:
        title = (row.get("gold_normalized_title") or "").strip()
        family = (row.get("gold_role_family") or "").strip()
        # In title-role-only mode, process rows where at least one field is missing.
        return not (title and family)
    return not any(
        (row.get(k) or "").strip()
        for k in (
            "gold_normalized_title",
            "gold_role_family",
            "gold_experience_years_min",
            "gold_education_level",
            "gold_location_type",
            "gold_country",
            "gold_location_city",
            "gold_employment_type",
            "gold_seniority",
            "gold_language_requirements",
            "gold_salary_min",
            "gold_salary_max",
            "gold_salary_currency",
            "gold_salary_period",
            "gold_tools_tech",
        )
    )


def _compute_fieldnames(rows: list[dict[str, str]]) -> list[str]:
    fieldnames = list(rows[0].keys())
    for extra in EXTRA_FIELDNAMES:
        if extra not in fieldnames:
            fieldnames.append(extra)
    return fieldnames


def _write_rows(out_path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Autolabel gold eval CSV via Ollama/Groq/Google.")
    ap.add_argument("--input", default="docs/gold_eval_set_v1.csv")
    ap.add_argument("--out", default="docs/gold_eval_set_v1_autolabeled.csv")
    ap.add_argument("--model", default="qwen2.5:7b")
    ap.add_argument("--provider", default="ollama", choices=["ollama", "groq", "google", "auto"])
    ap.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate")
    ap.add_argument("--groq-url", default="https://api.groq.com/openai/v1/chat/completions")
    ap.add_argument("--groq-api-key", default=os.getenv("GROQ_API_KEY", ""))
    ap.add_argument("--groq-model", default=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    ap.add_argument("--google-api-key", default=os.getenv("GOOGLE_API_KEY", ""))
    ap.add_argument("--google-model", default=os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"))
    ap.add_argument("--google-url-base", default="https://generativelanguage.googleapis.com/v1beta")
    ap.add_argument("--google-max-retries", type=int, default=3, help="Provider-level retries for Google 429/RESOURCE_EXHAUSTED.")
    ap.add_argument("--google-backoff-base-ms", type=int, default=1500, help="Google retry exponential backoff base (ms).")
    ap.add_argument("--google-backoff-max-ms", type=int, default=30000, help="Google retry exponential backoff max (ms).")
    ap.add_argument("--timeout-sec", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0, help="0 means all rows.")
    ap.add_argument("--start", type=int, default=0, help="0-based row offset.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing gold_* fields.")
    ap.add_argument(
        "--title-role-only",
        action="store_true",
        help="Only label gold_normalized_title and gold_role_family (closed-set).",
    )
    ap.add_argument("--min-confidence", type=float, default=0.65)
    ap.add_argument("--num-ctx", type=int, default=1024, help="Ollama context window for generation.")
    ap.add_argument("--num-predict", type=int, default=220, help="Max generated tokens per row.")
    ap.add_argument("--max-retries", type=int, default=2, help="Retries on invalid JSON response.")
    ap.add_argument(
        "--num-thread",
        type=int,
        default=max(1, min(4, (os.cpu_count() or 4) // 2)),
        help="CPU threads used by Ollama per request.",
    )
    ap.add_argument("--pause-ms", type=int, default=200, help="Sleep between rows to reduce sustained load.")
    ap.add_argument(
        "--max-desc-chars",
        type=int,
        default=420,
        help="Trim description_clean_excerpt before prompting (0 disables trimming).",
    )
    ap.add_argument(
        "--flush-every",
        type=int,
        default=25,
        help="Write partial CSV every N processed rows (0 disables checkpoints).",
    )
    args = ap.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.out)

    rows = list(csv.DictReader(in_path.open("r", encoding="utf-8")))
    if not rows:
        raise RuntimeError(f"No rows found in {in_path}")

    fieldnames = _compute_fieldnames(rows)

    labeled = 0
    errors = 0
    skipped = 0
    approved = 0
    in_review = 0

    selected = rows[args.start :]
    if args.limit > 0:
        selected = selected[: args.limit]

    processed_window = 0

    for row in selected:
        if not _should_label(row, overwrite=args.overwrite, title_role_only=args.title_role_only):
            skipped += 1
            continue

        try:
            out: dict[str, Any] | None = None
            last_err: Exception | None = None

            for attempt in range(max(1, args.max_retries + 1)):
                try:
                    out, used_provider, used_model = _call_llm(
                        _prompt_for_row(
                            row,
                            max_desc_chars=max(0, args.max_desc_chars),
                            title_role_only=args.title_role_only,
                        ),
                        provider=args.provider,
                        model=args.model,
                        timeout_sec=max(10, args.timeout_sec),
                        num_ctx=max(256, args.num_ctx),
                        num_predict=max(64, args.num_predict + attempt * 80),
                        num_thread=(args.num_thread if args.num_thread and args.num_thread > 0 else None),
                        ollama_url=args.ollama_url,
                        groq_url=args.groq_url,
                        groq_api_key=args.groq_api_key,
                        groq_model=args.groq_model,
                        google_api_key=args.google_api_key,
                        google_model=args.google_model,
                        google_url_base=args.google_url_base,
                        google_max_retries=max(0, args.google_max_retries),
                        google_backoff_base_ms=max(1, args.google_backoff_base_ms),
                        google_backoff_max_ms=max(1, args.google_backoff_max_ms),
                    )
                    break
                except RuntimeError as e:
                    last_err = e
                    if "Could not parse JSON object" not in str(e):
                        raise

            if out is None:
                raise last_err if last_err is not None else RuntimeError("Unknown autolabel error")

            previous_notes = row.get("notes", "")
            if args.title_role_only:
                update = _normalize_title_role_only_output(out, min_confidence=args.min_confidence)
            else:
                update = _normalize_llm_output(out, min_confidence=args.min_confidence)
                if not update.get("gold_country", "").strip():
                    pred_country = _normalize_country(row.get("pred_country"))
                    if pred_country:
                        update["gold_country"] = pred_country

                rule_review, rule_reasons = _apply_rule_based_review(update)
                if rule_review:
                    update["review_status"] = "in_review"
                    update["needs_review"] = "1"
                    update["notes"] = _merge_notes(
                        update.get("notes", ""),
                        f"rule_review: {','.join(rule_reasons)}",
                    )

            row.update(update)
            row["notes"] = _merge_notes(previous_notes, update.get("notes", ""))
            row["label_source"] = used_provider
            row["label_model"] = used_model

            labeled += 1
            if row.get("review_status") == "approved":
                approved += 1
            else:
                in_review += 1

        except (urlerror.URLError, urlerror.HTTPError, TimeoutError, RuntimeError, ValueError) as e:
            err_type = _classify_error(e)
            row["review_status"] = "todo"
            row["notes"] = _merge_notes(row.get("notes", ""), f"{err_type}: {e}")
            row["label_source"] = args.provider
            row["label_model"] = args.model
            row["label_confidence"] = "0.000"
            row["needs_review"] = "1"
            errors += 1

        processed_window += 1

        if args.flush_every > 0 and processed_window > 0 and processed_window % args.flush_every == 0:
            _write_rows(out_path, rows, fieldnames)
            print(f"[checkpoint] wrote partial output at processed={processed_window}")

        if args.pause_ms > 0:
            time.sleep(args.pause_ms / 1000.0)

    _write_rows(out_path, rows, fieldnames)

    print(f"Wrote: {out_path}")
    print(
        f"Rows total: {len(rows)} | attempted window: {len(selected)} | "
        f"labeled: {labeled} | approved: {approved} | in_review: {in_review} | "
        f"errors: {errors} | skipped: {skipped}"
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import re

try:
    from automation.microsaas.reference_aliases import load_country_aliases
except ModuleNotFoundError:
    from reference_aliases import load_country_aliases


COUNTRY_ALIASES: dict[str, str] = {
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
    "gb": "GB",
    "uk": "GB",
    "u k": "GB",
    "u.k": "GB",
    "u.k.": "GB",
    "united kingdom": "GB",
    "great britain": "GB",
    "england": "GB",
    "de": "DE",
    "germany": "DE",
    "fr": "FR",
    "france": "FR",
    "es": "ES",
    "spain": "ES",
    "it": "IT",
    "italy": "IT",
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
    "ca": "CA",
    "canada": "CA",
    "au": "AU",
    "australia": "AU",
    "in": "IN",
    "india": "IN",
    "tw": "TW",
    "taiwan": "TW",
    "hk": "HK",
    "hong kong": "HK",
}
COUNTRY_ALIASES = load_country_aliases(COUNTRY_ALIASES)

REGION_TOKENS = {
    "emea": "EMEA",
    "europe": "Europe",
    "eu": "Europe",
    "apac": "APAC",
    "asia pacific": "APAC",
    "latam": "LATAM",
    "north america": "North America",
    "na": "North America",
    "global": "Global",
    "worldwide": "Global",
}

CITY_TO_COUNTRY = {
    "berlin": "DE",
    "munich": "DE",
    "hamburg": "DE",
    "london": "GB",
    "manchester": "GB",
    "paris": "FR",
    "madrid": "ES",
    "barcelona": "ES",
    "milan": "IT",
    "rome": "IT",
    "amsterdam": "NL",
    "warsaw": "PL",
    "lisbon": "PT",
    "dublin": "IE",
    "zurich": "CH",
    "bucharest": "RO",
    "toronto": "CA",
    "vancouver": "CA",
    "montreal": "CA",
    "sydney": "AU",
    "melbourne": "AU",
    "delhi": "IN",
    "bangalore": "IN",
    "bengaluru": "IN",
    "mumbai": "IN",
    "new york": "US",
    "san francisco": "US",
    "austin": "US",
    "seattle": "US",
}

_DESC_LOCATION_PATTERNS = [
    re.compile(r"(?i)\bbased in ([a-z .'-]{2,40})"),
    re.compile(r"(?i)\bremote across (?:the )?([a-z .'-]{2,40})"),
    re.compile(r"(?i)\bremote from (?:the )?([a-z .'-]{2,40})"),
    re.compile(r"(?i)\bmust be located in (?:the )?([a-z .'-]{2,40})"),
    re.compile(r"(?i)\blocated in (?:the )?([a-z .'-]{2,40})"),
    re.compile(r"(?i)\bremote in (?:the )?([a-z .'-]{2,40})"),
    re.compile(r"(?i)\bhybrid in ([a-z .'-]{2,40})"),
]


def _s(value: str | None) -> str:
    return (value or "").strip()


def _norm(text: str) -> str:
    t = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    return re.sub(r"\s+", " ", t).strip()


def _country_from_text(text: str) -> str | None:
    norm = _norm(text)
    if not norm:
        return None
    if norm in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[norm]
    compact = norm.replace(" ", "")
    if len(compact) == 2 and compact.isalpha() and compact in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[compact]
    if len(compact) == 2 and compact.isalpha():
        return compact.upper()
    for alias, iso in COUNTRY_ALIASES.items():
        if len(alias) <= 2:
            continue
        if re.search(rf"\b{re.escape(alias)}\b", norm):
            return iso
    return None


def _country_from_text_strict(text: str) -> str | None:
    norm = _norm(text)
    if not norm:
        return None
    if norm in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[norm]
    compact = norm.replace(" ", "")
    if len(compact) == 2 and compact.isalpha():
        return COUNTRY_ALIASES.get(compact, compact.upper())
    return None


def _region_from_text(text: str) -> str | None:
    norm = _norm(text)
    if not norm:
        return None
    for token, canonical in REGION_TOKENS.items():
        if re.search(rf"\b{re.escape(token)}\b", norm):
            return canonical
    return None


def _clean_city_token(token: str) -> str:
    t = re.sub(r"(?i)\b(remote|hybrid|onsite|office based|work from home|wfh)\b", " ", token)
    t = re.sub(r"(?i)^\s*(in|at)\s+", "", t)
    t = re.sub(r"\s+", " ", t).strip(" -/,")
    return t


def _clean_country_token(token: str) -> str:
    t = re.sub(r"(?i)\b(remote|hybrid|onsite|office based|work from home|wfh|only|in|across|the)\b", " ", token)
    t = re.sub(r"\s+", " ", t).strip(" -/,")
    return t


def _parse_location_clean(location_clean: str) -> tuple[str | None, str | None, str | None, str | None]:
    loc = _s(location_clean)
    if not loc:
        return None, None, None, None

    country = _country_from_text(loc)
    region = _region_from_text(loc)

    # Keep hyphens inside tokens so regions like "Ile-de-France" remain intact.
    tokens = [t.strip() for t in re.split(r"[|,;/]+", loc) if t.strip()]
    city: str | None = None

    if not country and tokens:
        for token in reversed(tokens):
            country_candidate = _country_from_text(_clean_country_token(token))
            if country_candidate:
                country = country_candidate
                break

    if tokens:
        first = _clean_city_token(tokens[0])
        if first and not _country_from_text_strict(_clean_country_token(first)) and not _region_from_text(first):
            city = first
        if len(tokens) >= 3 and not region:
            mid = tokens[1].strip()
            if mid and not _country_from_text_strict(mid):
                region = mid

    if not country and city:
        c_guess = CITY_TO_COUNTRY.get(_norm(city))
        if c_guess:
            return city, region, c_guess, "location_clean_city_lookup"

    if country:
        return city, region, country, "location_clean"
    return city, region, None, None


def _infer_from_description(description_clean: str) -> tuple[str | None, str | None]:
    desc = _s(description_clean)
    if not desc:
        return None, None
    for pattern in _DESC_LOCATION_PATTERNS:
        m = pattern.search(desc)
        if not m:
            continue
        candidate = m.group(1).strip(" .,:;")
        country = _country_from_text(candidate)
        if country:
            return country, "description_clean"
        country = CITY_TO_COUNTRY.get(_norm(candidate))
        if country:
            return country, "description_clean_city_lookup"

    # Broad fallback for explicit country mentions in "remote/located" constraints.
    lowered = desc.lower()
    if any(tok in lowered for tok in ("remote", "located in", "based in", "work from")):
        for alias, iso in COUNTRY_ALIASES.items():
            if len(alias) <= 2:
                continue
            if re.search(rf"(?i)\b{re.escape(alias)}\b", desc):
                return iso, "description_clean_country_mention"

    return None, None


def normalize_location(
    location_clean: str,
    description_clean: str,
    location_type: str | None,
) -> dict[str, str | None]:
    city, region, country, country_source = _parse_location_clean(location_clean)
    notes: list[str] = []

    if country is None:
        inferred_country, inferred_source = _infer_from_description(description_clean)
        if inferred_country:
            country = inferred_country
            country_source = inferred_source
            notes.append("country_inferred_from_description")

    lt = _s(location_type).lower()
    if lt == "remote":
        # Keep explicit geographic info from location_clean (e.g. "Taipei, Taiwan").
        # Remote describes work mode and should not automatically erase valid city/country.
        if city and country:
            notes.append("remote_with_explicit_city_preserved")
        else:
            if city:
                notes.append("remote_city_cleared")
            city = None
            if not country:
                notes.append("remote_without_country")

    if not country and _region_from_text(location_clean):
        notes.append("region_scope_only")

    return {
        "city": city,
        "region": region,
        "country": country,
        "country_source": country_source,
        "location_resolution_notes": ";".join(notes) if notes else None,
    }

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

import requests

from ..interfaces import Collector
from ..canonical import validate_canonical
from ..model import JobPost

SOURCE_NAME = "lever"


def _as_bool(v: Any, default: bool = False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "on"}
    return bool(v)


def _as_str_list(v: Any) -> list[str]:
    if not isinstance(v, (list, tuple)):
        return []
    out: list[str] = []
    for x in v:
        if isinstance(x, str) and x.strip():
            out.append(x.strip())
    return out


def build_collector(cfg: Mapping[str, Any]) -> Collector | None:
    if not _as_bool(cfg.get("enabled"), default=False):
        return None
    companies = _as_str_list(cfg.get("companies"))
    if not companies:
        return None
    return LeverCollector(LeverConfig(companies=tuple(companies)))


@dataclass(frozen=True, slots=True)
class LeverConfig:
    companies: tuple[str, ...]


class LeverCollector(Collector):
    BASE = "https://api.lever.co/v0/postings/{company}"

    def __init__(self, cfg: LeverConfig, timeout_s: int = 20, retries: int = 3):
        self.cfg = cfg
        self.timeout_s = timeout_s
        self.retries = retries

    def name(self) -> str:
        return "lever"

    def fetch(self) -> list[JobPost]:
        out: list[JobPost] = []
        for company in self.cfg.companies:
            out.extend(self._fetch_company(company))
        return out

    def _fetch_company(self, company: str) -> list[JobPost]:
        url = self.BASE.format(company=company)
        postings = self._get(url, params={"mode": "json"})
        out: list[JobPost] = []
        for p in postings:
            if isinstance(p, Mapping):
                mapped = self._map(company, p)
                if mapped:
                    out.append(mapped)
        return out

    def _get(self, url: str, params: Mapping[str, Any]) -> list[Any]:
        last: Exception | None = None
        for _ in range(self.retries):
            try:
                r = requests.get(url, params=params, timeout=self.timeout_s)
                r.raise_for_status()
                data = r.json()
                return data if isinstance(data, list) else []
            except Exception as e:
                last = e
        raise RuntimeError(f"Lever failed: {last}")

    def _map(self, company_slug: str, j: Mapping[str, Any]) -> Optional[JobPost]:
        title = str(j.get("text") or "").strip()
        if not title:
            return None

        url = str(j.get("hostedUrl") or "").strip()
        if not url:
            return None

        categories = j.get("categories")
        location = ""
        if isinstance(categories, Mapping):
            location = str(categories.get("location") or "").strip()
        elif isinstance(j.get("location"), str):
            location = str(j.get("location") or "").strip()

        workplace_type = None
        txt = f"{title} {location}"
        if "remote" in txt.lower():
            workplace_type = "remote"

        published_at = _parse_ms_epoch(j.get("createdAt"))
        tags: tuple[str, ...] = ()
        if isinstance(categories, Mapping):
            values = [categories.get("team"), categories.get("commitment"), categories.get("level")]
            tags = tuple(str(v).strip() for v in values if isinstance(v, str) and v.strip())

        post = JobPost.from_source(
            source="lever",
            source_org=company_slug,
            external_id=str(j.get("id") or "").strip() or None,
            title=title,
            company_name=company_slug,
            location_raw=location,
            workplace_type=workplace_type,
            employment_type=str(categories.get("commitment") or "").strip() if isinstance(categories, Mapping) else None,
            seniority=str(categories.get("level") or "").strip() if isinstance(categories, Mapping) else None,
            function_family=str(categories.get("team") or "").strip() if isinstance(categories, Mapping) else None,
            url=url,
            posted_at=published_at,
            description_text=str(j.get("descriptionPlain") or ""),
            tags=tags,
            raw_payload=dict(j),
        )
        validate_canonical(post)
        return post


def _parse_ms_epoch(v: Any) -> Optional[datetime]:
    try:
        if v is None:
            return None
        ms = int(v)
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    except Exception:
        return None

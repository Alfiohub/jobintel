from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

import requests

from ..interfaces import Collector
from ..canonical import validate_canonical
from ..model import JobPost

SOURCE_NAME = "smartrecruiters"


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
    try:
        limit = int(cfg.get("limit", 100) or 100)
    except Exception:
        limit = 100
    return SmartRecruitersCollector(SmartRecruitersConfig(companies=tuple(companies), limit=limit))


@dataclass(frozen=True, slots=True)
class SmartRecruitersConfig:
    companies: tuple[str, ...]
    limit: int = 100


class SmartRecruitersCollector(Collector):
    BASE = "https://api.smartrecruiters.com/v1/companies/{company}/postings"

    def __init__(self, cfg: SmartRecruitersConfig, timeout_s: int = 20, retries: int = 3):
        self.cfg = cfg
        self.timeout_s = timeout_s
        self.retries = retries

    def name(self) -> str:
        return "smartrecruiters"

    def fetch(self) -> list[JobPost]:
        out: list[JobPost] = []
        for company in self.cfg.companies:
            out.extend(self._fetch_company(company))
        return out

    def _fetch_company(self, company: str) -> list[JobPost]:
        url = self.BASE.format(company=company)
        out: list[JobPost] = []
        limit = max(1, int(self.cfg.limit))
        offset = 0

        while True:
            params = {"limit": limit, "offset": offset}
            data = self._get(url, params=params)
            postings = data.get("content", []) if isinstance(data, Mapping) else []
            if not isinstance(postings, list) or not postings:
                break

            for p in postings:
                if isinstance(p, Mapping):
                    mapped = self._map(company, p)
                    if mapped:
                        out.append(mapped)

            total_found = data.get("totalFound") if isinstance(data, Mapping) else None
            if isinstance(total_found, int):
                offset += len(postings)
                if offset >= total_found:
                    break
            else:
                if len(postings) < limit:
                    break
                offset += len(postings)
        return out

    def _get(self, url: str, params: Mapping[str, Any]) -> Mapping[str, Any]:
        last: Exception | None = None
        for i in range(self.retries):
            try:
                r = requests.get(url, params=params, timeout=self.timeout_s)
                r.raise_for_status()
                data = r.json()
                return data if isinstance(data, Mapping) else {}
            except Exception as e:
                last = e
        raise RuntimeError(f"SmartRecruiters failed: {last}")

    def _map(self, company_slug: str, j: Mapping[str, Any]) -> Optional[JobPost]:
        title = str(j.get("name") or j.get("title") or "").strip()
        if not title:
            return None

        url = str(j.get("ref") or "").strip()
        if url:
            url = f"https://careers.smartrecruiters.com/{company_slug}/{url}"
        else:
            url = str(j.get("url") or "").strip()

        if not url:
            return None

        location_obj = j.get("location")
        location = ""
        if isinstance(location_obj, Mapping):
            parts = [
                str(location_obj.get("city") or "").strip(),
                str(location_obj.get("region") or "").strip(),
                str(location_obj.get("country") or "").strip(),
            ]
            location = ", ".join([p for p in parts if p])
        elif isinstance(location_obj, str):
            location = location_obj.strip()

        workplace_type = None
        txt = f"{title} {location}"
        if "remote" in txt.lower():
            workplace_type = "remote"

        published_at = _parse_dt(j.get("releasedDate") or j.get("createdOn") or j.get("updatedOn"))

        loc_city = str(location_obj.get("city") or "").strip() if isinstance(location_obj, Mapping) else None
        loc_region = str(location_obj.get("region") or "").strip() if isinstance(location_obj, Mapping) else None
        loc_country = str(location_obj.get("country") or "").strip() if isinstance(location_obj, Mapping) else None
        post = JobPost.from_source(
            source="smartrecruiters",
            source_org=company_slug,
            external_id=str(j.get("id") or j.get("ref") or "").strip() or None,
            title=title,
            company_name=company_slug,
            location_raw=location,
            city=loc_city or None,
            region=loc_region or None,
            country_code=loc_country or None,
            workplace_type=workplace_type,
            url=url,
            posted_at=published_at,
            description_text="",
            tags=(),
            raw_payload=dict(j),
        )
        validate_canonical(post)
        return post


def _parse_dt(v: Any) -> Optional[datetime]:
    if not isinstance(v, str) or not v.strip():
        return None
    s = v.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

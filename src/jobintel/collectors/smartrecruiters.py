from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

import requests

from ..interfaces import Collector
from ..model import JobPost


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
        params = {"limit": self.cfg.limit}
        data = self._get(url, params=params)
        postings = data.get("content", []) if isinstance(data, Mapping) else []

        out: list[JobPost] = []
        for p in postings:
            if isinstance(p, Mapping):
                mapped = self._map(company, p)
                if mapped:
                    out.append(mapped)
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

        remote = None
        txt = f"{title} {location}"
        if "remote" in txt.lower():
            remote = True

        published_at = _parse_dt(j.get("releasedDate") or j.get("createdOn") or j.get("updatedOn"))

        return JobPost(
            title=title,
            company=company_slug,
            location=location,
            url=url,
            source="smartrecruiters",
            remote=remote,
            published_at=published_at,
            description="",
            tags=(),
            raw=dict(j),
        )


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

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
import re
from typing import Any, Mapping, Optional
import asyncio
import time
import httpx
import requests

from ..interfaces import Collector
from ..canonical import validate_canonical
from ..model import JobPost

SOURCE_NAME = "greenhouse"
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


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
    if not _as_bool(cfg.get("enabled"), default=True):
        return None
    boards = _as_str_list(cfg.get("boards"))
    if not boards:
        return None
    content = _as_bool(cfg.get("content"), default=True)
    board_objs = [GreenhouseBoard(token=t, company_name=t) for t in boards]
    return GreenhouseCollector(boards=board_objs, content=content)


@dataclass(frozen=True, slots=True)
class GreenhouseBoard:
    token: str
    company_name: str


class GreenhouseCollector(Collector):

    BASE_URL = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(
        self,
        boards: list[GreenhouseBoard],
        content: bool = True,
        timeout_s: int = 20,
        retries: int = 3,
        max_concurrency: int = 8,
    ):
        self.boards = boards
        self.content = content
        self.timeout = timeout_s
        self.retries = retries
        self.max_concurrency = max_concurrency

    def name(self) -> str:
        return "greenhouse"

    def fetch(self) -> list[JobPost]:
        # Use async to speed up network-bound fetches.
        return asyncio.run(self._fetch_all())

    async def _fetch_all(self) -> list[JobPost]:
        if not self.boards:
            return []
        sem = asyncio.Semaphore(self.max_concurrency)
        timeout = httpx.Timeout(self.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            tasks = [self._fetch_board_async(client, b, sem) for b in self.boards]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        out: list[JobPost] = []
        errors: list[Exception] = []
        for res in results:
            if isinstance(res, Exception):
                errors.append(res)
            else:
                out.extend(res)
        if not out and errors:
            raise RuntimeError(f"Greenhouse failed: {errors[0]}")
        return out

    async def _fetch_board_async(
        self,
        client: httpx.AsyncClient,
        board: GreenhouseBoard,
        sem: asyncio.Semaphore,
    ) -> list[JobPost]:
        async with sem:
            return await self._fetch_board_async_inner(client, board)

    async def _fetch_board_async_inner(
        self,
        client: httpx.AsyncClient,
        board: GreenhouseBoard,
    ) -> list[JobPost]:
        params = {"content": "true"} if self.content else None
        url = f"{self.BASE_URL}/{board.token}/jobs"
        data = await self._get_async(client, url, params)
        jobs = data.get("jobs", [])
        out: list[JobPost] = []
        for j in jobs:
            p = self._map(board, j)
            if p:
                out.append(p)
        return out

    async def _get_async(self, client: httpx.AsyncClient, url: str, params=None) -> dict:
        last: Exception | None = None
        for i in range(self.retries):
            try:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last = e
                await asyncio.sleep(1.5 * (i + 1))
        raise RuntimeError(f"Greenhouse failed: {last}")

    def _fetch_board(self, board: GreenhouseBoard) -> list[JobPost]:

        params = {"content": "true"} if self.content else None
        url = f"{self.BASE_URL}/{board.token}/jobs"

        data = self._get(url, params)
        jobs = data.get("jobs", [])

        out: list[JobPost] = []

        for j in jobs:
            p = self._map(board, j)
            if p:
                out.append(p)

        return out

    def _get(self, url: str, params=None) -> dict:

        last = None

        for i in range(self.retries):

            try:
                r = requests.get(url, params=params, timeout=self.timeout)
                r.raise_for_status()
                return r.json()

            except Exception as e:
                last = e
                time.sleep(1.5 * (i + 1))

        raise RuntimeError(f"Greenhouse failed: {last}")

    def _map(self, board: GreenhouseBoard, j: Mapping[str, Any]) -> Optional[JobPost]:

        title = (j.get("title") or "").strip()
        url = (j.get("absolute_url") or "").strip()

        if not title or not url:
            return None

        location = ""

        loc = j.get("location")

        if isinstance(loc, dict):
            location = (loc.get("name") or "").strip()
        elif isinstance(loc, str):
            location = loc.strip()

        description = _extract_description(j.get("content"))

        workplace_type = None

        txt = f"{title} {location} {description}".lower()

        if any(k in txt for k in ["remote", "distributed", "anywhere"]):
            workplace_type = "remote"

        published = _parse_dt(j.get("updated_at"))

        post = JobPost.from_source(
            source="greenhouse",
            source_org=board.token,
            external_id=str(j.get("id") or "").strip() or None,
            title=title,
            company_name=board.company_name,
            location_raw=location,
            url=url,
            workplace_type=workplace_type,
            posted_at=published,
            description_text=description,
            language=_extract_language(j),
            tags=(),
            raw_payload=dict(j),
        )
        validate_canonical(post)
        return post


def _parse_dt(v: Any) -> Optional[datetime]:

    if not isinstance(v, str):
        return None

    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))

        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)

        return d.astimezone(timezone.utc)

    except Exception:
        return None


def _strip_html(text: str) -> str:
    plain = unescape(text)
    plain = re.sub(r"(?i)<br\s*/?>", "\n", plain)
    plain = re.sub(r"(?i)</p>|</div>|</li>|</h[1-6]>", "\n", plain)
    plain = _HTML_TAG_RE.sub(" ", plain)
    plain = _WHITESPACE_RE.sub(" ", plain)
    return plain.strip()


def _extract_description(content: Any) -> str:
    if isinstance(content, str):
        return _strip_html(content)
    if isinstance(content, dict):
        desc_parts: list[str] = []
        for key in ("description", "requirements", "responsibilities", "content"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                desc_parts.append(_strip_html(value))
        return "\n\n".join(part for part in desc_parts if part)
    return ""


def _extract_language(payload: Mapping[str, Any]) -> str | None:
    language = payload.get("language")
    if isinstance(language, str) and language.strip():
        return language.strip()
    return None

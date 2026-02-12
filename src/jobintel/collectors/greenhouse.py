from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
import asyncio
import time
import httpx
import requests

from ..interfaces import Collector
from ..model import JobPost


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

        desc_parts = []

        content = j.get("content")

        if isinstance(content, dict):
            for k in ("description", "requirements", "responsibilities"):
                v = content.get(k)
                if isinstance(v, str) and v.strip():
                    desc_parts.append(v.strip())

        description = "\n\n".join(desc_parts)

        remote = None

        txt = f"{title} {location} {description}".lower()

        if any(k in txt for k in ["remote", "distributed", "anywhere"]):
            remote = True

        published = _parse_dt(j.get("updated_at"))

        return JobPost(
            title=title,
            company=board.company_name,
            location=location,
            url=url,
            source="greenhouse",
            remote=remote,
            published_at=published,
            description=description,
            tags=(),
            raw=dict(j),
        )


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

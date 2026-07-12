from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Mapping

import httpx

from jobintel_next.adapters.greenhouse.client import GreenhouseAPIClient
from jobintel_next.adapters.greenhouse.mapper import CanonicalRawJob, map_greenhouse_job_to_canonical

SOURCE_NAME = "greenhouse"


@dataclass(frozen=True)
class GreenhouseCollectorConfig:
    boards: list[str]
    content: bool = True
    timeout_s: int = 20
    retries: int = 3
    max_concurrency: int = 12


class GreenhouseCollector:
    """Ingestion collector orchestration for Greenhouse boards."""

    def __init__(
        self,
        config: GreenhouseCollectorConfig,
        *,
        client: GreenhouseAPIClient | None = None,
        mapper: Callable[..., CanonicalRawJob | None] = map_greenhouse_job_to_canonical,
    ) -> None:
        self.config = config
        self.client = client or GreenhouseAPIClient(timeout_s=config.timeout_s, retries=config.retries)
        self.mapper = mapper

    def name(self) -> str:
        return SOURCE_NAME

    def fetch(self) -> list[CanonicalRawJob]:
        return asyncio.run(self._fetch_all())

    async def _fetch_all(self) -> list[CanonicalRawJob]:
        boards = self.config.boards
        if not boards:
            return []

        sem = asyncio.Semaphore(self.config.max_concurrency)
        timeout = httpx.Timeout(self.config.timeout_s)
        async with httpx.AsyncClient(timeout=timeout) as http_client:
            tasks = [self._fetch_board(http_client, board, sem) for board in boards]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        out: list[CanonicalRawJob] = []
        for result in results:
            if isinstance(result, list):
                out.extend(result)
        return out

    async def _fetch_board(
        self,
        http_client: httpx.AsyncClient,
        board: str,
        sem: asyncio.Semaphore,
    ) -> list[CanonicalRawJob]:
        async with sem:
            payload = await self.client.fetch_board_jobs_payload(
                http_client,
                board=board,
                content=self.config.content,
            )
            jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
            out: list[CanonicalRawJob] = []
            for row in jobs:
                if not isinstance(row, dict):
                    continue
                mapped = self.mapper(board=board, payload=row)
                if mapped is not None:
                    out.append(mapped)
            return out


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


def build_collector(cfg: Mapping[str, Any]) -> GreenhouseCollector | None:
    if not _as_bool(cfg.get("enabled"), default=True):
        return None

    boards = _as_str_list(cfg.get("boards"))
    if not boards:
        return None

    conf = GreenhouseCollectorConfig(
        boards=boards,
        content=_as_bool(cfg.get("content"), default=True),
        timeout_s=int(cfg.get("timeout_s", 20) or 20),
        retries=int(cfg.get("retries", 3) or 3),
        max_concurrency=int(cfg.get("max_concurrency", 12) or 12),
    )
    return GreenhouseCollector(conf)

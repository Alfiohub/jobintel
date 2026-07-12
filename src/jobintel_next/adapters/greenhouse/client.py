from __future__ import annotations

import asyncio
from typing import Any

import httpx


class GreenhouseAPIClient:
    """HTTP-only client for Greenhouse board API."""

    base_url = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, timeout_s: int = 20, retries: int = 3) -> None:
        self.timeout_s = timeout_s
        self.retries = retries

    async def fetch_board_jobs_payload(
        self,
        client: httpx.AsyncClient,
        *,
        board: str,
        content: bool = True,
    ) -> dict[str, Any]:
        params = {"content": "true"} if content else None
        url = f"{self.base_url}/{board}/jobs"
        return await self._request_json(client, url, params=params)

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        last_exc: Exception | None = None
        for _ in range(self.retries):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                payload = response.json()
                return payload if isinstance(payload, dict) else {}
            except Exception as exc:
                last_exc = exc
                await asyncio.sleep(0.35)
        raise RuntimeError(f"Greenhouse request failed: {last_exc}")

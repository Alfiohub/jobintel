import httpx

from jobintel_next.ingestion.collectors.greenhouse_collector import (
    GreenhouseCollector,
    GreenhouseCollectorConfig,
)


class _FakeClient:
    async def fetch_board_jobs_payload(self, client: httpx.AsyncClient, *, board: str, content: bool = True) -> dict:
        return {
            "jobs": [
                {
                    "id": 1,
                    "title": f"Engineer {board}",
                    "absolute_url": f"https://job-boards.greenhouse.io/{board}/jobs/1",
                    "updated_at": "2026-03-25T01:00:22-04:00",
                    "language": "en",
                    "location": {"name": "Remote"},
                }
            ]
        }


def test_collector_fetch_base_path() -> None:
    collector = GreenhouseCollector(
        GreenhouseCollectorConfig(
            boards=["found", "acme"],
            content=True,
            timeout_s=5,
            retries=1,
            max_concurrency=2,
        ),
        client=_FakeClient(),
    )

    rows = collector.fetch()
    assert len(rows) == 2
    assert {r.source_org for r in rows} == {"found", "acme"}
    assert all(r.source == "greenhouse" for r in rows)

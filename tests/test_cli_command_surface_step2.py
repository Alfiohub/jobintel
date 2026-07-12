from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jobintel_next import cli


def test_parser_official_ingest_run_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(["ingest", "run", "--config", "config/default.yml", "--out", "data/out.jsonl"])
    assert args.group == "ingest"
    assert args.ingest_cmd == "run"
    assert args.config.endswith("default.yml")


@dataclass(frozen=True)
class _Job:
    source: str
    source_org: str
    external_id: str | None
    url: str
    title: str
    company_name: str
    location_raw: str | None
    posted_at: str | None
    language: str | None
    raw_payload: dict


class _Collector:
    def fetch(self) -> list[_Job]:
        return [
            _Job(
                source="greenhouse",
                source_org="found",
                external_id="1",
                url="https://job-boards.greenhouse.io/found/jobs/1",
                title="Data Engineer",
                company_name="found",
                location_raw="Remote",
                posted_at="2026-03-25T05:00:22+00:00",
                language="en",
                raw_payload={"id": 1},
            )
        ]


def test_run_with_yaml_config(monkeypatch, tmp_path: Path) -> None:
    cfg = tmp_path / "cfg.yml"
    cfg.write_text(
        """
sources:
  greenhouse:
    enabled: true
    boards: [found]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(cli, "build_collectors_from_sources", lambda sources: [_Collector()])

    out = tmp_path / "out.jsonl"
    rc = cli.run_ingest_run(cfg, out)
    assert rc == 0
    assert out.exists()
    assert out.read_text(encoding="utf-8").count("\n") == 1


class _CollectorSingle:
    def fetch(self) -> list[_Job]:
        return [
            _Job(
                source="greenhouse",
                source_org="found",
                external_id="2",
                url="https://job-boards.greenhouse.io/found/jobs/2",
                title="Analyst",
                company_name="found",
                location_raw="Remote",
                posted_at="2026-03-25T05:00:22+00:00",
                language="en",
                raw_payload={"id": 2},
            )
        ]


def test_export_single_board(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cli, "build_collector", lambda cfg: _CollectorSingle())
    out = tmp_path / "single.jsonl"
    rc = cli.run_ingest_export(
        source="greenhouse",
        board="found",
        out_path=out,
        content=True,
        timeout_s=None,
        retries=None,
        max_concurrency=None,
    )
    assert rc == 0
    assert out.exists()

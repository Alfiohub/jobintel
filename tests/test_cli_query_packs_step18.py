from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_retrieval_pack_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "retrieval",
            "pack",
            "--input",
            "data/jobs/jobs_indexed_en.jsonl",
            "--pack",
            "python_tech_jobs",
            "--limit",
            "20",
        ]
    )
    assert args.group == "retrieval"
    assert args.retrieval_cmd == "pack"
    assert args.pack == "python_tech_jobs"
    assert args.limit == 20


def test_cli_retrieval_pack_handler_single(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_query_pack(*, input_path, pack_name, limit=None, output_path=None):
        called["input_path"] = str(input_path)
        called["pack_name"] = pack_name
        called["limit"] = limit
        called["output_path"] = None if output_path is None else str(output_path)
        return {"pack_name": pack_name, "matched_rows": 1, "results": []}

    monkeypatch.setattr(cli, "run_query_pack", _fake_run_query_pack)
    rc = cli._cmd_retrieval_pack(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "idx.jsonl"),
                "pack": "python_tech_jobs",
                "limit": 15,
                "out": str(tmp_path / "out.jsonl"),
                "report_dir": str(tmp_path / "docs"),
            },
        )
    )
    assert rc == 0
    assert called["input_path"] == str(tmp_path / "idx.jsonl")
    assert called["pack_name"] == "python_tech_jobs"
    assert called["limit"] == 15
    assert called["output_path"] == str(tmp_path / "out.jsonl")


def test_cli_retrieval_pack_handler_all(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_build_query_packs_report(*, input_path, report_dir, sample_limit):
        called["input_path"] = str(input_path)
        called["report_dir"] = str(report_dir)
        called["sample_limit"] = sample_limit
        return {"input_path": str(input_path)}

    monkeypatch.setattr(cli, "build_query_packs_report", _fake_build_query_packs_report)
    rc = cli._cmd_retrieval_pack(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "idx.jsonl"),
                "pack": "all",
                "limit": 12,
                "out": None,
                "report_dir": str(tmp_path / "docs"),
            },
        )
    )
    assert rc == 0
    assert called["input_path"] == str(tmp_path / "idx.jsonl")
    assert called["report_dir"] == str(tmp_path / "docs")
    assert called["sample_limit"] == 12

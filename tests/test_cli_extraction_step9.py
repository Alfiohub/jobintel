from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_extraction_run_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "extraction",
            "run",
            "--input",
            "data/jobs/jobs_cleaned_en.jsonl",
            "--out",
            "data/jobs/jobs_extracted_en.jsonl",
            "--report-dir",
            "docs",
            "--limit",
            "50",
        ]
    )
    assert args.group == "extraction"
    assert args.extraction_cmd == "run"
    assert args.limit == 50


def test_cli_extraction_run_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_extraction_stage(*, input_path, output_path, report_dir="docs", limit=None, sample_size=5):
        called["input_path"] = str(input_path)
        called["output_path"] = str(output_path)
        called["report_dir"] = str(report_dir)
        called["limit"] = limit
        return {
            "rows_total": 3,
            "invalid_rows": 0,
            "output_path": str(output_path),
        }

    monkeypatch.setattr(cli, "run_extraction_stage", _fake_run_extraction_stage)
    rc = cli._cmd_extraction_run(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "in.jsonl"),
                "out": str(tmp_path / "out.jsonl"),
                "report_dir": str(tmp_path / "docs"),
                "limit": 10,
                "sample_size": 4,
            },
        )
    )
    assert rc == 0
    assert called["limit"] == 10
    assert called["report_dir"] == str(tmp_path / "docs")


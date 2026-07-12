from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_titles_run_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "titles",
            "run",
            "--input-cleaned",
            "data/jobs/jobs_cleaned_en.jsonl",
            "--input-extracted",
            "data/jobs/jobs_extracted_en.jsonl",
            "--out",
            "data/jobs/jobs_titled_en.jsonl",
            "--report-dir",
            "docs",
            "--limit",
            "50",
        ]
    )
    assert args.group == "titles"
    assert args.titles_cmd == "run"
    assert args.limit == 50


def test_cli_titles_run_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_title_stage(
        *,
        input_cleaned_path,
        output_path,
        input_extracted_path=None,
        report_dir="docs",
        limit=None,
        top_k_other=20,
    ):
        called["input_cleaned_path"] = str(input_cleaned_path)
        called["output_path"] = str(output_path)
        called["input_extracted_path"] = None if input_extracted_path is None else str(input_extracted_path)
        called["report_dir"] = str(report_dir)
        called["limit"] = limit
        return {
            "rows_total": 2,
            "invalid_rows": 0,
            "output_path": str(output_path),
        }

    monkeypatch.setattr(cli, "run_title_stage", _fake_run_title_stage)
    rc = cli._cmd_titles_run(
        type(
            "Args",
            (),
            {
                "input_cleaned": str(tmp_path / "cleaned.jsonl"),
                "input_extracted": str(tmp_path / "extracted.jsonl"),
                "out": str(tmp_path / "out.jsonl"),
                "report_dir": str(tmp_path / "docs"),
                "limit": 10,
                "top_k_other": 5,
            },
        )
    )
    assert rc == 0
    assert called["limit"] == 10
    assert called["input_extracted_path"] == str(tmp_path / "extracted.jsonl")


def test_cli_parser_titles_eval_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "titles",
            "eval",
            "--input",
            "data/jobs/jobs_titled_en.jsonl",
            "--outdir",
            "docs",
            "--limit",
            "100",
        ]
    )
    assert args.group == "titles"
    assert args.titles_cmd == "eval"
    assert args.limit == 100


def test_cli_titles_eval_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_title_eval(*, input_path, outdir, limit=None, sample_size=50, top_k=20):
        called["input_path"] = str(input_path)
        called["outdir"] = str(outdir)
        called["limit"] = limit
        return {
            "rows_total": 10,
            "invalid_rows": 0,
        }

    monkeypatch.setattr(cli, "run_title_eval", _fake_run_title_eval)
    rc = cli._cmd_titles_eval(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "in.jsonl"),
                "outdir": str(tmp_path / "docs"),
                "limit": 10,
                "sample_size": 5,
                "top_k": 10,
            },
        )
    )
    assert rc == 0
    assert called["limit"] == 10

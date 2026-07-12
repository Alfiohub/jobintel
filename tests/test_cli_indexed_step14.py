from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_indexed_run_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "indexed",
            "run",
            "--input-canonical",
            "data/jobs/jobs_en_filtered.jsonl",
            "--input-language",
            "data/jobs/jobs_en_filtered.jsonl",
            "--input-cleaned",
            "data/jobs/jobs_cleaned_en.jsonl",
            "--input-extracted",
            "data/jobs/jobs_extracted_en.jsonl",
            "--input-titled",
            "data/jobs/jobs_titled_en.jsonl",
            "--out",
            "data/jobs/jobs_indexed_en.jsonl",
            "--report-dir",
            "docs",
            "--limit",
            "100",
        ]
    )
    assert args.group == "indexed"
    assert args.indexed_cmd == "run"
    assert args.limit == 100


def test_cli_indexed_run_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_indexed_stage(
        *,
        input_canonical_path,
        input_language_path,
        input_cleaned_path,
        input_extracted_path,
        input_titled_path,
        output_path,
        report_dir="docs",
        limit=None,
        sample_size=10,
    ):
        called["input_canonical_path"] = str(input_canonical_path)
        called["input_language_path"] = str(input_language_path)
        called["input_cleaned_path"] = str(input_cleaned_path)
        called["input_extracted_path"] = str(input_extracted_path)
        called["input_titled_path"] = str(input_titled_path)
        called["output_path"] = str(output_path)
        called["report_dir"] = str(report_dir)
        called["limit"] = limit
        return {
            "rows_total": 2,
            "missing_components": 0,
            "output_path": str(output_path),
        }

    monkeypatch.setattr(cli, "run_indexed_stage", _fake_run_indexed_stage)
    rc = cli._cmd_indexed_run(
        type(
            "Args",
            (),
            {
                "input_canonical": str(tmp_path / "canonical.jsonl"),
                "input_language": str(tmp_path / "language.jsonl"),
                "input_cleaned": str(tmp_path / "cleaned.jsonl"),
                "input_extracted": str(tmp_path / "extracted.jsonl"),
                "input_titled": str(tmp_path / "titled.jsonl"),
                "out": str(tmp_path / "indexed.jsonl"),
                "report_dir": str(tmp_path / "docs"),
                "limit": 10,
                "sample_size": 4,
            },
        )
    )
    assert rc == 0
    assert called["limit"] == 10
    assert called["input_titled_path"] == str(tmp_path / "titled.jsonl")

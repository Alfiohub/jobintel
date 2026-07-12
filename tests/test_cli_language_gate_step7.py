from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_language_gate_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "language",
            "gate",
            "--input",
            "data/in.jsonl",
            "--outdir",
            "data/jobs",
            "--report-dir",
            "docs",
            "--limit",
            "100",
        ]
    )
    assert args.group == "language"
    assert args.language_cmd == "gate"
    assert args.limit == 100


def test_cli_language_gate_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_language_gate(*, input_path, outdir, report_dir="docs", limit=None, top_k=20):
        called["input_path"] = str(input_path)
        called["outdir"] = str(outdir)
        called["report_dir"] = str(report_dir)
        called["limit"] = limit
        return {
            "rows_total": 10,
            "rows_en": 7,
            "rows_non_en": 2,
            "rows_unknown": 1,
            "output_files": {
                "en": "data/jobs/jobs_en_filtered.jsonl",
                "non_en": "data/jobs/jobs_non_en.jsonl",
                "unknown": "data/jobs/jobs_unknown_language.jsonl",
            },
        }

    monkeypatch.setattr(cli, "run_language_gate", _fake_run_language_gate)

    rc = cli._cmd_language_gate(
        type(
            "Args",
            (),
            {
                "input": str(tmp_path / "in.jsonl"),
                "outdir": str(tmp_path / "jobs"),
                "report_dir": str(tmp_path / "docs"),
                "limit": 10,
                "top_k": 10,
            },
        )
    )

    assert rc == 0
    assert called["limit"] == 10
    assert called["report_dir"] == str(tmp_path / "docs")


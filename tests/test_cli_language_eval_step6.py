from __future__ import annotations

from pathlib import Path

from jobintel_next import cli


def test_cli_parser_language_eval_shape() -> None:
    parser = cli.build_parser()
    args = parser.parse_args([
        "language",
        "eval",
        "--input",
        "data/in.jsonl",
        "--outdir",
        "docs",
        "--limit",
        "100",
    ])
    assert args.group == "language"
    assert args.language_cmd == "eval"
    assert args.limit == 100


def test_cli_language_eval_handler(monkeypatch, tmp_path: Path) -> None:
    called = {}

    def _fake_run_language_eval(*, input_path, outdir, limit=None, sample_size=50, top_k=20):
        called["input_path"] = str(input_path)
        called["outdir"] = str(outdir)
        called["limit"] = limit
        return {
            "rows_total": 10,
            "rows_en": 7,
            "rows_non_en": 2,
            "rows_unknown": 1,
        }

    monkeypatch.setattr(cli, "run_language_eval", _fake_run_language_eval)

    rc = cli._cmd_language_eval(
        type("Args", (), {
            "input": str(tmp_path / "in.jsonl"),
            "outdir": str(tmp_path / "out"),
            "limit": 10,
            "sample_size": 5,
            "top_k": 10,
        })
    )

    assert rc == 0
    assert called["limit"] == 10

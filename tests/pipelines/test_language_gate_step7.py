from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.language.gate import run_language_gate


def _read_jsonl(path: Path) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                out.append(json.loads(s))
    return out


def test_language_gate_routes_and_adds_fields(tmp_path: Path) -> None:
    input_path = tmp_path / "canonical.jsonl"
    rows = [
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/1",
            "title": "Senior Data Engineer",
            "company_name": "Acme",
            "language_hint": "en",
            "description_raw": "We are hiring for a data engineering role with product collaboration.",
            "raw_payload": {"id": 1},
        },
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/2",
            "title": "Ingénieur Données",
            "company_name": "Acme",
            "description_raw": "Nous recherchons une personne pour travailler avec les équipes.",
            "raw_payload": {"id": 2},
        },
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/3",
            "title": "Manager",
            "company_name": "Acme",
            "description_raw": "",
            "raw_payload": {"id": 3},
        },
    ]
    with input_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    outdir = tmp_path / "jobs"
    report_dir = tmp_path / "docs"
    report = run_language_gate(input_path=input_path, outdir=outdir, report_dir=report_dir)

    assert report["rows_total"] == 3
    assert report["rows_en"] >= 1
    assert report["rows_non_en"] >= 1
    assert report["rows_unknown"] >= 1

    en_rows = _read_jsonl(outdir / "jobs_en_filtered.jsonl")
    non_en_rows = _read_jsonl(outdir / "jobs_non_en.jsonl")
    unknown_rows = _read_jsonl(outdir / "jobs_unknown_language.jsonl")
    assert len(en_rows) + len(non_en_rows) + len(unknown_rows) == 3

    for row in en_rows + non_en_rows + unknown_rows:
        assert "language_bucket" in row
        assert "language_reason" in row
        assert "language_code" in row
        assert "language_confidence" in row

    assert (report_dir / "language_gate_step7.json").exists()
    assert (report_dir / "language_gate_step7.md").exists()


from __future__ import annotations

import json
from pathlib import Path

from jobintel_next.pipelines.language.eval import run_language_eval


def test_language_eval_outputs_reports_and_samples(tmp_path: Path) -> None:
    input_path = tmp_path / "canonical.jsonl"
    rows = [
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/1",
            "title": "Senior Data Engineer",
            "company_name": "Acme",
            "language_hint": "en",
            "description_raw": "We are looking for you and your team to build systems.",
            "raw_payload": {"id": 1},
        },
        {
            "source": "greenhouse",
            "source_org": "acme",
            "url": "https://example.com/2",
            "title": "Ingénieur Données",
            "company_name": "Acme",
            "description_raw": "Nous recherchons une personne avec des compétences pour le produit.",
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

    outdir = tmp_path / "out"
    report = run_language_eval(input_path=input_path, outdir=outdir, sample_size=10, top_k=5)

    assert report["rows_total"] == 3
    assert report["rows_en"] >= 1
    assert report["rows_non_en"] >= 1
    assert report["rows_unknown"] >= 1

    assert (outdir / "language_eval_step6.json").exists()
    assert (outdir / "language_eval_step6.md").exists()
    assert (outdir / "sample_en.jsonl").exists()
    assert (outdir / "sample_non_en.jsonl").exists()
    assert (outdir / "sample_unknown.jsonl").exists()

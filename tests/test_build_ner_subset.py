from __future__ import annotations

from automation.legacy_ner.build_ner_subset import looks_english


def test_looks_english_accepts_explicit_language() -> None:
    row = {
        "title": "Ingénieur Données",
        "description_text": "",
        "language": "en",
    }

    assert looks_english(row, min_hits=5) is True


def test_looks_english_falls_back_to_raw_payload() -> None:
    row = {
        "title": "Data Engineer",
        "description_text": None,
        "location_raw": "Remote",
        "raw_payload": {
            "language": "en",
            "content": "<p>Experience with Python, SQL, and distributed systems.</p>",
        },
    }

    assert looks_english(row, min_hits=5) is True

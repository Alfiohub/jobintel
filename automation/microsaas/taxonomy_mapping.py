from __future__ import annotations

from typing import Any


# Placeholder mapping layer: internal schema remains primary.
# This module enriches roles with an optional external taxonomy projection.
_RULES: list[dict[str, str]] = [
    {
        "normalized_title": "data_engineer",
        "taxonomy_source": "esco",
        "taxonomy_code": "2512.6",
        "taxonomy_label": "Data Engineer",
    },
    {
        "normalized_title": "data_scientist",
        "taxonomy_source": "esco",
        "taxonomy_code": "2511.7",
        "taxonomy_label": "Data Scientist",
    },
    {
        "normalized_title": "software_engineer",
        "taxonomy_source": "esco",
        "taxonomy_code": "2512.2",
        "taxonomy_label": "Software Developer",
    },
    {
        "normalized_title": "product_manager",
        "taxonomy_source": "onet",
        "taxonomy_code": "11-2021.00",
        "taxonomy_label": "Marketing Managers",
    },
]


def map_taxonomy(normalized_title: str, role_family: str, occupation_group: str) -> dict[str, Any]:
    nt = str(normalized_title or "").strip().lower()
    rf = str(role_family or "").strip().lower()
    og = str(occupation_group or "").strip().lower()

    for rule in _RULES:
        if nt and nt == rule["normalized_title"]:
            return {
                "taxonomy_source": rule["taxonomy_source"],
                "taxonomy_code": rule["taxonomy_code"],
                "taxonomy_label": rule["taxonomy_label"],
                "taxonomy_match_confidence": 0.9,
            }

    # Lightweight family/group fallback: provides weak but usable mapping.
    if rf == "data_analytics" or og == "data":
        return {
            "taxonomy_source": "esco",
            "taxonomy_code": "2521",
            "taxonomy_label": "Database and network professionals",
            "taxonomy_match_confidence": 0.45,
        }
    if rf == "software_engineering" or og == "engineering":
        return {
            "taxonomy_source": "esco",
            "taxonomy_code": "2512",
            "taxonomy_label": "Software developers and analysts",
            "taxonomy_match_confidence": 0.4,
        }

    return {
        "taxonomy_source": None,
        "taxonomy_code": None,
        "taxonomy_label": None,
        "taxonomy_match_confidence": 0.0,
    }


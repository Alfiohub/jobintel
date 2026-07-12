from __future__ import annotations

import os
import sqlite3
from functools import lru_cache
from pathlib import Path
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


def _db_candidates() -> list[Path]:
    out: list[Path] = []
    env_db = str(os.getenv("JOBINTEL_DB_PATH", "")).strip()
    if env_db:
        out.append(Path(env_db))
    out.extend(
        [
            Path("data/jobintel_microsaas_loccheck_2k_v6r_plus.sqlite"),
            Path("data/jobintel_microsaas_loccheck_2k_prod_candidate.sqlite"),
            Path("data/jobintel_microsaas.sqlite"),
        ]
    )
    seen: set[str] = set()
    dedup: list[Path] = []
    for p in out:
        k = str(p)
        if k in seen:
            continue
        seen.add(k)
        dedup.append(p)
    return dedup


@lru_cache(maxsize=1)
def _load_esco_crosswalk() -> dict[str, tuple[str, str, float]]:
    for db_path in _db_candidates():
        if not db_path.exists():
            continue
        try:
            con = sqlite3.connect(str(db_path))
            cur = con.cursor()
            cur.execute(
                """
                SELECT normalized_title, esco_id, esco_label, mapping_confidence
                FROM title_esco_crosswalk
                WHERE normalized_title IS NOT NULL AND normalized_title <> ''
                """
            )
            rows = cur.fetchall()
            con.close()
        except sqlite3.Error:
            continue
        if not rows:
            continue
        out: dict[str, tuple[str, str, float]] = {}
        for nt, esco_id, esco_label, conf in rows:
            key = str(nt or "").strip().lower()
            if not key:
                continue
            code = str(esco_id or "").strip()
            label = str(esco_label or "").strip()
            try:
                confidence = float(conf) if conf is not None else 0.95
            except Exception:
                confidence = 0.95
            out[key] = (code, label, confidence)
        if out:
            return out
    return {}


def map_taxonomy(normalized_title: str, role_family: str, occupation_group: str) -> dict[str, Any]:
    nt = str(normalized_title or "").strip().lower()
    rf = str(role_family or "").strip().lower()
    og = str(occupation_group or "").strip().lower()

    # 1) Prefer DB-driven ESCO crosswalk when available.
    crosswalk = _load_esco_crosswalk()
    if nt and nt in crosswalk:
        code, label, confidence = crosswalk[nt]
        return {
            "taxonomy_source": "esco",
            "taxonomy_code": code or None,
            "taxonomy_label": label or None,
            "taxonomy_match_confidence": confidence,
        }

    # 2) Static fallback rules.
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

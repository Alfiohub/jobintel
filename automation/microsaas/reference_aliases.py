from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _reference_path(name: str) -> Path:
    return _repo_root() / "data" / "reference" / name


@lru_cache(maxsize=1)
def _country_aliases_from_file() -> dict[str, str]:
    out: dict[str, str] = {}
    p = _reference_path("country_aliases.csv")
    if not p.exists():
        return out

    with p.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            alias = (row.get("alias") or "").strip().lower()
            iso2 = (row.get("iso2") or "").strip().upper()
            if not alias:
                continue
            if len(iso2) != 2 or not iso2.isalpha():
                continue
            out[alias] = iso2
    return out


@lru_cache(maxsize=1)
def _currency_aliases_from_file() -> dict[str, str]:
    out: dict[str, str] = {}
    p = _reference_path("currency_aliases.csv")
    if not p.exists():
        return out

    with p.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            iso3 = (row.get("iso3") or "").strip().upper()
            alias = (row.get("alias") or "").strip().lower()
            if not alias:
                continue
            if len(iso3) != 3 or not iso3.isalpha():
                continue
            out[alias] = iso3
    return out


def load_country_aliases(base: dict[str, str] | None = None) -> dict[str, str]:
    out = dict(base or {})
    out.update(_country_aliases_from_file())
    return out


def load_currency_aliases(base: dict[str, str] | None = None) -> dict[str, str]:
    out = dict(base or {})
    out.update(_currency_aliases_from_file())
    return out

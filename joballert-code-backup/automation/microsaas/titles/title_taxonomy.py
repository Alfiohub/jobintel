from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Dict, Set


DEFAULT_TAXONOMY_CSV = Path("docs/taxonomy_v1_final.csv")


class TitleTaxonomy:
    def __init__(self, csv_path: Path = DEFAULT_TAXONOMY_CSV) -> None:
        self.csv_path = Path(csv_path)
        self._role_families: Set[str] = set()
        self._normalized_titles: Set[str] = set()
        self._title_to_family: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"taxonomy csv not found: {self.csv_path}")
        with self.csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                family = str(row.get("role_family") or "").strip().lower()
                title = str(row.get("normalized_title") or "").strip().lower()
                if not family or not title:
                    continue
                self._role_families.add(family)
                self._normalized_titles.add(title)
                self._title_to_family[title] = family

    @property
    def role_families(self) -> Set[str]:
        return set(self._role_families)

    @property
    def normalized_titles(self) -> Set[str]:
        return set(self._normalized_titles)

    @property
    def valid_mapping(self) -> Dict[str, str]:
        return dict(self._title_to_family)

    def validate_mapping(self, normalized_title: str, role_family: str) -> bool:
        nt = str(normalized_title or "").strip().lower()
        rf = str(role_family or "").strip().lower()
        if not nt or not rf:
            return False
        return self._title_to_family.get(nt) == rf


@lru_cache(maxsize=1)
def get_default_taxonomy() -> TitleTaxonomy:
    return TitleTaxonomy()

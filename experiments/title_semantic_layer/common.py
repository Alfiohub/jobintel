from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

_WORD_RE = re.compile(r"[a-z0-9]+")
_PUNCT_RE = re.compile(r"[^a-z0-9\s]+")
_SPACE_RE = re.compile(r"\s+")
_LOCATION_TAIL_RE = re.compile(r"\s*[-,]\s*[a-z .']+,\s*[a-z]{2}\s*$")
_SENIORITY_RE = re.compile(r"\b(senior|sr\.?|staff|principal|lead|junior|jr\.?|associate)\b")
_ROMAN_RE = re.compile(r"\b(i|ii|iii|iv|v|vi|vii|viii|ix|x)\b")

AMBIGUOUS_TOKENS = {
    "manager",
    "analyst",
    "specialist",
    "consultant",
    "partner",
    "coordinator",
    "lead",
    "engineer",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def normalize_title(text: str) -> str:
    s = (text or "").lower().strip()
    s = _LOCATION_TAIL_RE.sub("", s)
    s = _PUNCT_RE.sub(" ", s)
    s = _SENIORITY_RE.sub(" ", s)
    s = _ROMAN_RE.sub(" ", s)
    s = _SPACE_RE.sub(" ", s).strip()
    return s


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


def cosine_sparse(vec_a: Counter[int], vec_b: Counter[int]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = 0.0
    for k, av in vec_a.items():
        dot += av * vec_b.get(k, 0.0)
    na = math.sqrt(sum(v * v for v in vec_a.values()))
    nb = math.sqrt(sum(v * v for v in vec_b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def hashed_ngram_vector(text: str, n: int = 3, dim: int = 2048) -> Counter[int]:
    tokens = tokenize(normalize_title(text))
    if not tokens:
        return Counter()
    joined = " ".join(tokens)
    grams: list[str] = []
    if len(joined) < n:
        grams.append(joined)
    else:
        grams.extend(joined[i : i + n] for i in range(0, len(joined) - n + 1))
    out: Counter[int] = Counter()
    for gram in grams:
        out[hash(gram) % dim] += 1
    return out


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(r) for r in reader]

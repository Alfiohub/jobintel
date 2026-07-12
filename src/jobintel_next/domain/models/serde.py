from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, TypeVar

T = TypeVar("T")


def model_to_jsonl_line(model: Any) -> str:
    """Serialize dataclass-like model to JSONL line."""
    return json.dumps(asdict(model), ensure_ascii=False)


def model_from_dict(model_type: type[T], payload: dict[str, Any]) -> T:
    """Lightweight constructor helper for domain dataclasses."""
    return model_type(**payload)

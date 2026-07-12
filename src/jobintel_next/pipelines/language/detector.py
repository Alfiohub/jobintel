from __future__ import annotations

from dataclasses import dataclass

try:
    from lingua import Language, LanguageDetectorBuilder
except Exception:  # pragma: no cover
    Language = None  # type: ignore[assignment]
    LanguageDetectorBuilder = None  # type: ignore[assignment]


@dataclass(frozen=True)
class DetectorDecision:
    language_code: str | None
    confidence: float | None
    margin: float | None
    reliable: bool


_LANGUAGE_BY_CODE = {
    "en": "ENGLISH",
    "de": "GERMAN",
    "fr": "FRENCH",
    "it": "ITALIAN",
    "es": "SPANISH",
    "nl": "DUTCH",
    "pt": "PORTUGUESE",
}


def _build_detector():
    if Language is None or LanguageDetectorBuilder is None:
        return None
    langs = []
    for name in _LANGUAGE_BY_CODE.values():
        lang = getattr(Language, name, None)
        if lang is not None:
            langs.append(lang)
    if not langs:
        return None
    return (
        LanguageDetectorBuilder.from_languages(*langs)
        .with_minimum_relative_distance(0.12)
        .build()
    )


_DETECTOR = _build_detector()


def detect_language(text: str) -> DetectorDecision:
    content = str(text or "").strip()
    if not content or _DETECTOR is None:
        return DetectorDecision(language_code=None, confidence=None, margin=None, reliable=False)

    try:
        values = list(_DETECTOR.compute_language_confidence_values(content))
    except Exception:
        return DetectorDecision(language_code=None, confidence=None, margin=None, reliable=False)

    if not values:
        return DetectorDecision(language_code=None, confidence=None, margin=None, reliable=False)

    top = values[0]
    top_lang_name = str(getattr(top, "language", "")).split(".")[-1].upper()
    top_score = float(getattr(top, "value", 0.0))

    reverse = {v: k for k, v in _LANGUAGE_BY_CODE.items()}
    language_code = reverse.get(top_lang_name)

    second_score = float(getattr(values[1], "value", 0.0)) if len(values) > 1 else 0.0
    margin = max(0.0, top_score - second_score)
    reliable = bool(language_code and top_score >= 0.65 and margin >= 0.12)

    return DetectorDecision(
        language_code=language_code,
        confidence=round(top_score, 3),
        margin=round(margin, 3),
        reliable=reliable,
    )


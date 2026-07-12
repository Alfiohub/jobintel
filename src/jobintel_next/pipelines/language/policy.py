from __future__ import annotations

import re
from typing import Iterable

from jobintel_next.domain.models import CanonicalRawJob, LanguageDecision

from .detector import detect_language
from .text_utils import text_for_language_decision


_TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ']+")

_HINT_EN = {"en", "eng", "english"}
_HINT_NON_EN = {
    "de": "de",
    "ger": "de",
    "german": "de",
    "fr": "fr",
    "fre": "fr",
    "french": "fr",
    "it": "it",
    "italian": "it",
    "es": "es",
    "spa": "es",
    "spanish": "es",
    "pt": "pt",
    "por": "pt",
    "portuguese": "pt",
    "nl": "nl",
    "dut": "nl",
    "dutch": "nl",
}

_STOPWORDS = {
    "en": {"the", "and", "with", "for", "you", "your", "will", "from", "this", "that", "are", "our"},
    "de": {"und", "mit", "für", "der", "die", "das", "ist", "eine", "einen", "wir", "du", "nicht"},
    "fr": {"le", "la", "les", "des", "avec", "pour", "vous", "nous", "est", "une", "dans", "pas"},
    "it": {"con", "per", "che", "non", "una", "della", "delle", "noi", "voi", "sono", "nel", "dei"},
    "es": {"con", "para", "que", "una", "las", "los", "del", "por", "este", "esta", "nos", "como"},
    "pt": {"com", "para", "que", "uma", "não", "dos", "das", "este", "esta", "você", "nós", "como"},
    "nl": {"met", "voor", "een", "niet", "van", "de", "het", "wij", "jij", "dit", "dat", "als"},
}


def _norm_hint(value: str | None) -> str:
    v = str(value or "").strip().lower()
    return re.sub(r"[^a-z]", "", v)


def _tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in _TOKEN_RE.finditer(text)]


def _count_matches(tokens: Iterable[str], lexicon: set[str]) -> int:
    return sum(1 for t in tokens if t in lexicon)


def _hint_bucket_and_code(hint: str | None) -> tuple[str | None, str | None]:
    normalized = _norm_hint(hint)
    if normalized in _HINT_EN:
        return "en", "en"
    if normalized in _HINT_NON_EN:
        return "non_en", _HINT_NON_EN[normalized]
    return None, None


def _heuristics_bucket(tokens: list[str]) -> tuple[str | None, str | None]:
    counts = {lang: _count_matches(tokens, words) for lang, words in _STOPWORDS.items()}
    en_count = counts.get("en", 0)

    non_en_lang, non_en_count = "", 0
    for lang, count in counts.items():
        if lang == "en":
            continue
        if count > non_en_count:
            non_en_lang, non_en_count = lang, count

    if en_count >= 3 and en_count >= non_en_count + 1:
        return "en", "text_stopwords_en"
    if non_en_count >= 3 and non_en_count >= en_count + 1:
        return "non_en", "text_stopwords_non_en"
    return None, None


def _confidence(base: float, *extras: float) -> float:
    return round(min(0.98, max(base, *extras)), 3)


def decide_language(job: CanonicalRawJob) -> LanguageDecision:
    hint_bucket, hint_code = _hint_bucket_and_code(job.language_hint)
    text = text_for_language_decision(job.title, job.description_raw)
    tokens = _tokenize(text)
    if len(tokens) < 4 or len(text) < 20:
        if hint_bucket:
            return LanguageDecision(
                url=job.url,
                bucket="unknown",
                reason="hint_without_enough_text",
                language_code=hint_code,
                confidence=0.2,
            )
        return LanguageDecision(
            url=job.url,
            bucket="unknown",
            reason="text_too_short_or_ambiguous",
            language_code=None,
            confidence=0.1,
        )

    detector = detect_language(text)
    detector_bucket = None
    if detector.language_code:
        detector_bucket = "en" if detector.language_code == "en" else "non_en"

    heur_bucket, heur_reason = _heuristics_bucket(tokens)

    if hint_bucket and detector_bucket and detector.reliable and hint_bucket == detector_bucket:
        return LanguageDecision(
            url=job.url,
            bucket=detector_bucket,
            reason="hint_detector_agree",
            language_code=detector.language_code,
            confidence=_confidence(0.88, detector.confidence or 0.0),
        )

    if hint_bucket and detector_bucket and detector.reliable and hint_bucket != detector_bucket:
        if heur_bucket == detector_bucket or (detector.confidence or 0.0) >= 0.85:
            return LanguageDecision(
                url=job.url,
                bucket=detector_bucket,
                reason="hint_detector_disagree_detector_override",
                language_code=detector.language_code,
                confidence=_confidence(0.8, detector.confidence or 0.0),
            )
        return LanguageDecision(
            url=job.url,
            bucket="unknown",
            reason="hint_detector_conflict",
            language_code=None,
            confidence=0.3,
        )

    if detector_bucket and detector.reliable:
        if heur_bucket and heur_bucket != detector_bucket:
            return LanguageDecision(
                url=job.url,
                bucket="unknown",
                reason="detector_heuristics_conflict",
                language_code=None,
                confidence=0.35,
            )
        return LanguageDecision(
            url=job.url,
            bucket=detector_bucket,
            reason="detector_primary",
            language_code=detector.language_code,
            confidence=_confidence(0.75, detector.confidence or 0.0),
        )

    if heur_bucket and heur_reason:
        code = "en" if heur_bucket == "en" else detector.language_code
        return LanguageDecision(
            url=job.url,
            bucket=heur_bucket,
            reason=heur_reason,
            language_code=code,
            confidence=0.62,
        )

    if hint_bucket:
        return LanguageDecision(
            url=job.url,
            bucket="unknown",
            reason="hint_without_text_support",
            language_code=hint_code,
            confidence=0.25,
        )

    return LanguageDecision(
        url=job.url,
        bucket="unknown",
        reason="low_signal_mixed_or_ambiguous",
        language_code=None,
        confidence=0.2,
    )

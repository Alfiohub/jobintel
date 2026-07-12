from __future__ import annotations

from jobintel_next.domain.models import CanonicalRawJob
from jobintel_next.pipelines.language import LanguageStage, decide_language


def _job(
    *,
    title: str,
    description_raw: str | None,
    language_hint: str | None = None,
    url: str = "https://example.com/job/1",
) -> CanonicalRawJob:
    return CanonicalRawJob(
        source="greenhouse",
        source_org="acme",
        url=url,
        title=title,
        company_name="Acme",
        raw_payload={"title": title},
        language_hint=language_hint,
        description_raw=description_raw,
    )


def test_english_clear_text() -> None:
    job = _job(
        title="Senior Data Engineer",
        description_raw=(
            "We are looking for you and your team to build data systems. "
            "This role will work with the product and the platform team."
        ),
    )
    decision = decide_language(job)
    assert decision.bucket == "en"
    assert decision.reason in {"detector_primary", "hint_detector_agree", "text_stopwords_en"}
    assert decision.language_code == "en"


def test_non_english_clear_text() -> None:
    job = _job(
        title="Ingénieur Données",
        description_raw=(
            "Nous recherchons une personne avec des compétences techniques "
            "pour le développement avec les équipes et la plateforme."
        ),
    )
    decision = decide_language(job)
    assert decision.bucket == "non_en"
    assert decision.reason in {"detector_primary", "hint_detector_agree", "text_stopwords_non_en"}
    assert decision.language_code in {"fr", "it", "es", "pt", "de", "nl"}


def test_ambiguous_text_goes_unknown() -> None:
    job = _job(title="Manager", description_raw=None)
    decision = decide_language(job)
    assert decision.bucket == "unknown"
    assert decision.reason in {"text_too_short_or_ambiguous", "low_signal_mixed_or_ambiguous"}


def test_hint_en_with_non_english_text_is_not_blindly_en() -> None:
    job = _job(
        title="Chef de projet",
        description_raw="Nous cherchons une personne avec des compétences pour le produit.",
        language_hint="en",
    )
    decision = decide_language(job)
    assert decision.bucket in {"non_en", "unknown"}
    assert decision.reason in {"hint_detector_disagree_detector_override", "hint_detector_conflict", "hint_without_text_support"}


def test_hint_non_en_with_english_text_is_not_blindly_non_en() -> None:
    job = _job(
        title="Account Executive, Mid-Market",
        description_raw="We are hiring an account executive to work with customers across markets.",
        language_hint="de",
    )
    decision = decide_language(job)
    assert decision.bucket in {"en", "unknown"}
    assert decision.reason in {"hint_detector_disagree_detector_override", "hint_detector_conflict", "hint_without_text_support"}


def test_no_hint_english_text_goes_en() -> None:
    job = _job(
        title="Backend Engineer",
        description_raw="You will build APIs and work with our team on product features.",
    )
    decision = decide_language(job)
    assert decision.bucket == "en"


def test_no_hint_non_english_text_goes_non_en() -> None:
    job = _job(
        title="Ingeniero de Datos",
        description_raw="Buscamos una persona con experiencia para trabajar con equipos y producto.",
    )
    decision = decide_language(job)
    assert decision.bucket == "non_en"


def test_hint_en_with_english_text_goes_en() -> None:
    job = _job(
        title="Senior Product Manager",
        description_raw="You will work with engineering and design teams to deliver product outcomes.",
        language_hint="en",
    )
    decision = decide_language(job)
    assert decision.bucket == "en"
    assert decision.reason in {"hint_detector_agree", "detector_primary", "text_stopwords_en"}


def test_html_escaped_description_is_handled() -> None:
    job = _job(
        title="Analyste",
        description_raw=(
            "&lt;p&gt;Nous recherchons une personne avec des compétences pour le produit "
            "et la plateforme avec les équipes.&lt;/p&gt;"
        ),
    )
    stage = LanguageStage()
    decision = stage.run_one(job)
    assert decision.bucket == "non_en"
    assert decision.reason in {"detector_primary", "hint_detector_agree", "text_stopwords_non_en"}

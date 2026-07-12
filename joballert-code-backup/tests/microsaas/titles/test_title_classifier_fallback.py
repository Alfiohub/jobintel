from automation.microsaas.titles.title_classifier import TitleClassifier


def test_generic_quality_assurance_falls_to_other() -> None:
    c = TitleClassifier()
    r = c.classify("Quality Assurance")
    assert r.normalized_title == "other"
    assert r.role_family == "other"
    assert r.classification_status == "other"

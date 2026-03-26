from automation.microsaas.titles.title_classifier import TitleClassifier


def test_ambiguous_title_falls_to_other() -> None:
    c = TitleClassifier()
    r = c.classify("QA Engineer")
    assert r.normalized_title == "other"
    assert r.role_family == "other"
    assert r.classification_status == "other"

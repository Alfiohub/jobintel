from automation.microsaas.titles.title_classifier import TitleClassifier


def test_rule_match_specific_architect() -> None:
    c = TitleClassifier()
    r = c.classify("Partner Innovation Architect")
    assert r.normalized_title == "solutions_architect"
    assert r.role_family == "architecture"
    assert r.classification_status == "matched"
    assert r.matched_rule_id == "arch_partner_innovation"

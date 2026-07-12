from __future__ import annotations

from jobintel_next.domain.models import TitleClassification

from .location_noise import strip_simple_location_noise
from .rules import TitleRule, get_rules
from .taxonomy import TitleTaxonomy, get_default_taxonomy
from .text_utils import normalize_title_for_match
from .variants import normalize_variants


class TitleClassifier:
    def __init__(self, *, taxonomy: TitleTaxonomy | None = None, rules: list[TitleRule] | None = None) -> None:
        self.taxonomy = taxonomy or get_default_taxonomy()
        self.rules = rules or get_rules()

    def classify(self, *, url: str, title_clean: str) -> TitleClassification:
        t = normalize_title_for_match(title_clean)
        t = normalize_variants(t)
        t = strip_simple_location_noise(t)

        for rule in self.rules:
            if not rule.matches(t):
                continue
            if self.taxonomy.validate_mapping(rule.normalized_title, rule.role_family):
                is_other = rule.normalized_title == "other"
                is_non_role = rule.normalized_title == "non_role_recruiting_entry"
                return TitleClassification(
                    url=url,
                    normalized_title=rule.normalized_title,
                    role_family=rule.role_family,
                    classification_status="non_role" if is_non_role else ("other" if is_other else "matched"),
                    match_method=rule.match_method,  # type: ignore[arg-type]
                    confidence=0.1 if is_other else (0.98 if is_non_role else (0.95 if rule.match_method == "rule_exact" else 0.85)),
                    matched_rule_id=rule.rule_id,
                    notes=["non_role_recruiting_entry"] if is_non_role else [],
                )
            return TitleClassification(
                url=url,
                normalized_title="other",
                role_family="other",
                classification_status="other",
                match_method="fallback",
                confidence=0.1,
                matched_rule_id=rule.rule_id,
                notes=["invalid_taxonomy_mapping"],
            )

        return TitleClassification(
            url=url,
            normalized_title="other",
            role_family="other",
            classification_status="other",
            match_method="fallback",
            confidence=0.1,
            matched_rule_id=None,
            notes=["no_title_rule_match"],
        )

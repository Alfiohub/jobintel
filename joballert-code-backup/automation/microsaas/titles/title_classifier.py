from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .title_cleaning import clean_title, normalize_for_match
from .title_location_noise import strip_simple_location_noise
from .title_rules import TitleRule, get_rules
from .title_schema import TitleNormalizationResult
from .title_taxonomy import TitleTaxonomy, get_default_taxonomy
from .title_variants import normalize_lexical_variants, strip_seniority_tokens


@dataclass(frozen=True)
class _Candidate:
    normalized_title: str
    role_family: str
    status: str
    method: str
    confidence: float
    rule_id: Optional[str] = None
    notes: List[str] = field(default_factory=list)


def _confidence_for(*, classification_status: str, match_method: str) -> float:
    # Single confidence policy across subsystem:
    # rule_exact=0.95, rule_pattern=0.85, fallback=0.55, other=0.10
    if classification_status == "other":
        return 0.10
    if match_method == "rule_exact":
        return 0.95
    if match_method == "rule_pattern":
        return 0.85
    return 0.55


def _fallback_classify(text: str) -> _Candidate:
    # Controlled fallback only; avoid forcing ambiguous titles.
    if re.search(r"\bdata\b|\banalytics?\b|\bbi\b|\bbusiness intelligence\b", text):
        if re.search(r"\bdirector\b|\bhead\b|\bvp\b", text):
            return _Candidate("analytics_director", "data_analytics", "fallback", "fallback", 0.55, notes=["fallback_data_director"])
        if re.search(r"\bmanager\b|\blead\b", text):
            return _Candidate("analytics_manager", "data_analytics", "fallback", "fallback", 0.55, notes=["fallback_data_manager"])
        if re.search(r"\bengineer\b", text):
            return _Candidate("analytics_engineer", "data_analytics", "fallback", "fallback", 0.55, notes=["fallback_data_engineer"])
        return _Candidate("data_analyst", "data_analytics", "fallback", "fallback", 0.55, notes=["fallback_data"])

    if re.search(r"\bcounsel\b|\battorney\b|\blegal\b", text):
        return _Candidate("legal_counsel", "legal", "fallback", "fallback", 0.55, notes=["fallback_legal"])

    if re.search(r"\baccountant\b|\bcontroller\b|\bauditor\b|\bfinance\b", text):
        if re.search(r"\banalyst\b", text):
            return _Candidate("financial_analyst", "finance", "fallback", "fallback", 0.55, notes=["fallback_finance_analyst"])
        return _Candidate("accountant", "finance", "fallback", "fallback", 0.55, notes=["fallback_finance"])

    if re.search(r"\bseo\b|\bmarketing\b|\bcontent\b", text):
        return _Candidate("marketing_specialist", "marketing", "fallback", "fallback", 0.55, notes=["fallback_marketing"])

    if re.search(r"\brecruiter\b|\btalent acquisition\b|\bpeople partner\b", text):
        return _Candidate("technical_recruiter", "recruiting", "fallback", "fallback", 0.55, notes=["fallback_recruiting"])

    if re.search(r"\boperations?\b|\bfulfillment\b", text):
        return _Candidate("operations_specialist", "operations", "fallback", "fallback", 0.55, notes=["fallback_operations"])

    if "manager" in text:
        return _Candidate("other", "other", "other", "fallback", 0.10, notes=["fallback_manager_ambiguous"])

    if "engineer" in text or "developer" in text:
        return _Candidate("software_engineer", "software_engineering", "fallback", "fallback", 0.55, notes=["fallback_engineer"])

    return _Candidate("other", "other", "other", "fallback", 0.10, notes=["fallback_other"])


class TitleClassifier:
    def __init__(self, taxonomy: Optional[TitleTaxonomy] = None, rules: Optional[List[TitleRule]] = None) -> None:
        self.taxonomy = taxonomy or get_default_taxonomy()
        self.rules = rules or get_rules()

    def classify(self, title_raw: str) -> TitleNormalizationResult:
        title_clean = clean_title(title_raw)
        base_text = normalize_for_match(title_clean)
        text = normalize_lexical_variants(base_text)
        text_no_seniority = strip_seniority_tokens(text)
        text_no_location = strip_simple_location_noise(text_no_seniority)
        match_texts = [text]
        if text_no_seniority and text_no_seniority != text:
            match_texts.append(text_no_seniority)
        if text_no_location and text_no_location not in match_texts:
            match_texts.append(text_no_location)

        for rule in self.rules:
            if not any(rule.matches(t) for t in match_texts):
                continue
            if self.taxonomy.validate_mapping(rule.normalized_title, rule.role_family):
                is_other = rule.normalized_title == "other" and rule.role_family == "other"
                return TitleNormalizationResult(
                    title_raw=title_raw,
                    title_clean=title_clean,
                    normalized_title=rule.normalized_title,
                    role_family=rule.role_family,
                    classification_status="other" if is_other else "matched",
                    match_method=rule.match_method,
                    confidence=_confidence_for(
                        classification_status="other" if is_other else "matched",
                        match_method=rule.match_method,
                    ),
                    matched_rule_id=rule.rule_id,
                    notes=[rule.notes] if rule.notes else [],
                )
            # Rule matched, but taxonomy contract rejected -> force safe other.
            return TitleNormalizationResult(
                title_raw=title_raw,
                title_clean=title_clean,
                normalized_title="other",
                role_family="other",
                classification_status="other",
                match_method="fallback",
                confidence=_confidence_for(classification_status="other", match_method="fallback"),
                matched_rule_id=rule.rule_id,
                notes=["rule_matched_but_invalid_taxonomy_mapping"],
            )

        fb = _fallback_classify(text)
        if fb.normalized_title == "other" and len(match_texts) > 1:
            fb2 = _fallback_classify(match_texts[1])
            if fb2.normalized_title != "other":
                fb = fb2
        if self.taxonomy.validate_mapping(fb.normalized_title, fb.role_family):
            return TitleNormalizationResult(
                title_raw=title_raw,
                title_clean=title_clean,
                normalized_title=fb.normalized_title,
                role_family=fb.role_family,
                classification_status=fb.status,
                match_method=fb.method,
                confidence=_confidence_for(classification_status=fb.status, match_method=fb.method),
                matched_rule_id=fb.rule_id,
                notes=fb.notes,
            )

        return TitleNormalizationResult(
            title_raw=title_raw,
            title_clean=title_clean,
            normalized_title="other",
            role_family="other",
            classification_status="other",
            match_method="fallback",
            confidence=_confidence_for(classification_status="other", match_method="fallback"),
            matched_rule_id=None,
            notes=["fallback_invalid_taxonomy_mapping"],
        )


def classify_title(title_raw: str) -> TitleNormalizationResult:
    return TitleClassifier().classify(title_raw)

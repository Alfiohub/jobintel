from __future__ import annotations

# Auto-generated candidate TITLE_RULES patches.
# Review manually before merging into title_normalization.py
TITLE_RULES_CANDIDATES: list[tuple[str, str, str, str]] = [
    ('\\bobservability\\\\s+architect\\b|\\bcanada\\b|\\bremote\\b', 'observability_architect', 'other', 'business'),  # sig::observability_architect conf=0.67 n=6
    ('\\bbanco\\\\s+de\\\\s+talentos\\b|\\bbanco\\\\s+de\\\\s+talentos\\\\s+\\-\\\\s+energia\\b|\\bbanco\\\\s+de\\\\s+talentos\\\\s+\\-\\\\s+java\\b', 'banco_de_talentos', 'other', 'business'),  # sig::banco_de_talentos conf=0.64 n=5
    ('\\bcapco\\\\s+associate\\\\s+talent\\\\s+program\\\\s+\\-\\\\s+dallas\\\\s+jan\\\\s+2027\\b|\\bcapco\\\\s+associate\\\\s+talent\\\\s+program\\\\s+\\-\\\\s+dallas\\\\s+june\\\\s+2026\\b|\\bcapco\\\\s+associate\\\\s+talent\\\\s+program\\\\s+\\-\\\\s+houston\\\\s+jan\\\\s+2027\\b', 'capco_associate_talent_program', 'recruiting', 'hr'),  # sig::capco_associate_talent_program conf=0.61 n=4
    ('\\bproduct\\\\s+owner\\b', 'product_owner', 'product_management', 'product'),  # sig::product_owner conf=0.61 n=4
    ('\\bsenior\\\\s+solution\\\\s+architect\\b|\\bsolution\\\\s+architect\\\\s+\\-\\\\s+insurance\\b|\\bsolution\\\\s+architect\\b', 'solution_architect', 'other', 'business'),  # sig::solution_architect conf=0.58 n=3
    ('\\bsenior\\\\s+strategy\\\\s+\\&\\\\s+planning\\\\s+analyst\\b|\\bireland\\b|\\bremote\\b', 'strategy_planning_analyst', 'other', 'business'),  # sig::strategy_planning_analyst conf=0.58 n=3
    ('\\bsenior\\\\s+ba/pm\\b|\\bsecurities\\\\s+services\\b|\\bsr\\\\s+ba\\\\s+/\\\\s+pm\\b', 'ba_pm', 'other', 'business'),  # sig::ba_pm conf=0.55 n=2
    ('\\bcapco\\\\s+summer\\\\s+internship\\\\s+program\\\\s+\\-\\\\s+dallas\\\\s+summer\\\\s+2026\\b|\\bcapco\\\\s+summer\\\\s+internship\\\\s+program\\\\s+\\-\\\\s+houston\\\\s+summer\\\\s+2026\\b', 'capco_summer_internship_program', 'other', 'business'),  # sig::capco_summer_internship_program conf=0.55 n=2
    ('\\bcareer\\\\s+success\\\\s+coach\\b|\\bcareer\\\\s+success\\\\s+coach:\\b', 'career_success_coach', 'other', 'business'),  # sig::career_success_coach conf=0.55 n=2
    ('\\bclient\\\\s+engagement\\\\s+partner\\\\s+\\-\\\\s+fsi\\b|\\bclient\\\\s+engagement\\\\s+partner\\\\s+\\-\\\\s+manufacturing\\\\s+/\\\\s+automotive\\b', 'client_engagement_partner', 'other', 'business'),  # sig::client_engagement_partner conf=0.55 n=2
    ('\\bdesenvolvedor\\\\s+backend\\\\s+\\-\\\\s+node\\.js\\b|\\bdesenvolvedor\\\\s+backend\\\\s+junior\\\\s+\\-\\\\s+exclusivo\\\\s+para\\\\s+pessoas\\\\s+com\\\\s+deficiência\\b', 'desenvolvedor_backend', 'other', 'business'),  # sig::desenvolvedor_backend conf=0.55 n=2
    ('\\bdesenvolvedor\\\\s+llm/backend\\\\s+\\-\\\\s+com\\\\s+inglês\\\\s+\\-\\\\s+remoto\\b', 'desenvolvedor_llm_backend', 'data_analytics', 'data'),  # sig::desenvolvedor_llm_backend conf=0.55 n=2
    ('\\bstaff\\\\s+product\\\\s+analyst\\b|\\busa\\b|\\bremote\\b', 'product_analyst', 'product_management', 'product'),  # sig::product_analyst conf=0.55 n=2
    ('\\bqa\\\\s+automation\\\\s+tester\\\\s+\\-\\\\s+all\\\\s+levels\\b', 'qa_automation_tester', 'software_engineering', 'engineering'),  # sig::qa_automation_tester conf=0.55 n=2
    ('\\blead\\\\s+quality\\\\s+assurance\\b|\\bquality\\\\s+assurance\\\\s+intern\\b', 'quality_assurance', 'software_engineering', 'engineering'),  # sig::quality_assurance conf=0.55 n=2
    ('\\blead\\\\s+service\\\\s+designer\\\\s+\\-\\\\s+product\\\\s+\\&\\\\s+experience\\b|\\bsenior\\\\s+service\\\\s+designer\\\\s+\\-\\\\s+product\\\\s+\\&\\\\s+experience\\b', 'service_designer', 'product_management', 'product'),  # sig::service_designer conf=0.55 n=2
    ('\\bsummernaut\\\\s+program\\\\s+\\-\\\\s+ai\\\\s+\\&\\\\s+management\\\\s+consulting\\\\s+summer\\\\s+intern\\b|\\bsummernaut\\\\s+program\\\\s+\\-\\\\s+esg\\\\s+transformation\\\\s+summer\\\\s+intern\\b', 'summernaut_program', 'other', 'business'),  # sig::summernaut_program conf=0.55 n=2
    ('\\blead\\\\s+supply\\\\s+chain\\\\s+optimization\\\\s+deployment\\\\s+architect\\\\s+\\-\\\\s+public\\\\s+sector\\b|\\bsenior\\\\s+supply\\\\s+chain\\\\s+optimization\\\\s+deployment\\\\s+architect\\\\s+\\-\\\\s+public\\\\s+sector\\b', 'supply_chain_optimization_deployment', 'other', 'business'),  # sig::supply_chain_optimization_deployment conf=0.55 n=2
]


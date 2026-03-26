from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Pattern


@dataclass(frozen=True)
class TitleRule:
    rule_id: str
    pattern_text: str
    normalized_title: str
    role_family: str
    priority: int
    match_method: str = "rule_pattern"
    notes: Optional[str] = None
    pattern: Pattern[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "pattern", re.compile(self.pattern_text, re.IGNORECASE))

    def matches(self, text: str) -> bool:
        return bool(self.pattern.search(text))


RULES: List[TitleRule] = [
    TitleRule("exact_general_application", r"\binterested in joining our team\b|\bgeneral application\b", "general_application", "other", 10, "rule_exact"),
    TitleRule("exec_cto", r"\bfield cto\b|\bchief technology officer\b|\bcto\b", "chief_technology_officer", "executive_leadership", 20),
    TitleRule("exec_rvp_sales", r"(?:\bregional vice president\b.*\b(sales|revenue|commercial|gtm|go[- ]to[- ]market)\b|\b(sales|revenue|commercial|gtm|go[- ]to[- ]market)\b.*\bregional vice president\b)", "chief_revenue_officer", "executive_leadership", 30),
    TitleRule("arch_enterprise", r"\bprincipal enterprise architect\b|\benterprise architect\b", "enterprise_architect", "architecture", 40),
    TitleRule("arch_solutions", r"\bsolutions architect\b|\bsolution architect\b|\bobservability architect\b|\btechnical architect\b", "solutions_architect", "architecture", 50),
    TitleRule("arch_partner_innovation", r"\bpartner innovation architect\b", "solutions_architect", "architecture", 60),
    TitleRule("product_owner", r"\bproduct owner\b", "product_manager", "product_management", 70),
    TitleRule("qa_automation", r"\bqa automation tester\b|\bqa automation engineer\b", "software_engineer", "software_engineering", 80),
    TitleRule("qa_ambiguous", r"\bqa engineer\b|\bquality assurance\b", "other", "other", 85, notes="avoid_forced_qa_mapping"),
    TitleRule("sales_account_exec", r"\baccount executive\b", "account_executive", "sales", 90),
    TitleRule("sales_account_manager", r"\bstrategic accounts?\b|\bclient value partner\b|\baccount management\b|\baccount manager\b", "account_manager", "sales", 100),
    TitleRule("sales_bdr", r"\bbusiness development representative\b|\bbdr\b|\bsales development representative\b|\bsdr\b|\bdeveloppement des ventes\b|\bdesarrollo de ventas\b", "business_development_representative", "sales", 110),
    TitleRule("sales_industry", r"\bhead of industry\b|\bindustry lead\b", "industry_lead", "sales", 120),
    TitleRule("business_analyst", r"\bbusiness analyst\b|\bba\s*-", "business_analyst", "business_analysis", 130),
    TitleRule("strategy_corp_dev", r"\bcorporate development\b", "corporate_development", "strategy", 140),
    TitleRule("recruiting_coordinator", r"\brecruiting coordinator\b", "technical_recruiter", "recruiting", 150),
    TitleRule("recruiting_tech", r"\btechnical recruiter\b|\bexecutive search lead\b", "technical_recruiter", "recruiting", 160),
    TitleRule("hrbp", r"\bhr business partner\b|\bpeople business partner\b|\bhrbp\b", "hr_business_partner", "hr", 170),
    TitleRule("hr_generalist", r"\bhr generalist\b", "hr_generalist", "hr", 180),
    TitleRule("hr_head", r"\bhead of talent development\b|\bhead of human resources\b|\bhr manager\b|\bhuman resources manager\b", "hr_manager", "hr", 190),
    TitleRule("consulting_implementation", r"\bimplementation consultant\b|\binstallations specialist\b", "implementation_consultant", "consulting", 200),
    TitleRule("consulting_coordinator", r"\binstall coordinator\b", "implementation_coordinator", "consulting", 210),
    TitleRule("finance_investment", r"\binvestment analyst\b", "investment_analyst", "finance", 220),
    TitleRule("finance_treasury", r"\btreasury analyst\b", "financial_analyst", "finance", 230),
    TitleRule("finance_accounting", r"\baccounting apprentice\b|\baccountant\b|\bcontroller\b|\bauditor\b|\btax senior associate\b", "accountant", "finance", 240),
    TitleRule("finance_analyst", r"\bcommissions analyst\b|\bpricing analyst\b|\bpayroll analyst\b|\bstrategic finance\b|\bfinancial analyst\b|\bfinance analyst\b", "financial_analyst", "finance", 250),
    TitleRule("legal_counsel", r"\bcounsel\b|\battorney\b|\blegal\b", "legal_counsel", "legal", 260),
    TitleRule("csm", r"\bcustomer success\b|\brole readiness specialist\b|\bwinback specialist\b|\bclient services?\b|\btechnical account management\b", "customer_success_manager", "customer_success", 270),
    TitleRule("data_analytics_director", r"\bdata analytics director\b|\bdirector of data analytics\b|\banalytics director\b", "analytics_director", "data_analytics", 280),
    TitleRule("data_analytics_manager", r"\bdata analytics manager\b|\banalytics manager\b", "analytics_manager", "data_analytics", 290),
    TitleRule("data_analytics_engineer", r"\banalytics engineer\b", "analytics_engineer", "data_analytics", 300),
    TitleRule("data_bi_analyst", r"\bbusiness intelligence analyst\b|\bbi analyst\b", "business_intelligence_analyst", "data_analytics", 310),
    TitleRule("data_bi_engineer", r"\bbusiness intelligence engineer\b|\bbi engineer\b", "business_intelligence_engineer", "data_analytics", 320),
    TitleRule("data_analyst", r"\bdata analyst\b|\banalyst, data\b", "data_analyst", "data_analytics", 330),
    TitleRule("data_engineer", r"\bdata engineer\b", "data_engineer", "data_engineering", 340),
    TitleRule("data_scientist", r"\bdata scientist\b", "data_scientist", "data_science", 350),
    TitleRule("ml_scientist", r"\bmachine learning scientist\b|\bml scientist\b", "ml_scientist", "machine_learning", 360),
    TitleRule("ml_engineer", r"\bmachine learning engineer\b|\bml engineer\b|\bgraph engineer\b", "ml_engineer", "machine_learning", 370),
    TitleRule("eng_backend", r"\bbackend engineer\b|\bbackend developer\b|\bdesenvolvedor\(?a\)? backend\b", "backend_engineer", "software_engineering", 380),
    TitleRule("eng_frontend", r"\bfrontend engineer\b|\bfrontend developer\b", "frontend_engineer", "software_engineering", 390),
    TitleRule("eng_fullstack", r"\bfull[ -]?stack engineer\b|\bfull[ -]?stack developer\b", "fullstack_engineer", "software_engineering", 400),
    TitleRule("eng_devops", r"\bdevops\b", "devops_engineer", "devops", 410),
    TitleRule("eng_sre", r"\bsite reliability\b|\bsre\b", "site_reliability_engineer", "sre", 420),
    TitleRule("eng_software", r"\bsoftware engineer\b|\bsoftware developer\b|\btechnical lead\b", "software_engineer", "software_engineering", 430),
    TitleRule("product_manager", r"\bproduct manager\b|\bproduct management\b", "product_manager", "product_management", 440),
    TitleRule("program_tpm", r"\btpm\b|\btechnical program manager\b", "technical_program_manager", "program_management", 450),
    TitleRule("program_analyst", r"\btechnology program analyst\b", "program_analyst", "program_management", 460),
    TitleRule("design_product", r"\bux designer\b|\bui designer\b|\bproduct designer\b|\bproduct design\b|\bvisual designer\b|\bsenior design researcher\b|\bdesign researcher\b", "product_designer", "design", 470),
    TitleRule("design_content", r"\bcontent designer\b|\blearning designer\b|\binstructional designer\b|\btechnical author\b|\bcustomer education\b|\bonboarding\s*(?:&|and)\s*training lead\b|\btraining lead\b", "content_designer", "design", 480),
    TitleRule("it_sysadmin", r"\bsalesforce administrator\b|\bnetsuite administrator\b|\bsystems administrator\b|\bjira administrator\b", "systems_administrator", "it_operations", 490),
    TitleRule("it_support_specialist", r"\bsecurity .*systems specialist\b|\bdesktop systems specialist\b|\bit support specialist\b", "it_support_specialist", "it_operations", 500),
    TitleRule("ops_office", r"\boffice administrator\b|\bworkplace experience specialist\b", "office_administrator", "operations", 510),
    TitleRule("ops_analyst", r"\bworkforce management analyst\b", "operations_analyst", "operations", 520),
    TitleRule("ops_localization", r"\btraining localization intern\b", "localization_intern", "operations", 530),
    TitleRule("ops_delivery", r"\bdelivery excellence\b|\bthreat intelligence\b|\bsecurity risk management specialist\b|\bpublic cloud enablement professional\b", "operations_specialist", "operations", 540),
    TitleRule("partnerships_alliance", r"\bhead of partnerships\b|\balliances?\b", "alliance_manager", "partnerships", 550),
    TitleRule("healthcare_provider", r"\btelehealth provider\b", "healthcare_provider", "healthcare", 560),
    TitleRule("marketing_seo", r"\bseo\b", "seo_specialist", "marketing", 900),
    TitleRule("marketing_ads", r"\bads specialist\b", "marketing_specialist", "marketing", 910),
    TitleRule("consultant_generic", r"\bmanagement consultant\b|\bsenior consultant\b|\blead consultant\b|\bconsultant\b|\bai coach\b|\bagile coach\b|\bai governance\b|\bai transformation\b|\bai delivery lead\b|\bmanaging principal\b", "consultant", "consulting", 920),
    TitleRule("it_technical_support_generic", r"\btechnical support (engineer|specialist|analyst|representative|technician)\b", "it_support_specialist", "it_operations", 930),
    TitleRule("marketing_generic", r"\bmarketing\b", "marketing_specialist", "marketing", 940),
    TitleRule("sales_generic", r"\bsales\b", "sales_representative", "sales", 950),
    TitleRule("recruiting_generic", r"\brecruiter\b|\btalent acquisition\b", "technical_recruiter", "recruiting", 960),
    TitleRule("ops_generic", r"\boperations specialist\b|\boperations coordinator\b", "operations_specialist", "operations", 970),
]


def get_rules() -> List[TitleRule]:
    return sorted(RULES, key=lambda r: r.priority)

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
    TitleRule("qa_engineer_explicit", r"\b(?:senior\s+)?qa engineer\b|\bquality assurance engineer\b", "software_engineer", "software_engineering", 84),
    TitleRule("qa_ambiguous", r"\bquality assurance\b", "other", "other", 85, notes="avoid_forced_qa_mapping"),
    TitleRule("sales_account_exec", r"\baccount executive\b", "account_executive", "sales", 90),
    TitleRule("sales_account_manager", r"\bstrategic accounts?\b|\bclient value partner\b|\baccount management\b|\baccount manager\b", "account_manager", "sales", 100),
    TitleRule("sales_bdr", r"\bbusiness development representative\b|\bbdr\b|\bsales development representative\b|\bsdr\b|\bdeveloppement des ventes\b|\bdesarrollo de ventas\b", "business_development_representative", "sales", 110),
    TitleRule("sales_account_development_representative", r"\baccount development representative\b|\badr\b", "business_development_representative", "sales", 111),
    TitleRule("sales_industry", r"\bhead of industry\b|\bindustry lead\b", "industry_lead", "sales", 120),
    TitleRule("sales_store_associate", r"\blead store associate\b|\bstore associate\b|\bfloor lead\b|\bparts associate\b|\blot attendant\b|\bstylist\b|\bhair color bar assistant\b", "store_associate", "sales", 121),
    TitleRule("sales_business_development_manager", r"\bbusiness development manager\b", "account_manager", "sales", 122),
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
    TitleRule("finance_wealth_advisor", r"\bassociate wealth advisor\b|\bwealth advisor\b", "investment_analyst", "finance", 221),
    TitleRule("finance_treasury", r"\btreasury analyst\b", "financial_analyst", "finance", 230),
    TitleRule("finance_accounting", r"\baccounting apprentice\b|\baccountant\b|\bcontroller\b|\bauditor\b|\btax senior associate\b", "accountant", "finance", 240),
    TitleRule("finance_accounting_manager", r"\baccounting manager\b", "accountant", "finance", 245),
    TitleRule("finance_analyst", r"\bcommissions analyst\b|\bpricing analyst\b|\bpayroll analyst\b|\bpayroll specialist\b|\baccounts payable specialist\b|\bcompliance analyst\b|\bstrategic finance\b|\bfinancial analyst\b|\bfinance analyst\b", "financial_analyst", "finance", 250),
    TitleRule("legal_counsel", r"\bcounsel\b|\battorney\b|\blegal\b", "legal_counsel", "legal", 260),
    TitleRule("healthcare_nurse_practitioner", r"\bnurse practitioner\b|\bpmhnp\b", "nurse_practitioner", "healthcare_clinical", 265),
    TitleRule("healthcare_psychiatrist", r"\bpsychiatrist\b", "psychiatrist", "healthcare_clinical", 266),
    TitleRule("healthcare_registered_nurse", r"\bregistered nurse\b|\blicensed practical nurse\b|\bclinical research nurse\b|\b(?:rn|lpn)\b\s*nurse\b|\bnurse\b.*\((?:rn|lpn)\)", "registered_nurse", "healthcare_clinical", 266),
    TitleRule("healthcare_physician", r"\bprimary care physician\b|\bfamily medicine physician\b|\bcollaborating physician\b", "healthcare_provider", "healthcare", 266),
    TitleRule("healthcare_psychotherapist", r"\bpsychotherapist\b", "psychotherapist", "healthcare_clinical", 267),
    TitleRule("healthcare_licensed_mental_health_therapist", r"\blicensed mental health therapist\b|\bmental health therapist\b", "psychotherapist", "healthcare_clinical", 267),
    TitleRule("healthcare_mental_health_specialist", r"\bintervention specialist\b|\bbehavioral interventionist\b|\bdirect support professional\b|\bboard certified behavior analyst\b", "mental_health_specialist", "healthcare_clinical", 267),
    TitleRule("healthcare_occupational_therapist", r"\boccupational therapist\b", "occupational_therapist", "healthcare_clinical", 267),
    TitleRule("healthcare_medical_assistant", r"\bmedical assistant\b", "medical_assistant", "healthcare_clinical", 267),
    TitleRule("healthcare_personal_care_specialist", r"\bpersonal care specialist\b", "personal_care_specialist", "healthcare_clinical", 267),
    TitleRule("healthcare_health_info_specialist", r"\bhealth information specialist\b", "health_information_specialist", "healthcare_clinical", 268),
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
    TitleRule("eng_manager", r"\bengineering manager\b|\bsoftware engineering manager\b|\bmanager,\s*software engineering\b|\bmanager\s+software engineering\b", "engineering_manager", "software_engineering", 435),
    TitleRule("product_manager", r"\bproduct manager\b|\bproduct management\b", "product_manager", "product_management", 440),
    TitleRule("manager_general_ambiguous", r"\bgeneral manager\b", "other", "other", 444, notes="ambiguous_general_manager"),
    TitleRule("program_project_manager", r"\bproject manager\b", "project_manager", "program_management", 445),
    TitleRule("program_manager_generic", r"\bprogram manager\b", "project_manager", "program_management", 446),
    TitleRule("program_tpm", r"\btpm\b|\btechnical program manager\b", "technical_program_manager", "program_management", 450),
    TitleRule("program_analyst", r"\btechnology program analyst\b", "program_analyst", "program_management", 460),
    TitleRule("education_instructor", r"\bamt instructor\b|\binstructor\b", "teacher", "education", 465),
    TitleRule("education_instructional_aide", r"\binstructional aide\b", "assistant_teacher", "education", 466),
    TitleRule("design_product", r"\bux designer\b|\bui designer\b|\bproduct designer\b|\bproduct design\b|\bvisual designer\b|\bsenior design researcher\b|\bdesign researcher\b", "product_designer", "design", 470),
    TitleRule("design_content", r"\bcontent designer\b|\blearning designer\b|\binstructional designer\b|\btechnical author\b|\btechnical writer\b|\bcustomer education\b|\bonboarding\s*(?:&|and)\s*training lead\b|\btraining lead\b", "content_designer", "design", 480),
    TitleRule("design_brand_designer", r"\bbrand designer\b", "product_designer", "design", 481),
    TitleRule("it_sysadmin", r"\bsalesforce administrator\b|\bnetsuite administrator\b|\bsystems administrator\b|\bjira administrator\b", "systems_administrator", "it_operations", 490),
    TitleRule("it_support_specialist", r"\bsecurity .*systems specialist\b|\bdesktop systems specialist\b|\bit support specialist\b", "it_support_specialist", "it_operations", 500),
    TitleRule("admin_executive_assistant", r"\bexecutive assistant\b", "executive_assistant", "administrative_support", 505),
    TitleRule("admin_administrative_assistant", r"\badministrative assistant\b", "administrative_assistant", "administrative_support", 506),
    TitleRule("admin_chief_of_staff", r"\bchief of staff\b", "chief_of_staff", "administrative_support", 507),
    TitleRule("ops_office", r"\boffice administrator\b|\bworkplace experience specialist\b", "office_administrator", "operations", 510),
    TitleRule("ops_coordinator", r"\brental coordinator\b|\bproject coordinator\b|\blogistics coordinator\b|\boffice coordinator\b", "operations_specialist", "operations", 515),
    TitleRule("ops_safety_manager", r"\bregional safety manager\b", "operations_specialist", "operations", 516),
    TitleRule("ops_analyst", r"\bworkforce management analyst\b", "operations_analyst", "operations", 520),
    TitleRule("ops_localization", r"\btraining localization intern\b", "localization_intern", "operations", 530),
    TitleRule("ops_customer_service", r"\bcustomer service delivery advocate\b|\bcustomer service specialist\b|\bcustomer service representative\b|\bcustomer service advisor\b|\bcustomer support representative\b|\bcustomer support specialist\b", "customer_service_specialist", "operations", 535),
    TitleRule("ops_case_manager", r"\bbilingual case manager\b|\bcase manager\b", "operations_specialist", "operations", 536),
    TitleRule("ops_delivery", r"\bdelivery excellence\b|\bthreat intelligence\b|\bsecurity risk management specialist\b|\bpublic cloud enablement professional\b", "operations_specialist", "operations", 540),
    TitleRule("partnerships_strategy_manager", r"\bmarket strategy and partnerships manager\b", "alliance_manager", "partnerships", 549),
    TitleRule("partnerships_alliance", r"\bhead of partnerships\b|\balliances?\b", "alliance_manager", "partnerships", 550),
    TitleRule("healthcare_provider", r"\btelehealth provider\b", "healthcare_provider", "healthcare", 560),
    TitleRule("education_assistant_teacher", r"\bassistant teacher\b", "assistant_teacher", "education", 570),
    TitleRule("education_substitute_teacher", r"\bsubstitute teacher\b", "substitute_teacher", "education", 575),
    TitleRule("education_teacher", r"\bteacher\b", "teacher", "education", 580),
    TitleRule("logistics_delivery_driver", r"\bcustomer delivery driver\b|\bdelivery driver\b", "delivery_driver", "logistics", 590),
    TitleRule("logistics_driver", r"\bcdl\b.*\bdriver\b|\bdriver\b", "driver", "logistics", 600),
    TitleRule("trades_field_technician", r"\bheavy equipment field technician\b|\bfield technician\b", "field_technician", "skilled_trades", 610),
    TitleRule("trades_mechanic", r"\bheavy equipment shop technician\b|\bshop technician\b.*\bmechanic\b|\bmechanic\b", "mechanic", "skilled_trades", 620),
    TitleRule("trades_landscape_technician", r"\blandscape technician\b", "landscape_technician", "skilled_trades", 625),
    TitleRule(
        "trades_auto_body_repair_precision_v27",
        r"\b(?:auto\s?body|autobody)\b.*\b(?:repair|prep(?:per)?|inspector|combo\s+tech|tech|technician|painter|paint\s+prep(?:per)?)\b"
        r"|\bpaintless dent repair\s*(?:tech|technician)\b"
        r"|\b(?:auto(?:motive)?\s+)?(?:wheel\s*[-/]?\s*rim|rim)\s+repair\s*(?:tech|technician)\b"
        r"|\bauto(?:motive)?\s+interior\s+repair\b.*\bglass\s+repair\b.*\b(?:tech|technician)\b",
        "mechanic",
        "skilled_trades",
        626,
        notes="precision_auto_body_repair_cluster_v27",
    ),
    TitleRule("trades_car_detailer", r"\bcar detailer\b", "car_detailer", "skilled_trades", 630),
    TitleRule("trades_technician", r"\bfuture technician\b|\btechnician\b", "technician", "skilled_trades", 635),
    TitleRule("trades_telematics_installer", r"\btelematics installer\b", "technician", "skilled_trades", 636),
    TitleRule("trades_auto_painter", r"\bauto painter\b|\bautomotive painter\b", "auto_painter", "skilled_trades", 637),
    TitleRule("sales_territory_account_manager", r"\bterritory account manager\b", "account_manager", "sales", 640),
    TitleRule("sales_account_director", r"\baccount director\b", "account_manager", "sales", 641),
    TitleRule("marketing_social_media_manager", r"\bsocial media manager\b", "marketing_specialist", "marketing", 645),
    TitleRule("data_quantitative_researcher", r"\bquantitative researcher\b", "data_scientist", "data_science", 646),
    TitleRule("business_product_analyst", r"\bproduct analyst\b", "business_analyst", "business_analysis", 647),
    TitleRule("business_deal_desk_analyst", r"\bdeal desk analyst\b", "business_analyst", "business_analysis", 648),
    TitleRule("finance_fpa_manager", r"\bfp\\s*(?:&|and)\\s*a manager\b|\bfp&a manager\b|\bfpa manager\b", "financial_analyst", "finance", 649),
    TitleRule("content_editorial", r"\bstory desk editor\b|\bmultiskilled journalist\b|\bproducer\b", "content_designer", "design", 651),
    TitleRule("content_media_manager", r"\bmedia manager\b", "content_designer", "design", 652),
    TitleRule("marketing_paid_media_manager", r"\bpaid media\b", "marketing_specialist", "marketing", 650),
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

from __future__ import annotations

import re


_WS_RE = re.compile(r"\s+")

TITLE_RULES: list[tuple[str, str, str, str]] = [
    (r"\binterested in joining our team\b|\bgeneral application\b", "general_application", "other", "hr"),
    (r"\bfield cto\b|\bchief technology officer\b|\bcto\b", "chief_technology_officer", "executive_leadership", "business"),
    (r"\bprincipal enterprise architect\b|\benterprise architect\b", "enterprise_architect", "architecture", "engineering"),
    (r"\bsolutions architect\b", "solutions_architect", "architecture", "engineering"),
    (r"\bsolution architect\b|\bobservability architect\b", "solutions_architect", "architecture", "engineering"),
    (r"\btechnical architect\b", "solutions_architect", "architecture", "engineering"),
    (r"\bproduct owner\b", "product_manager", "product_management", "product"),
    (r"\bstrategy\s*(?:&|and)\s*planning analyst\b", "business_analyst", "business_analysis", "business"),
    (r"\bqa automation tester\b|\bquality assurance\b|\bqa engineer\b", "software_engineer", "software_engineering", "engineering"),
    (r"\bcareer success coach\b", "customer_success_manager", "customer_success", "business"),
    (r"\bclient engagement partner\b", "account_manager", "sales", "business"),
    (r"\bdesenvolvedor\(a\)? backend\b|\bdesenvolvedor backend\b", "backend_engineer", "software_engineering", "engineering"),
    (r"\bdesenvolvedor\(a\)? llm/backend\b|\bgraph engineer\b", "ml_engineer", "machine_learning", "data"),
    (
        r"\bbanco de talentos\b|\bassociate talent program\b|\bsummer internship program\b|\bsummernaut program\b",
        "general_application",
        "other",
        "hr",
    ),
    (r"\baccount executive\b", "account_executive", "sales", "business"),
    (r"\bstrategic accounts?\b|\bclient value partner\b", "account_manager", "sales", "business"),
    (r"\baccount management\b|\baccount manager\b", "account_manager", "sales", "business"),
    (r"\bbusiness development representative\b|\bbdr\b", "business_development_representative", "sales", "business"),
    (r"\bsales development representative\b|\bsdr\b", "business_development_representative", "sales", "business"),
    (r"\bchief revenue officer\b|\bcro\b", "chief_revenue_officer", "executive_leadership", "business"),
    (r"\bhead of industry\b|\bindustry lead\b", "industry_lead", "sales", "business"),
    (r"\bsales\b", "sales_representative", "sales", "business"),
    (r"\bbusiness analyst\b|\bba\s*-", "business_analyst", "business_analysis", "business"),
    (r"\bcorporate development\b", "corporate_development", "strategy", "business"),
    (r"\btechnical recruiter\b", "technical_recruiter", "recruiting", "hr"),
    (r"\bexecutive search lead\b", "technical_recruiter", "recruiting", "hr"),
    (r"\bhr business partner\b|\bpeople business partner\b|\bhrbp\b", "hr_business_partner", "hr", "hr"),
    (r"\bhr generalist\b", "hr_generalist", "hr", "hr"),
    (r"\bimplementation consultant\b", "implementation_consultant", "consulting", "business"),
    (r"\bmanagement consultant\b|\bsenior consultant\b|\blead consultant\b|\bconsultant\b", "consultant", "consulting", "business"),
    (r"\binstallations specialist\b", "implementation_consultant", "consulting", "business"),
    (r"\binstall coordinator\b", "implementation_coordinator", "consulting", "business"),
    (r"\bai coach\b|\bagile coach\b", "consultant", "consulting", "business"),
    (r"\bai governance\b|\bai transformation\b|\bai delivery lead\b|\bmanaging principal\b", "consultant", "consulting", "business"),
    (r"\binvestment analyst\b", "investment_analyst", "finance", "finance"),
    (r"\baccountant\b|\bcontroller\b|\bauditor\b", "accountant", "finance", "finance"),
    (r"\bcommissions analyst\b|\bpricing analyst\b", "financial_analyst", "finance", "finance"),
    (r"\bstrategic finance\b|\bfinancial analyst\b|\bfinance analyst\b", "financial_analyst", "finance", "finance"),
    (r"\bcounsel\b|\battorney\b|\blegal\b", "legal_counsel", "legal", "business"),
    (r"\bcustomer success\b", "customer_success_manager", "customer_success", "business"),
    (r"\brole readiness specialist\b|\bwinback specialist\b", "customer_success_manager", "customer_success", "business"),
    (r"\bclient services?\b|\btechnical account management\b", "customer_success_manager", "customer_success", "business"),
    (r"\bdata analytics director\b|\bdirector of data analytics\b", "analytics_director", "data_analytics", "data"),
    (r"\banalytics director\b", "analytics_director", "data_analytics", "data"),
    (r"\bdata analytics manager\b|\banalytics manager\b", "analytics_manager", "data_analytics", "data"),
    (r"\banalytics engineer\b", "analytics_engineer", "data_analytics", "data"),
    (r"\bbusiness intelligence analyst\b|\bbi analyst\b", "business_intelligence_analyst", "data_analytics", "data"),
    (r"\bbusiness intelligence engineer\b|\bbi engineer\b", "business_intelligence_engineer", "data_analytics", "data"),
    (r"\bdata analyst\b|\banalyst, data\b", "data_analyst", "data_analytics", "data"),
    (r"\bdata engineer\b", "data_engineer", "data_engineering", "data"),
    (r"\bdata scientist\b", "data_scientist", "data_science", "data"),
    (r"\bmachine learning scientist\b|\bml scientist\b", "ml_scientist", "machine_learning", "data"),
    (r"\bmachine learning engineer\b|\bml engineer\b", "ml_engineer", "machine_learning", "data"),
    (r"\bai (technical )?architect\b|\bai deployment architect\b", "enterprise_architect", "architecture", "engineering"),
    (r"\bbackend engineer\b|\bbackend developer\b", "backend_engineer", "software_engineering", "engineering"),
    (r"\bfrontend engineer\b|\bfrontend developer\b", "frontend_engineer", "software_engineering", "engineering"),
    (r"\bfull[ -]?stack engineer\b|\bfull[ -]?stack developer\b", "fullstack_engineer", "software_engineering", "engineering"),
    (r"\bdevops\b", "devops_engineer", "devops", "engineering"),
    (r"\bsite reliability\b|\bsre\b", "site_reliability_engineer", "sre", "engineering"),
    (r"\bsoftware engineer\b|\bsoftware developer\b", "software_engineer", "software_engineering", "engineering"),
    (r"\bproduct manager\b|\bproduct management\b", "product_manager", "product_management", "product"),
    (r"\btpm\b|\btechnical program manager\b", "technical_program_manager", "program_management", "product"),
    (r"\btechnology program analyst\b", "program_analyst", "program_management", "product"),
    (r"\bux designer\b|\bui designer\b|\bproduct designer\b|\bproduct design\b", "product_designer", "design", "design"),
    (r"\bcontent designer\b|\blearning designer\b", "content_designer", "design", "design"),
    (r"\binstructional designer\b", "content_designer", "design", "design"),
    (r"\bsalesforce administrator\b|\bnetsuite administrator\b|\bsystems administrator\b", "systems_administrator", "it_operations", "engineering"),
    (r"\boffice administrator\b|\bworkplace experience specialist\b", "office_administrator", "operations", "business"),
    (r"\bnetsuite analyst\b", "business_systems_analyst", "business_analysis", "business"),
    (r"\bworkforce management analyst\b", "operations_analyst", "operations", "business"),
    (r"\btalent development partner\b|\bpeople business partnerships?\b", "hr_business_partner", "hr", "hr"),
    (r"\btalent scientist\b|\btalent science\b", "talent_analytics_specialist", "hr", "hr"),
    (r"\bhead of talent development\b", "hr_manager", "hr", "hr"),
    (r"\btelehealth provider\b", "healthcare_provider", "healthcare", "business"),
    (r"\bsecurity .*systems specialist\b|\bdesktop systems specialist\b|\bit support specialist\b", "it_support_specialist", "it_operations", "engineering"),
    (r"\btechnical support\b", "it_support_specialist", "it_operations", "engineering"),
    (r"\balliances?\b", "alliance_manager", "partnerships", "business"),
    (r"\btechnical lead\b", "software_engineer", "software_engineering", "engineering"),
    (r"\btraining localization intern\b", "localization_intern", "operations", "business"),
    (r"\bseo\b", "seo_specialist", "marketing", "business"),
    (r"\bads specialist\b", "marketing_specialist", "marketing", "business"),
    (r"\bmarketing\b", "marketing_specialist", "marketing", "business"),
    (r"\brecruiter\b|\btalent acquisition\b", "technical_recruiter", "recruiting", "hr"),
    (r"\boperations specialist\b|\boperations coordinator\b", "operations_specialist", "operations", "business"),
]


def normalize_title(title_clean: str) -> tuple[str, str, str]:
    t = title_clean.lower()
    t = re.sub(r"\([^\)]*\)", " ", t)
    t = re.sub(r"[^a-z0-9+/#& -]+", " ", t)
    t = _WS_RE.sub(" ", t).strip()
    for pattern, normalized, family, group in TITLE_RULES:
        if re.search(pattern, t):
            return normalized, family, group
    # Data/analytics fallback to reduce "other" on common variants.
    if re.search(r"\bdata\b|\banalytics?\b|\bbi\b|\bbusiness intelligence\b", t):
        if re.search(r"\bdirector\b|\bhead\b|\bvp\b", t):
            return "analytics_director", "data_analytics", "data"
        if re.search(r"\bmanager\b|\blead\b", t):
            return "analytics_manager", "data_analytics", "data"
        if re.search(r"\bengineer\b", t):
            return "analytics_engineer", "data_analytics", "data"
        if re.search(r"\banalyst\b", t):
            return "data_analyst", "data_analytics", "data"
        return "data_analyst", "data_analytics", "data"
    if re.search(r"\bcounsel\b|\battorney\b|\blegal\b", t):
        return "legal_counsel", "legal", "business"
    if re.search(r"\baccountant\b|\bcontroller\b|\bauditor\b|\bfinance\b", t):
        if re.search(r"\banalyst\b", t):
            return "financial_analyst", "finance", "finance"
        return "accountant", "finance", "finance"
    if re.search(r"\bseo\b|\bmarketing\b|\bcontent\b", t):
        return "marketing_specialist", "marketing", "business"
    if re.search(r"\brecruiter\b|\btalent acquisition\b|\bpeople partner\b", t):
        return "technical_recruiter", "recruiting", "hr"
    if re.search(r"\boperations?\b|\bfulfillment\b", t):
        return "operations_specialist", "operations", "business"
    if "manager" in t:
        # Manager redistribution policy: map to existing specific titles or fallback to other.
        if re.search(r"\bproduct manager\b|\bproduct owner\b", t):
            return "product_manager", "product_management", "product"
        if re.search(r"\bproject manager\b|\bprogram manager\b", t):
            return "technical_program_manager", "program_management", "product"
        if re.search(r"\bsuccess manager\b", t):
            return "customer_success_manager", "customer_success", "business"
        if re.search(r"\bpartner manager\b|\balliance manager\b", t):
            return "alliance_manager", "partnerships", "business"
        if re.search(r"\baccounting manager\b|\brevenue accounting manager\b|\bmanager\b.*\baccounting\b", t):
            return "accountant", "finance", "finance"
        if re.search(r"\bfinance manager\b", t):
            return "financial_analyst", "finance", "finance"
        if re.search(r"\bhr manager\b|\bhuman resources manager\b", t):
            return "hr_manager", "hr", "hr"
        if re.search(r"\bdesign manager\b", t):
            return "product_designer", "design", "design"
        if re.search(r"\bcampaign manager\b|\bgrowth manager\b|\bcommunications manager\b", t):
            return "marketing_specialist", "marketing", "business"
        if re.search(r"\bsolution services manager\b|\bmanager,\s*solution services\b|\bsolution architecture manager\b|\bsolutions architecture manager\b", t):
            return "solutions_architect", "architecture", "engineering"
        if re.search(r"\bsales manager\b", t):
            return "sales_representative", "sales", "business"
        if re.search(r"\bprofessional services manager\b|\bbusiness services team manager\b|\bdeal desk\b|\bhealth information management\b", t):
            return "operations_specialist", "operations", "business"
        if re.search(r"\bengineering\b", t):
            return "software_engineer", "software_engineering", "engineering"
        if re.search(r"\boperations manager\b", t):
            return "operations_specialist", "operations", "business"
        return "other", "other", "other"
    if "engineer" in t or "developer" in t:
        return "software_engineer", "software_engineering", "engineering"
    return "other", "other", "other"

# Query Packs Step 18

Input: `data/jobs/jobs_indexed_en.jsonl`

## Pack List
- `account_executive_jobs` | quality=strong | matched_rows=3152
- `healthcare_clinical_jobs` | quality=usable | matched_rows=2104
- `high_confidence_tech_jobs` | quality=strong | matched_rows=8677
- `marketing_jobs_with_salary` | quality=strong | matched_rows=1584
- `other_with_strong_signals` | quality=noisy | matched_rows=10166
- `python_tech_jobs` | quality=usable | matched_rows=6049
- `remote_data_jobs` | quality=strong | matched_rows=582
- `skilled_trades_jobs` | quality=usable | matched_rows=713

## Pack Details
### account_executive_jobs
- quality: **strong**
- description: High-precision account executive opportunities.
- matched_rows: 3152
- tradeoff: Only normalized account executive roles.
- filters:
  - account_executive: `{'normalized_title': 'account_executive', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=3152)
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7728365 | Account Executive, Product Sales - Capital | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7724828 | National Account Executive, Enterprise (India) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7693271 | Enterprise Account Executive | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7686224 | Account Executive - Funded Startups - French | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7675661 | Account Executive, Product - BNPLs | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7577015 | Account Executive, Platforms (Grower) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7576967 | Account Executive, Platforms (Existing Business) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7555127 | Account Executive, SMB - Existing Business (French-speaking) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7553751 | Account Executive, Existing Business, Iberia | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7546284 | Account Executive, AI Sales | account_executive | family=sales | loc=None | salary=False | skills=False | other=False

### healthcare_clinical_jobs
- quality: **usable**
- description: Healthcare clinical jobs covered by current taxonomy.
- matched_rows: 2104
- tradeoff: Clinical residual long-tail in other is not included.
- filters:
  - healthcare_clinical: `{'normalized_title': None, 'role_family': 'healthcare_clinical', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=2104)
- sample rows (10):
  - https://www.datavant.com/about/careers/open-roles/job?gh_jid=5153785008 | Health Information Specialist I | health_information_specialist | family=healthcare_clinical | loc=onsite | salary=False | skills=False | other=False
  - https://job-boards.greenhouse.io/dianahealth94/jobs/4424228008 | Women's Health Nurse Practitioner (Full-Time) | nurse_practitioner | family=healthcare_clinical | loc=None | salary=False | skills=False | other=False
  - https://www.datavant.com/about/careers/open-roles/job?gh_jid=5158721008 | Health Information Specialist I | health_information_specialist | family=healthcare_clinical | loc=onsite | salary=False | skills=False | other=False
  - https://job-boards.greenhouse.io/dianahealth94/jobs/4885719008 | Women's Health Nurse Practitioner (Full-Time) | nurse_practitioner | family=healthcare_clinical | loc=None | salary=False | skills=False | other=False
  - https://job-boards.greenhouse.io/dianahealth94/jobs/4885674008 | Women's Health Nurse Practitioner (Full-Time) | nurse_practitioner | family=healthcare_clinical | loc=None | salary=False | skills=False | other=False
  - https://job-boards.greenhouse.io/dianahealth94/jobs/4885663008 | Women's Health Nurse Practitioner (Full-Time) | nurse_practitioner | family=healthcare_clinical | loc=None | salary=False | skills=False | other=False
  - https://job-boards.greenhouse.io/dianahealth94/jobs/5152060008 | WHNP - Women's Health Nurse Practitioner (Full-Time) | nurse_practitioner | family=healthcare_clinical | loc=None | salary=False | skills=False | other=False
  - https://www.datavant.com/about/careers/open-roles/job?gh_jid=5160856008 | Health Information Specialist I | health_information_specialist | family=healthcare_clinical | loc=onsite | salary=False | skills=False | other=False
  - https://boards.greenhouse.io/spacex/jobs/8365449002?gh_jid=8365449002 | Sr. DSP Engineer (Starshield) | behavioral_support_specialist | family=healthcare_clinical | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8321911002?gh_jid=8321911002 | DSP Engineer (Starshield) | behavioral_support_specialist | family=healthcare_clinical | loc=None | salary=True | skills=False | other=False

### high_confidence_tech_jobs
- quality: **strong**
- description: Core technical normalized titles with salary/skills strong signals.
- matched_rows: 8677
- tradeoff: Conservative and intentionally excludes borderline technical roles.
- filters:
  - software_engineer: `{'normalized_title': 'software_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=6314)
  - data_engineer: `{'normalized_title': 'data_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=693)
  - ml_engineer: `{'normalized_title': 'ml_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=731)
  - devops_engineer: `{'normalized_title': 'devops_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=301)
  - site_reliability_engineer: `{'normalized_title': 'site_reliability_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=307)
  - solutions_architect: `{'normalized_title': 'solutions_architect', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=331)
- sample rows (10):
  - https://job-boards.greenhouse.io/outschool/jobs/4607423006 | Software Engineer | software_engineer | family=software_engineering | loc=hybrid | salary=True | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7746721 | Senior Staff Frontend Engineer, Merchant Experience | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7705412 | Staff Software Engineer, Terminal Developer Productivity | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7671038 | Forward Deployed Engineer, Professional Services | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7656562 | Frontend Engineer, Privy | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7629052 | Machine Learning Engineer, Stripe Assistant | ml_engineer | family=machine_learning | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7607761 | Partner Solutions Architect - AWS | solutions_architect | family=architecture | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7600792 | Software Engineer, Experimental Projects | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7545459 | Software Engineer, Product Security Data Platforms | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7543868 | Software Engineer, Internal Systems | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False

### marketing_jobs_with_salary
- quality: **strong**
- description: Marketing jobs where salary signal is present.
- matched_rows: 1584
- tradeoff: Biased toward geographies/companies with salary disclosure.
- filters:
  - marketing_salary: `{'normalized_title': None, 'role_family': 'marketing', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': True, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=1584)
- sample rows (10):
  - https://job-boards.greenhouse.io/recordedfuture/jobs/8482248002 | Senior Product Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://boards.greenhouse.io/spacex/jobs/8433873002?gh_jid=8433873002 | Sr. Channel Marketing Manager (Starlink) | marketing_specialist | family=marketing | loc=None | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/edmentum/jobs/5692818004 | Sr. Product Marketing Manager - Career | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/apexcompanies/jobs/5081772008 | Senior Marketing Proposal Coordinator – AEC | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/apexcompanies/jobs/5079653008 | Senior Marketing Proposal Coordinator – AEC | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False
  - https://fundraiseup.com/careers/4676197005/?gh_jid=4676197005 | Manager, Enterprise & Strategic Marketing, USA, Remote | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/asteralabs/jobs/4678170005 | Events Marketing Manager | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/rockstargames/jobs/6261996003 | Marketing Manager, Live Services | marketing_specialist | family=marketing | loc=onsite | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/axon/jobs/7638746003 | Software Product Marketing Manager | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/axon/jobs/7637489003 | Software Product Marketing Manager | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False

### other_with_strong_signals
- quality: **noisy**
- description: Discovery pack: other titles but with stronger structured signals.
- matched_rows: 10166
- tradeoff: Useful for curation; heterogeneity remains high by design.
- filters:
  - other_salary_and_skills: `{'normalized_title': 'other', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': True, 'has_skills': True, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=7866)
  - other_remote_with_skills: `{'normalized_title': 'other', 'role_family': None, 'language_bucket': None, 'location_type': 'remote', 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=4483)
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7743307 | Frontend Platform Engineer, JavaScript Infrastructure | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7737241 | Backend / API Engineer, Billing | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733216 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7723989 | Internal Recruiting Coordinator | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7722938 | Credit Operations Analyst | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7716032 | Staff Engineer - Production Eng | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7688196 | Equity Administrator | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7685049 | Deal Pricing | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7657938 | Product Strategy & Operations, Link | other | family=other | loc=remote | salary=False | skills=True | other=True

### python_tech_jobs
- quality: **usable**
- description: Python jobs with stronger product signal: non-other + technical families.
- matched_rows: 6049
- tradeoff: Lower recall on python mentions in broad non-tech roles.
- filters:
  - python_non_other: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=6049)
  - python_software_engineering: `{'normalized_title': None, 'role_family': 'software_engineering', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=3071)
  - python_data_engineering: `{'normalized_title': None, 'role_family': 'data_engineering', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=584)
  - python_machine_learning: `{'normalized_title': None, 'role_family': 'machine_learning', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=505)
  - python_data_science: `{'normalized_title': None, 'role_family': 'data_science', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=395)
  - python_sre: `{'normalized_title': None, 'role_family': 'sre', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=211)
  - python_devops: `{'normalized_title': None, 'role_family': 'devops', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=197)
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7685855 | Technical Program Manager, Risk | technical_program_manager | family=program_management | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7678655 | Technical Program Manager, Risk | technical_program_manager | family=program_management | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7650073 | Technical Account Manager, Bridge | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7649036 | Processing Cost Accountant | accountant | family=finance | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7629052 | Machine Learning Engineer, Stripe Assistant | ml_engineer | family=machine_learning | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7610132 | Data Analyst | data_analyst | family=data_analytics | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7600792 | Software Engineer, Experimental Projects | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7594376 | Technical Account Manager, German OR Polish Speaking | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7564690 | Technical Account Manager, Risk | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7549012 | Technical Account Manager | account_manager | family=sales | loc=None | salary=False | skills=True | other=False

### remote_data_jobs
- quality: **strong**
- description: Remote-oriented data roles with title normalization not other.
- matched_rows: 582
- tradeoff: Does not include data-like jobs still classified as other.
- filters:
  - remote_data_engineering_family: `{'normalized_title': None, 'role_family': 'data_engineering', 'language_bucket': None, 'location_type': 'remote', 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=334)
  - remote_data_analyst: `{'normalized_title': 'data_analyst', 'role_family': None, 'language_bucket': None, 'location_type': 'remote', 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=101)
  - remote_data_scientist: `{'normalized_title': 'data_scientist', 'role_family': None, 'language_bucket': None, 'location_type': 'remote', 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=147)
- sample rows (10):
  - https://sofi.com/careers/job/7679146003?gh_jid=7679146003 | Data Scientist | data_scientist | family=data_science | loc=remote | salary=False | skills=True | other=False
  - https://sofi.com/careers/job/7679134003?gh_jid=7679134003 | Data Scientist | data_scientist | family=data_science | loc=remote | salary=False | skills=True | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7663349 | Business Intelligence Analyst | data_analyst | family=data_analytics | loc=remote | salary=False | skills=True | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7584120 | Data Analyst III | data_analyst | family=data_analytics | loc=remote | salary=False | skills=True | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7525188 | Data Analyst II | data_analyst | family=data_analytics | loc=remote | salary=False | skills=True | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7525159 | Senior Data Analyst | data_analyst | family=data_analytics | loc=remote | salary=False | skills=True | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=6900544 | Financial Data Analyst | data_analyst | family=data_analytics | loc=remote | salary=False | skills=True | other=False
  - https://job-boards.greenhouse.io/smithrx/jobs/8482781002 | Staff Data Engineer | data_engineer | family=data_engineering | loc=remote | salary=False | skills=True | other=False
  - https://job-boards.greenhouse.io/smithrx/jobs/8468985002 | Senior Staff Data Engineer | data_engineer | family=data_engineering | loc=remote | salary=False | skills=True | other=False
  - https://job-boards.greenhouse.io/springhealth66/jobs/4677925005 | Senior Data Analyst, Customer Value | data_analyst | family=data_analytics | loc=remote | salary=True | skills=True | other=False

### skilled_trades_jobs
- quality: **usable**
- description: Skilled trades jobs covered by current taxonomy pack.
- matched_rows: 713
- tradeoff: Domain-specific long-tail variants can still be in other.
- filters:
  - skilled_trades: `{'normalized_title': None, 'role_family': 'skilled_trades', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}` (matched=713)
- sample rows (10):
  - https://job-boards.greenhouse.io/apexcompanies/jobs/5162470008 | Landscape Technician (Stormwater) | technician | family=skilled_trades | loc=None | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/apexcompanies/jobs/5162449008 | Landscape Technician (Stormwater) | technician | family=skilled_trades | loc=None | salary=True | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7759762 | Heavy Equipment Shop Technician (Mechanic) | mechanic | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7673762 | Heavy Equipment Field Technician (Mechanic) | field_technician | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.carvana.com/careers/apply?gh_jid=7761311 | Car Detailer | car_detailer | family=skilled_trades | loc=None | salary=True | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7759852 | Heavy Equipment Shop Technician (Mechanic) | mechanic | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7759784 | Heavy Equipment Shop Technician (Mechanic) | mechanic | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7759765 | Heavy Equipment Field Technician (Mechanic) | field_technician | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7759759 | Heavy Equipment Field Technician (Mechanic) | field_technician | family=skilled_trades | loc=None | salary=False | skills=False | other=False
  - https://www.equipmentshare.com/careers/openings/?gh_jid=7758441 | Heavy Equipment Field Technician (Mechanic) | field_technician | family=skilled_trades | loc=onsite | salary=False | skills=False | other=False

## Known Limits
- Pack composition is deterministic and rules-based only.
- No ranking/semantic search in this step.
- Pack quality depends on upstream title and skills signals.
# Retrieval Quality Step 16

Input: `data/jobs/jobs_indexed_en.jsonl`

## Query Evaluation
### data_engineer
- quality: **strong**
- results_count: 730
- filters: `{'normalized_title': 'data_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://boards.greenhouse.io/accenturefederalservices/jobs/4607396006?gh_jid=4607396006 | Data Engineer/Architect | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8391768002?gh_jid=8391768002 | Data Engineer (Direct To Cell) | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8379395002?gh_jid=8379395002 | Sr. Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8379386002?gh_jid=8379386002 | Sr. Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8243150002?gh_jid=8243150002 | Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8240611002?gh_jid=8240611002 | Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | loc=None | salary=True | skills=True | other=False
  - https://boards.greenhouse.io/spacex/jobs/8192168002?gh_jid=8192168002 | Data Engineer, Ground Network Engineering (Gateway) | data_engineer | family=data_engineering | loc=hybrid | salary=True | skills=True | other=False
  - https://job-boards.greenhouse.io/spauldingridge/jobs/5734967004 | Data Engineer | data_engineer | family=data_engineering | loc=hybrid | salary=False | skills=True | other=False
  - https://job-boards.greenhouse.io/rockstargames/jobs/7637154003 | Principal Data Engineer, Data Architecture | data_engineer | family=data_engineering | loc=onsite | salary=True | skills=True | other=False
  - https://job-boards.greenhouse.io/rockstargames/jobs/7619983003 | Principal Data Engineer, Data Architecture | data_engineer | family=data_engineering | loc=onsite | salary=True | skills=True | other=False

### software_engineer
- quality: **strong**
- results_count: 8517
- filters: `{'normalized_title': 'software_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://job-boards.greenhouse.io/outschool/jobs/4607423006 | Software Engineer | software_engineer | family=software_engineering | loc=hybrid | salary=True | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7746721 | Senior Staff Frontend Engineer, Merchant Experience | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7737239 | Full Stack Engineer, Billing | software_engineer | family=software_engineering | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7715292 | Full Stack Engineer, Compliance Applications | software_engineer | family=software_engineering | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7705412 | Staff Software Engineer, Terminal Developer Productivity | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7671038 | Forward Deployed Engineer, Professional Services | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7656562 | Frontend Engineer, Privy | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7618977 | Software Engineer, Core Technology | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7600792 | Software Engineer, Experimental Projects | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7591894 | Full Stack Engineer, Risk & Support | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False

### marketing
- quality: **usable**
- results_count: 2513
- filters: `{'normalized_title': None, 'role_family': 'marketing', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'updated_at_desc', 'limit': 10}`
- problemi osservati:
  - Buona copertura, ma include varianti molto diverse (manager/coordinator/specialist).
- sample rows (10):
  - https://www.talkspace.com/careers/job?gh_jid=5831759004 | Marketing Ops Engineer Intern | marketing_specialist | family=marketing | loc=remote | salary=False | skills=True | other=False
  - https://www.talkspace.com/careers/job?gh_jid=5831378004 | Marketing Design Intern | marketing_specialist | family=marketing | loc=remote | salary=False | skills=False | other=False
  - https://www.taboola.com/careers/job/7722945?gh_jid=7722945 | Marketing Coordinator | marketing_specialist | family=marketing | loc=hybrid | salary=False | skills=True | other=False
  - https://www.taboola.com/careers/job/7713805?gh_jid=7713805 | Marketing Manager - Taiwan / Hong Kong | marketing_specialist | family=marketing | loc=hybrid | salary=False | skills=True | other=False
  - https://www.taboola.com/careers/job/7550360?gh_jid=7550360 | Marketing Manager, China | marketing_specialist | family=marketing | loc=hybrid | salary=False | skills=False | other=False
  - https://www.taboola.com/careers/job/7529880?gh_jid=7529880 | Marketing Manager, Italy and Turkey | marketing_specialist | family=marketing | loc=hybrid | salary=False | skills=True | other=False
  - https://www.suki.ai/open-positions?gh_jid=7644217003 | Product Marketing Manager (Partners) | marketing_specialist | family=marketing | loc=None | salary=True | skills=True | other=False
  - https://www.suki.ai/open-positions?gh_jid=7629151003 | Events Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=True | other=False
  - https://www.storyblok.com/job?gh_jid=4791291101 | Technical Product Marketing Manager - UK | marketing_specialist | family=marketing | loc=remote | salary=False | skills=False | other=False
  - https://www.storyblok.com/job?gh_jid=4791261101 | Technical Product Marketing Manager - USA | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False

### account_executive
- quality: **strong**
- results_count: 3152
- filters: `{'normalized_title': 'account_executive', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7728365 | Account Executive, Product Sales - Capital | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7724828 | National Account Executive, Enterprise (India) | account_executive | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7693271 | Enterprise Account Executive | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7686224 | Account Executive - Funded Startups - French | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7675661 | Account Executive, Product - BNPLs | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7577015 | Account Executive, Platforms (Grower) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7576967 | Account Executive, Platforms (Existing Business) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7555127 | Account Executive, SMB - Existing Business (French-speaking) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7553751 | Account Executive, Existing Business, Iberia | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7546284 | Account Executive, AI Sales | account_executive | family=sales | loc=None | salary=False | skills=False | other=False

### account_manager
- quality: **strong**
- results_count: 1814
- filters: `{'normalized_title': 'account_manager', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7650073 | Technical Account Manager, Bridge | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7594376 | Technical Account Manager, German OR Polish Speaking | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7564690 | Technical Account Manager, Risk | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7549012 | Technical Account Manager | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7545600 | Account Manager - Scale, Bridge | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7528441 | Technical Account Manager (Greater China) | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7524334 | Business Development Manager, Agentic Commerce | account_manager | family=sales | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7366283 | Technical Account Manager, Terminal | account_manager | family=sales | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7204777 | Technical Account Manager, Spanish Speaking | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7076173 | Technical Account Manager, German Speaking | account_manager | family=sales | loc=None | salary=False | skills=True | other=False

### remote_jobs
- quality: **strong**
- results_count: 22186
- filters: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': 'remote', 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://job-boards.greenhouse.io/recordedfuture/jobs/8482248002 | Senior Product Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7751786 | Talent Brand Experience Manager | other | family=other | loc=remote | salary=False | skills=False | other=True
  - https://stripe.com/jobs/search?gh_jid=7743309 | Design Recruiter (Fixed Term) | technical_recruiter | family=recruiting | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7743307 | Frontend Platform Engineer, JavaScript Infrastructure | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7737241 | Backend / API Engineer, Billing | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733216 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7723989 | Internal Recruiting Coordinator | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7722938 | Credit Operations Analyst | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7716032 | Staff Engineer - Production Eng | other | family=other | loc=remote | salary=False | skills=True | other=True

### jobs_with_salary
- quality: **strong**
- results_count: 37867
- filters: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': True, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati: nessuno critico nel sample
- sample rows (10):
  - https://job-boards.greenhouse.io/recordedfuture/jobs/8482248002 | Senior Product Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/redcellpartners/jobs/5085420007 | Staff Developer Experience Engineer | other | family=other | loc=None | salary=True | skills=False | other=True
  - https://job-boards.greenhouse.io/outschool/jobs/4607423006 | Software Engineer | software_engineer | family=software_engineering | loc=hybrid | salary=True | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7653060 | Solutions Architect, Commercial | solutions_architect | family=architecture | loc=onsite | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/zscaler/jobs/5058765007 | Director, Strategic Alliances-AI Ecosystem | other | family=other | loc=hybrid | salary=True | skills=True | other=True
  - https://www.esri.com/careers/5091856007?gh_jid=5091856007 | Accounts Receivable and Collections Representative | other | family=other | loc=onsite | salary=True | skills=True | other=True
  - https://www.epirusinc.com/open-roles?gh_jid=5836504004 | Accounting Manager | accountant | family=finance | loc=None | salary=True | skills=True | other=False
  - https://job-boards.greenhouse.io/webflow/jobs/7681033 | Staff Developer Relations Engineer | other | family=other | loc=remote | salary=True | skills=True | other=True
  - https://ensono.com/company/careers/jobs-board/?gh_jid=4560137005 | Senior Data Center Operator | other | family=other | loc=remote | salary=True | skills=True | other=True
  - https://job-boards.greenhouse.io/k2spacecorporation/jobs/5141978008 | Senior PCBA Rework Technician | other | family=other | loc=None | salary=True | skills=False | other=True

### jobs_with_python_skill
- quality: **noisy**
- results_count: 13660
- filters: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati:
  - Skill extraction può includere ruoli non tecnici o other con mention generiche.
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7736640 | Head of Connect & Crypto F&S | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7733216 | IT Support Engineer | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7729743 | Tech Ops Associate, New Grad (Mexico) | other | family=other | loc=onsite | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7716032 | Staff Engineer - Production Eng | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7714564 | Staff Engineer, Infrastructure | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7703909 | Solutions Architect, Start Ups and SMB (UKI) | solutions_architect | family=architecture | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7685855 | Technical Program Manager, Risk | technical_program_manager | family=program_management | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7678655 | Technical Program Manager, Risk | technical_program_manager | family=program_management | loc=None | salary=False | skills=True | other=False

### normalized_not_other
- quality: **usable**
- results_count: 34198
- filters: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': False, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati:
  - Ampia copertura ma mescola famiglie diverse; richiede filtri aggiuntivi di prodotto.
- sample rows (10):
  - https://job-boards.greenhouse.io/recordedfuture/jobs/8482248002 | Senior Product Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=False | other=False
  - https://job-boards.greenhouse.io/outschool/jobs/4607423006 | Software Engineer | software_engineer | family=software_engineering | loc=hybrid | salary=True | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7749540 | Technical Program Manager, Extensibility Programs | technical_program_manager | family=program_management | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7747640 | Forward Deployed AI Accelerator, Marketing | marketing_specialist | family=marketing | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7747638 | Forward Deployed AI Accelerator, Marketing | marketing_specialist | family=marketing | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7747636 | Forward Deployed AI Accelerator, Marketing | marketing_specialist | family=marketing | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7746721 | Senior Staff Frontend Engineer, Merchant Experience | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7743309 | Design Recruiter (Fixed Term) | technical_recruiter | family=recruiting | loc=remote | salary=False | skills=True | other=False
  - https://stripe.com/jobs/search?gh_jid=7741833 | Contracting Operations Specialist | operations_specialist | family=operations | loc=None | salary=False | skills=False | other=False
  - https://stripe.com/jobs/search?gh_jid=7737239 | Full Stack Engineer, Billing | software_engineer | family=software_engineering | loc=None | salary=False | skills=False | other=False

### other_with_skills
- quality: **noisy**
- results_count: 21265
- filters: `{'normalized_title': 'other', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati:
  - Query utile per discovery ma alta eterogeneità semantica.
- sample rows (10):
  - https://stripe.com/jobs/search?gh_jid=7748617 | Bridge Operations Associate | other | family=other | loc=onsite | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7743307 | Frontend Platform Engineer, JavaScript Infrastructure | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7738241 | Verifications Operations Associate | other | family=other | loc=onsite | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7737243 | Engineer Manager, Billing | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7737241 | Backend / API Engineer, Billing | other | family=other | loc=remote | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7737237 | Backend / API Engineer, Billing | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7736640 | Head of Connect & Crypto F&S | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7736171 | SDK Engineer (React/React Native), Privy | other | family=other | loc=None | salary=False | skills=True | other=True
  - https://stripe.com/jobs/search?gh_jid=7735676 | Sales Manager - SMB | other | family=other | loc=None | salary=False | skills=True | other=True

### healthcare_clinical
- quality: **usable**
- results_count: 2104
- filters: `{'normalized_title': None, 'role_family': 'healthcare_clinical', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati:
  - Buona precisione su label coperte, ma cluster clinico residuale resta in other.
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

### skilled_trades
- quality: **usable**
- results_count: 713
- filters: `{'normalized_title': None, 'role_family': 'skilled_trades', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 10}`
- problemi osservati:
  - Pack utile ma ancora incompleto su varianti domain-specific.
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

## Field Assessment
- campi più utili oggi:
  - normalized_title
  - role_family
  - location_type
  - has_salary
  - title_is_other
- campi più deboli:
  - skills (precision variabile)
  - employment_type (coverage parziale)
  - published_at/updated_at (qualità dipende dalla source)

## Miglioramenti ROI Alto
- Migliorare precisione skills extraction (ridurre falsi positivi su query skill-based).
- Aumentare coverage title su cluster ad alto volume residuale per ridurre other con skill utili.
- Aggiungere facet/filter combinati predefiniti di prodotto (title+family+location+salary).

## Cosa Non Conviene Fare Ancora
- Semantic search prima di stabilizzare ulteriormente quality dei segnali strutturati.
- Ranking avanzato senza ground-truth click/relevance.
- Espansione taxonomy massiva non cluster-driven.

## Summary
- strong: ['data_engineer', 'software_engineer', 'account_executive', 'account_manager', 'remote_jobs', 'jobs_with_salary']
- usable: ['marketing', 'normalized_not_other', 'healthcare_clinical', 'skilled_trades']
- noisy: ['jobs_with_python_skill', 'other_with_skills']
- weak: []
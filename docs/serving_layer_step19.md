# Serving Layer Step 19

Input: `data/jobs/jobs_indexed_en.jsonl`

## Supported Operations
- `list_jobs(filters..., limit, offset)`
- `count_jobs(filters...)`
- `run_pack(pack_name, limit, offset)`
- `count_pack(pack_name)`

## Supported Filters
- `normalized_title`
- `role_family`
- `language_bucket`
- `location_type`
- `employment_type`
- `has_salary`
- `has_skills`
- `title_is_other`
- `skills_contains`
- `salary_currency`

## Pagination
- params: `['limit', 'offset']`
- default_limit: 20
- default_offset: 0
- behavior: offset applied before limit on sorted matches

## Available Query Packs
- `account_executive_jobs`
- `healthcare_clinical_jobs`
- `high_confidence_tech_jobs`
- `marketing_jobs_with_salary`
- `other_with_strong_signals`
- `python_tech_jobs`
- `remote_data_jobs`
- `skilled_trades_jobs`

## Examples
- `jobintel-next serve query --input data/jobs/jobs_indexed_en.jsonl --normalized-title account_executive --limit 20 --offset 0`
- `jobintel-next serve count --input data/jobs/jobs_indexed_en.jsonl --role-family marketing --has-salary true`
- `jobintel-next serve pack --input data/jobs/jobs_indexed_en.jsonl --pack high_confidence_tech_jobs --limit 20 --offset 0`
- `jobintel-next serve pack-count --input data/jobs/jobs_indexed_en.jsonl --pack python_tech_jobs`

## Sample Results
### list_account_executive
- type: `list_jobs`
- query: `{'normalized_title': 'account_executive', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': None}`
- total_count: 3152
- returned_count: 5
- count_api: 3152
- https://stripe.com/jobs/search?gh_jid=7728365 | Account Executive, Product Sales - Capital | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
- https://stripe.com/jobs/search?gh_jid=7724828 | National Account Executive, Enterprise (India) | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
- https://stripe.com/jobs/search?gh_jid=7693271 | Enterprise Account Executive | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
- https://stripe.com/jobs/search?gh_jid=7686224 | Account Executive - Funded Startups - French | account_executive | family=sales | loc=None | salary=False | skills=False | other=False
- https://stripe.com/jobs/search?gh_jid=7675661 | Account Executive, Product - BNPLs | account_executive | family=sales | loc=None | salary=False | skills=False | other=False

### list_marketing_with_salary_offset_5
- type: `list_jobs`
- query: `{'normalized_title': None, 'role_family': 'marketing', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': True, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'updated_at_desc', 'limit': None}`
- total_count: 1584
- returned_count: 5
- count_api: 1584
- https://www.sphereentertainmentco.com/job/5082454007?gh_jid=5082454007 | Director, B2B Marketing & Events | marketing_specialist | family=marketing | loc=onsite | salary=True | skills=False | other=False
- https://www.sphereentertainmentco.com/job/5005813007?gh_jid=5005813007 | Lifecycle Marketing Manager | marketing_specialist | family=marketing | loc=onsite | salary=True | skills=True | other=False
- https://www.sentinelone.com/jobs/7552112003?gh_jid=7552112003 | Senior Service Provider Partner Marketing Manager | marketing_specialist | family=marketing | loc=remote | salary=True | skills=True | other=False
- https://www.seekout.com/company/careers/roles?gh_jid=7672729003 | Senior Product Marketing Manager | marketing_specialist | family=marketing | loc=onsite | salary=True | skills=True | other=False
- https://www.samsara.com/company/careers/roles/7743897?gh_jid=7743897 | Director, ABM & Field Marketing | marketing_specialist | family=marketing | loc=hybrid | salary=True | skills=False | other=False

### pack_high_confidence_tech_jobs
- type: `run_pack`
- pack_name: `high_confidence_tech_jobs`
- total_count: 8677
- returned_count: 5
- count_api: 8677
- https://job-boards.greenhouse.io/outschool/jobs/4607423006 | Software Engineer | software_engineer | family=software_engineering | loc=hybrid | salary=True | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7746721 | Senior Staff Frontend Engineer, Merchant Experience | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7705412 | Staff Software Engineer, Terminal Developer Productivity | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7671038 | Forward Deployed Engineer, Professional Services | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7656562 | Frontend Engineer, Privy | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False

### pack_python_tech_jobs_offset_5
- type: `run_pack`
- pack_name: `python_tech_jobs`
- total_count: 6049
- returned_count: 5
- count_api: 6049
- https://stripe.com/jobs/search?gh_jid=7610132 | Data Analyst | data_analyst | family=data_analytics | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7600792 | Software Engineer, Experimental Projects | software_engineer | family=software_engineering | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7594376 | Technical Account Manager, German OR Polish Speaking | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7564690 | Technical Account Manager, Risk | account_manager | family=sales | loc=None | salary=False | skills=True | other=False
- https://stripe.com/jobs/search?gh_jid=7549012 | Technical Account Manager | account_manager | family=sales | loc=None | salary=False | skills=True | other=False

## Known Limits
- Local JSONL scan in memory; no DB index in step19.
- No ranking, semantic search, or recommendation.
- Quality depends on upstream structured signals.
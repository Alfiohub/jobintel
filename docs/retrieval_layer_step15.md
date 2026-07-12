# Retrieval Layer Step 15

Input: `data/jobs/jobs_indexed_en.jsonl`

## Supported Filters
- normalized_title
- role_family
- language_bucket
- location_type
- employment_type
- has_salary
- has_skills
- title_is_other
- skills_contains
- salary_currency

## Supported Sorting
- published_at_desc
- updated_at_desc
- url

## Examples
- `jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --normalized-title data_engineer --has-salary true --sort-by published_at_desc --limit 20`
- `jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --role-family marketing --sort-by updated_at_desc --limit 20`
- `jobintel-next retrieval query --input data/jobs/jobs_indexed_en.jsonl --skills-contains python --has-skills true --limit 20`

## Sample Query Results
### data_engineer_with_salary
- matched_rows: 5
- query: `{'normalized_title': 'data_engineer', 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': True, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 5}`
- https://boards.greenhouse.io/accenturefederalservices/jobs/4607396006?gh_jid=4607396006 | Data Engineer/Architect | data_engineer | family=data_engineering | lang=en | salary=True | skills=True | other=False
- https://boards.greenhouse.io/spacex/jobs/8391768002?gh_jid=8391768002 | Data Engineer (Direct To Cell) | data_engineer | family=data_engineering | lang=en | salary=True | skills=True | other=False
- https://boards.greenhouse.io/spacex/jobs/8379395002?gh_jid=8379395002 | Sr. Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | lang=en | salary=True | skills=True | other=False
- https://boards.greenhouse.io/spacex/jobs/8379386002?gh_jid=8379386002 | Sr. Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | lang=en | salary=True | skills=True | other=False
- https://boards.greenhouse.io/spacex/jobs/8243150002?gh_jid=8243150002 | Data Engineer (Starlink Growth) | data_engineer | family=data_engineering | lang=en | salary=True | skills=True | other=False

### marketing_role_family
- matched_rows: 5
- query: `{'normalized_title': None, 'role_family': 'marketing', 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'updated_at_desc', 'limit': 5}`
- https://www.talkspace.com/careers/job?gh_jid=5831759004 | Marketing Ops Engineer Intern | marketing_specialist | family=marketing | lang=en | salary=False | skills=True | other=False
- https://www.talkspace.com/careers/job?gh_jid=5831378004 | Marketing Design Intern | marketing_specialist | family=marketing | lang=en | salary=False | skills=False | other=False
- https://www.taboola.com/careers/job/7722945?gh_jid=7722945 | Marketing Coordinator | marketing_specialist | family=marketing | lang=en | salary=False | skills=True | other=False
- https://www.taboola.com/careers/job/7713805?gh_jid=7713805 | Marketing Manager - Taiwan / Hong Kong | marketing_specialist | family=marketing | lang=en | salary=False | skills=True | other=False
- https://www.taboola.com/careers/job/7550360?gh_jid=7550360 | Marketing Manager, China | marketing_specialist | family=marketing | lang=en | salary=False | skills=False | other=False

### other_titles_with_skills
- matched_rows: 5
- query: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': True, 'title_is_other': True, 'skills_contains': [], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 5}`
- https://stripe.com/jobs/search?gh_jid=7748617 | Bridge Operations Associate | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7743307 | Frontend Platform Engineer, JavaScript Infrastructure | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7738241 | Verifications Operations Associate | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7737243 | Engineer Manager, Billing | other | family=other | lang=en | salary=False | skills=True | other=True

### python_skill
- matched_rows: 5
- query: `{'normalized_title': None, 'role_family': None, 'language_bucket': None, 'location_type': None, 'employment_type': None, 'has_salary': None, 'has_skills': None, 'title_is_other': None, 'skills_contains': ['python'], 'salary_currency': None, 'sort_by': 'published_at_desc', 'limit': 5}`
- https://stripe.com/jobs/search?gh_jid=7743311 | Data Writer and Editor | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7736640 | Head of Connect & Crypto F&S | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7733233 | IT Support Engineer | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7733216 | IT Support Engineer | other | family=other | lang=en | salary=False | skills=True | other=True
- https://stripe.com/jobs/search?gh_jid=7729743 | Tech Ops Associate, New Grad (Mexico) | other | family=other | lang=en | salary=False | skills=True | other=True

## Known Limits
- In-memory JSONL scan; no DB index in v1.
- Only exact-match filters (except skills_contains over normalized skill tokens).
- No ranking, semantic search, or recommendation in this step.
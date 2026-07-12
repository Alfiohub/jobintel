# Extraction Stage Step 9

Input: `data/jobs/jobs_cleaned_en.jsonl`
Output: `data/jobs/jobs_extracted_en.jsonl`

## Counts
- rows_total: 81011
- invalid_rows: 0

## Field Fill Rates
- seniority: 64542 (79.67%)
- employment_type: 29319 (36.19%)
- location_type: 49816 (61.49%)
- salary: 37867 (46.74%)
- salary_currency: 37867 (46.74%)
- salary_period: 10581 (13.06%)
- skills: 32894 (40.6%)

## Sample Extracted Rows
- https://job-boards.greenhouse.io/found/jobs/4652575005 | seniority=director | employment_type=None | location_type=remote | salary=(None,None,None,None) | skills=['python', 'sql', 'dbt', 'tableau']
- https://job-boards.greenhouse.io/found/jobs/4665181005 | seniority=manager | employment_type=None | location_type=remote | salary=(None,None,None,None) | skills=[]
- https://job-boards.greenhouse.io/found/jobs/4668478005 | seniority=manager | employment_type=contract | location_type=hybrid | salary=(None,None,None,None) | skills=[]
- https://job-boards.greenhouse.io/found/jobs/4668477005 | seniority=manager | employment_type=None | location_type=remote | salary=(None,None,None,None) | skills=[]
- https://job-boards.greenhouse.io/found/jobs/4501664005 | seniority=None | employment_type=contract | location_type=remote | salary=(140,180,USD,hour) | skills=[]

## Known Limits
- Regex/rules approach only; no heavy NLP.
- Salary extraction supports common base patterns only.
- Skills list is intentionally small in this stage.
# Search Benchmark Results v1 (Manual Relevance)

- source csv: `docs/semantic_eval_top3_prefilled.csv`
- queries: `20`
- judged depth: `top-3`

## Aggregate Metrics

| Provider | Precision@3 | Hit@3 | MRR@3 |
|---|---:|---:|---:|
| hash | 0.067 | 0.200 | 0.092 |
| openai | 0.550 | 0.750 | 0.675 |

- wins: `openai=14` `hash=0` `tie=6`

## Query Breakdown

| Query | Hash P@3 | OpenAI P@3 | Hash MRR@3 | OpenAI MRR@3 | Winner |
|---|---:|---:|---:|---:|---|
| senior data engineer remote | 0.333 | 1.000 | 0.500 | 1.000 | openai |
| python airflow dbt | 0.000 | 1.000 | 0.000 | 1.000 | openai |
| analytics director healthcare | 0.000 | 0.667 | 0.000 | 1.000 | openai |
| business analyst retail energy | 0.000 | 0.667 | 0.000 | 1.000 | openai |
| staff machine learning scientist | 0.000 | 1.000 | 0.000 | 1.000 | openai |
| solutions architect cloud | 0.000 | 0.000 | 0.000 | 0.000 | tie |
| enterprise account executive saas | 0.333 | 1.000 | 0.500 | 1.000 | openai |
| customer success manager | 0.000 | 1.000 | 0.000 | 1.000 | openai |
| technical recruiter contract | 0.000 | 0.000 | 0.000 | 0.000 | tie |
| product manager platform | 0.000 | 0.333 | 0.000 | 1.000 | openai |
| frontend react typescript | 0.000 | 0.000 | 0.000 | 0.000 | tie |
| devops kubernetes terraform | 0.000 | 0.667 | 0.000 | 1.000 | openai |
| data analyst tableau sql | 0.000 | 0.667 | 0.000 | 0.500 | openai |
| bi analyst power bi | 0.000 | 0.000 | 0.000 | 0.000 | tie |
| head of engineering | 0.333 | 1.000 | 0.333 | 1.000 | openai |
| hr business partner | 0.000 | 0.667 | 0.000 | 1.000 | openai |
| implementation consultant | 0.000 | 0.667 | 0.000 | 1.000 | openai |
| field cto | 0.000 | 0.333 | 0.000 | 0.500 | openai |
| ml engineer llm | 0.000 | 0.000 | 0.000 | 0.000 | tie |
| sales development representative | 0.333 | 0.333 | 0.500 | 0.500 | tie |

## Notes

- `Top-10` relevance is not included in this report because the current manual eval set is top-3 only.
- Next step: add a `top-10` judged CSV and extend this report with `P@10` and `MRR@10`.

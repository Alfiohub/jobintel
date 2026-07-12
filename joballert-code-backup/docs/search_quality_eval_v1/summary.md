# Search Quality Eval v1

- db: `data/jobintel_microsaas_taxonomy_v1_final_2k_20260326_r3.sqlite`
- queries: `docs/search_quality_queries_v1.json`
- query count: `10`
- top-k: `5`
- relevant threshold: `0.75`

## Aggregate

- overall_avg_coherence: `0.935`
- overall_hit_rate: `1.0`

## Per Query

| query_id | avg_coherence@5 | hit@5 | relevant@5 | returned_count |
|---|---:|---:|---:|---:|
| q1_sw_us_remote_skills | 1.0 | 1 | 5 | 30 |
| q2_data_us_remote | 1.0 | 1 | 5 | 13 |
| q3_customer_success_us | 1.0 | 1 | 5 | 7 |
| q4_product_remote | 1.0 | 1 | 5 | 18 |
| q5_marketing_remote | 1.0 | 1 | 5 | 30 |
| q6_finance_us | 1.0 | 1 | 5 | 13 |
| q7_partnerships | 1.0 | 1 | 5 | 24 |
| q8_program_management | 1.0 | 1 | 5 | 30 |
| q9_us_remote_python_sql | 0.87 | 1 | 4 | 30 |
| q10_gb_general | 0.48 | 1 | 1 | 30 |

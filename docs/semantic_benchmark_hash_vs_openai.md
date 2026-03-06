# Semantic Benchmark: Hash vs OpenAI (Common Corpus)

- hash DB: `data/jobintel_microsaas.sqlite`
- openai DB: `data/jobintel_microsaas_openai.sqlite`
- openai model: `text-embedding-3-small`
- top-k: `10`
- common URLs compared: `200`

| Query | Overlap@k | Hash Top-1 | OpenAI Top-1 |
|---|---:|---|---|
| senior data engineer remote | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7630792 | https://job-boards.greenhouse.io/smartsheet/jobs/7435911 |
| python airflow dbt | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7475545 | https://job-boards.greenhouse.io/gomotive/jobs/8213266002 |
| analytics director healthcare | 1/10 | https://job-boards.greenhouse.io/gomotive/jobs/8381121002 | https://job-boards.greenhouse.io/omadahealth/jobs/7351285 |
| business analyst retail energy | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7435911 | https://job-boards.greenhouse.io/gomotive/jobs/8307807002 |
| staff machine learning scientist | 0/10 | https://job-boards.greenhouse.io/gomotive/jobs/7812320002 | https://job-boards.greenhouse.io/smartsheet/jobs/7577295 |
| solutions architect cloud | 2/10 | https://job-boards.greenhouse.io/gomotive/jobs/8235635002 | https://job-boards.greenhouse.io/smartsheet/jobs/7395033 |
| enterprise account executive saas | 2/10 | https://job-boards.greenhouse.io/gomotive/jobs/8402712002 | https://job-boards.greenhouse.io/gomotive/jobs/8367411002 |
| customer success manager | 1/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7395033 | https://job-boards.greenhouse.io/gomotive/jobs/8129164002 |
| technical recruiter contract | 0/10 | https://job-boards.greenhouse.io/gomotive/jobs/7812270002 | https://job-boards.greenhouse.io/smartsheet/jobs/7648752 |
| product manager platform | 1/10 | https://job-boards.greenhouse.io/smartsheet/jobs/6718388 | https://job-boards.greenhouse.io/smartsheet/jobs/7651508 |
| frontend react typescript | 1/10 | https://job-boards.greenhouse.io/gomotive/jobs/7213840002 | https://job-boards.greenhouse.io/gomotive/jobs/8209651002 |
| devops kubernetes terraform | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7571627 | https://job-boards.greenhouse.io/smartsheet/jobs/7385653 |
| data analyst tableau sql | 1/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7386364 | https://job-boards.greenhouse.io/smartsheet/jobs/7395033 |
| bi analyst power bi | 0/10 | https://job-boards.greenhouse.io/omadahealth/jobs/7402427 | https://job-boards.greenhouse.io/smartsheet/jobs/7395033 |
| head of engineering | 1/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7594178 | https://job-boards.greenhouse.io/gomotive/jobs/8209651002 |
| hr business partner | 1/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7578148 | https://job-boards.greenhouse.io/gomotive/jobs/8329430002 |
| implementation consultant | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7599444 | https://job-boards.greenhouse.io/gomotive/jobs/8379119002 |
| field cto | 0/10 | https://job-boards.greenhouse.io/gomotive/jobs/7761424002 | https://job-boards.greenhouse.io/gomotive/jobs/8384761002 |
| ml engineer llm | 2/10 | https://job-boards.greenhouse.io/gomotive/jobs/8324209002 | https://job-boards.greenhouse.io/gomotive/jobs/8209651002 |
| sales development representative | 0/10 | https://job-boards.greenhouse.io/smartsheet/jobs/7364595 | https://job-boards.greenhouse.io/gomotive/jobs/8367923002 |

- Avg overlap@10: `0.065`

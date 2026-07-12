# Language Eval Step 6

Input: `data/all_greenhouse_jobs_from_targets.jsonl`

## Counts
- rows_total: 84487
- invalid_rows: 0
- rows_en: 81011 (95.89%)
- rows_non_en: 3118 (3.69%)
- rows_unknown: 358 (0.42%)

## Sample Files
- en: `docs/sample_en.jsonl`
- non_en: `docs/sample_non_en.jsonl`
- unknown: `docs/sample_unknown.jsonl`

## Top Reasons (en)
- hint_detector_agree: 80709
- detector_primary: 155
- hint_detector_disagree_detector_override: 94
- text_stopwords_en: 53

## Top Titles (en)
- Psychiatric Mental Health Nurse Practitioner (PMHNP): 381
- Psychiatrist (MD): 324
- Senior Software Engineer: 285
- CDL Drivers: 279
- Future Technicians: 279
- Territory Account Managers: 273
- Senior Data Engineer: 224
- Sales Development Representative: 204
- Account Executive: 202
- Psychotherapist: 177

## Top Reasons (non_en)
- hint_detector_agree: 2739
- hint_detector_disagree_detector_override: 375
- detector_primary: 4

## Top Titles (non_en)
- Business Development Executive - Außendienst (w/m/d): 11
- (Senior) Consultant* - Payments: 7
- Brand Ambassador (Evenementen): 6
- Consulting Manager – Strategy & Transformation: 6
- Psychologe (m/w/d): 6
- Psychologische Berater:in (m/w/d): 6
- Lohn- und Gehaltsabrechner (m/w/d) - Remote: 5
- Senior Account Executive - Praxissoftware (x/f/m): 5
- Brand Ambassador (Events): 5
- Account Manager DACH (all genders): 5

## Top Reasons (unknown)
- low_signal_mixed_or_ambiguous: 175
- hint_without_text_support: 166
- hint_without_enough_text: 16
- text_too_short_or_ambiguous: 1

## Top Titles (unknown)
- Senior Android Engineer (Eats Customer): 2
- Staff Database Engineer (DBA): 2
- インサイドセールス/ Sales Development Representative: 1
- Account Operations Intern - Beijing: 1
- Sales Manager(IC, Hunter), Ad Cloud: 1
- 社内ITヘルプデスク/IT Support Specialist (Part-time, Japanese & Mandarin) – Tokyo: 1
- BA / PM Reg Reporting: 1
- Assistance Required: 1
- [쿠팡] 이츠 광고 세일즈 전략 및 운영 팀장 (경력): 1
- [쿠팡] 세무 전문가 (부가가치세 담당): 1

## Diagnostics
- No obvious global imbalance detected from bucket ratios.

## Examples
### en
- title: Data Analytics Director
- reason: hint_detector_agree
- url: https://job-boards.greenhouse.io/found/jobs/4652575005

### non_en
- title: Représentant du Développement des Ventes
- reason: hint_detector_disagree_detector_override
- url: https://job-boards.greenhouse.io/canonical/jobs/5906505

### unknown
- title: インサイドセールス/ Sales Development Representative
- reason: hint_without_text_support
- url: https://job-boards.greenhouse.io/canonical/jobs/5906570
